"""Helper library for Weechat reactive charm."""
import os
import subprocess
import random
import shutil
import string
import weechat_relay

from charmhelpers.core import (
    hookenv,
    templating,
    unitdata,
    host
)
from charmhelpers import fetch
from OpenSSL import crypto


class WeechatHelper():
    """Helper for installing and configuring WeeChat."""

    def __init__(self):
        """Set instance variables based on charm configuration."""
        self.charm_config = hookenv.config()
        self.encfs_password = self.charm_config['encfs-password']
        self.charm_config['encfs-password'] = 'not-the-password'
        self.weechat_folder = "/home/weechat/.weechat"
        self.encweechat_folder = "/home/weechat/.encweechat"
        self.service_file = '/lib/systemd/system/weechat.service'
        self.mount_file = '/root/mountencfs.sh'
        self.enc_unit_file = '/lib/systemd/system/home-weechat-.weechat.mount'
        self.fifo_file = '/home/weechat/.weechat/weechat_fifo'
        self.relay_cert_folder = '/home/weechat/.weechat/ssl'
        self.python_plugin_dir = '/home/weechat/.weechat/python'
        self.relay_cert_file = self.relay_cert_folder + '/relay.pem'
        self.kv = unitdata.kv()
        self.relay_password = self.kv.get('relay-password')

    def gen_passwd(self):
        """
        Generate random password.

        :rtype str
        :returns random password
        """
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        size = random.randint(8, 12)
        return ''.join(random.choice(chars) for x in range(size))

    def install_mnt_script(self):
        """Install script for mounting encfs prior to starting WeeChat."""
        templating.render('mountencfs.sh',
                          self.mount_file,
                          context={'unit': hookenv.local_unit()})

    def install_enc_mount(self):
        """Install systemd mount unit for mounting encfs prior to starting WeeChat"""
        self.install_mnt_script()
        templating.render('home-weechat-.weechat.mount',
                          self.enc_unit_file,
                          context={'unit': hookenv.local_unit()})

    def install_py_script(self, uri, name):
        """Install a weechat addon script from an URI"""
        # ensure plugins dir and autoload dir exists
        for dirname in [
                self.python_plugin_dir,
                "{}/autoload".format(
                    self.python_plugin_dir)]:
            os.makedirs(dirname,
                        mode=0o700,
                        exist_ok=True)
        
        # checkout addon
        local_download = fetch.install_remote(uri)
        hookenv.log("Downloaded wee_slack to {}".format(
            local_download))
        if os.path.isfile("{}/wee-slack-master/wee_slack.py".format(local_download)):
            hookenv.log("Copying wee_slack from {}/wee-slack-master/ to {}".format(
                local_download,
                self.python_plugin_dir))
            shutil.copyfile(
                "{}/wee-slack-master/wee_slack.py".format(local_download),
                "{}/wee_slack.py".format(self.python_plugin_dir))

        # symlink into autoload
        hookenv.log("Symlinking wee_slack from {0} to {0}/autoload".format(
            self.python_plugin_dir))
        host.symlink(
            "{}/{}".format(
                self.python_plugin_dir,
                name),
            "{}/autoload/{}".format(
                self.python_plugin_dir,
                name))
        # check ownsership
        host.chownr(
            self.python_plugin_dir,
            'weechat',
            'weechat',
            follow_links=True,
            chowntopdir=True
        )

    def install_wee_slack(self):
        """Install wee_slack script for Slack features"""
        self.install_py_script(
            'https://github.com/wee-slack/wee-slack/archive/master.tar.gz',
            'wee_slack.py'
        )

    def install_systemd(self):
        templating.render('weechat.service',
                          self.service_file,
                          context={})

    def weechat_command(self, command):
        hookenv.log("Received weechat_command: {}".format(command))
        if not command:
            return 'Empty command'
        cmd = "*{}".format(command)
        hookenv.log("Calling fifo with: {}".format(cmd))
        result = subprocess.check_output('echo {} > {}'.format(cmd, self.fifo_file),
                                         shell=True)
        return result.decode()

    def generate_certificate(self):
        pkey = crypto.PKey()
        pkey.generate_key(crypto.TYPE_RSA, 2048)
        serial = random.getrandbits(64)
        cert = crypto.X509()
        cert.get_subject().CN = 'Weechat Relay'
        cert.set_serial_number(serial)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(pkey)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(157700000)
        cert.sign(pkey, 'sha512')
        os.makedirs(self.relay_cert_folder, exist_ok=True)
        with open(self.relay_cert_file, 'wb') as certfile:
            certfile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))
            certfile.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    def enable_relay(self):
        if not self.relay_password:
            if self.charm_config['relay-password']:
                self.kv.set('relay-password', self.charm_config['relay-password'])
                self.relay_password = self.charm_config['relay-password']
            else:
                password = self.gen_passwd()
                self.kv.set('relay-password', password)
                self.relay_password = password
        self.weechat_command('/relay sslcertkey')
        self.weechat_command('/set relay.network.password {}'.format(self.relay_password))
        self.weechat_command('/relay add ssl.weechat {}'.format(self.charm_config['relay-port']))
        self.weechat_command('/save')

    def ping_relay(self, hostname, port, secure=False):
        return weechat_relay.ping_relay(hostname, port, self.relay_password, secure)

    def apply_user_config(self):
        for line in self.charm_config['user-config'].strip().split('\n'):
            self.weechat_command(line)
        self.weechat_command('/save')
