import os
import subprocess
import random
import string
import weechat_relay

from charmhelpers.core import hookenv, templating, unitdata
from OpenSSL import crypto


class WeechatHelper():
    def __init__(self):
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
        self.relay_cert_file = self.relay_cert_folder + '/relay.pem'
        self.kv = unitdata.kv()
        self.relay_password = self.kv.get('relay-password')

    def gen_passwd(self):
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        size = random.randint(8, 12)
        return ''.join(random.choice(chars) for x in range(size))

    def install_mnt_script(self):
        templating.render('mountencfs.sh',
                          self.mount_file,
                          context={'unit': hookenv.local_unit()})

    def install_enc_mount(self):
        self.install_mnt_script()
        templating.render('home-weechat-.weechat.mount',
                          self.enc_unit_file,
                          context={'unit': hookenv.local_unit()})

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
