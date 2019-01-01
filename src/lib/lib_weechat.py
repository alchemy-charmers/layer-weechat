import os
import subprocess
import random

from charmhelpers.core import hookenv, templating
from OpenSSL import crypto
from pyweerelay import Relay


class WeechatHelper():
    def __init__(self):
        self.charm_config = hookenv.config()
        self.service_file = '/lib/systemd/system/weechat.service'
        self.fifo_file = '/home/weechat/.weechat/weechat_fifo'
        self.relay_cert_folder = '/home/weechat/.weechat/ssl'
        self.relay_cert_file = self.relay_cert_folder + '/relay.pem'

    def install_systemd(self):
        templating.render('weechat.service',
                          self.service_file,
                          context={})

    def weechat_command(self, command):
        cmd = "*{}".format(command)
        result = subprocess.check_output('echo {} > {}'.format(cmd, self.fifo_file),
                                         shell=True)
        return result.decode()

    def action_function(self):
        ''' An example function for calling from an action '''
        return

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
        self.weechat_command('/relay sslcertkey')
        self.weechat_command('/set relay.network.password changeme')
        self.weechat_command('/relay add ssl.weechat 9001')

    def ping_relay(self, hostname):
        with Relay(hostname, port=9001, password='changeme') as r:
            r.ping()
