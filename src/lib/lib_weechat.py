import os
import subprocess
import random
import struct
import ssl

from charmhelpers.core import hookenv, templating
from OpenSSL import crypto
from websocket import create_connection


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

    def decode_reply(self, reply):
        length, compression, idlen = struct.unpack('!I?I', reply[0:9])
        if idlen:
            index = 9 + idlen
            msgid = reply[9:index]
        else:
            index = 9
            msgid = b''
        typ = reply[index:index + 3]
        index += 3
        if typ == b'str':
            strlen = struct.unpack('!I', reply[index:index + 4])[0]
            index += 4
            obj = reply[index:index + strlen]
        else:
            hookenv.log("Type not implemented: {}".format(typ),
                        level=hookenv.WARNING)
            obj = "Type not implemented: {}".format(typ)
        return(msgid, obj)

    def ping_relay(self, hostname, port, secure=False):
        # b'\x00\x00\x00\x1a\x00\x00\x00\x00\x05_pongstr\x00\x00\x00\x05Hello'
        if secure:
            ws = create_connection("wss://{}:{}/weechat".format(hostname, port),
                                   sslopt={"cert_reqs": ssl.CERT_NONE})
        else:
            ws = create_connection("ws://{}:{}/weechat".format(hostname, port))
        ws.send('init password=changeme,compression=off\r\n')
        ws.send('ping Hello Weechat\r\n')
        result = None
        while not result:
            result = ws.recv()
        ws.close()
        msgid, obj = self.decode_reply(result)
        if msgid == b'_pong' and\
           obj == b'Hello Weechat':
            return True
        else:
            return False
