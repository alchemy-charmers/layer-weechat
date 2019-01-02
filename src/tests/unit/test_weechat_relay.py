class TestRelay():
    def test_decode_reply(self, weechat_relay):
        reply = b'\x00\x00\x00\x1a\x00\x00\x00\x00\x05_pongstr\x00\x00\x00\x05Hello'
        msgid, obj = weechat_relay.decode_reply(reply)
        assert msgid == b'_pong'
        assert obj == b'Hello'

        reply = b'\x00\x00\x00\x1a\x00\x00\x00\x00\x00buf\x00\x00\x00\x05Hello'
        msgid, obj = weechat_relay.decode_reply(reply)
        assert msgid == b''
        assert obj == "Type not implemented: b'buf'"
