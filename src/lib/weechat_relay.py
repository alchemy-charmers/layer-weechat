import ssl
import struct

from websocket import create_connection


def decode_reply(reply):
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
        obj = "Type not implemented: {}".format(typ)
    return(msgid, obj)


def ping_relay(hostname, port, passwd, secure=False):
    # b'\x00\x00\x00\x1a\x00\x00\x00\x00\x05_pongstr\x00\x00\x00\x05Hello'
    if secure:
        ws = create_connection("wss://{}:{}/weechat".format(hostname, port),
                               sslopt={"cert_reqs": ssl.CERT_NONE})
    else:
        ws = create_connection("ws://{}:{}/weechat".format(hostname, port))
    ws.send('init password={},compression=off\r\n'.format(passwd))
    ws.send('ping Hello Weechat\r\n')
    result = None
    while not result:
        result = ws.recv()
    ws.close()
    msgid, obj = decode_reply(result)
    if msgid == b'_pong' and\
       obj == b'Hello Weechat':
        return True
    else:
        return False
