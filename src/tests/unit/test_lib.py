#!/usr/bin/python3


class TestLib():
    def test_pytest(self):
        assert True

    def test_weechat(self, weechat):
        ''' See if the helper fixture works to load charm configs '''
        assert isinstance(weechat.charm_config, dict)

    def test_example_action(self, weechat):
        weechat.action_function()

    def test_install_systemd(self, weechat):
        weechat.install_systemd()
        with open(weechat.service_file, 'r') as service_file:
            content = service_file.read()
            assert 'ExecStart=/usr/bin/screen -D -m -S weechat /usr/bin/weechat' in content

    def test_generate_certificate(self, weechat):
        weechat.generate_certificate()
        with open(weechat.relay_cert_file, 'r') as cert_file:
            content = cert_file.read()
            assert '-----BEGIN PRIVATE KEY-----' in content
            assert '-----BEGIN CERTIFICATE-----' in content

    def test_weechat_command(self, weechat):
        weechat.weechat_command('/set relay test')
        with open(weechat.fifo_file, 'r') as fifo:
            contents = fifo.read()
            assert '*/set relay test' in contents
        result = weechat.weechat_command('')
        assert 'Empty command' in result

    def test_enable_relay(self, weechat):
        # Check enable and auto-generate password
        weechat.enable_relay()
        with open(weechat.fifo_file, 'r') as fifo:
            contents = fifo.read()
            assert '*/relay add ssl.weechat 9001' in contents

        # Check enable with pre-set password
        weechat.charm_config['relay-password'] = 'testpassword'
        weechat.relay_password = ''
        weechat.enable_relay()
        assert 'testpassword' == weechat.relay_password

    def test_ping_relay(self, weechat):
        # Pass / Fail is due to the mock chaning the return, not the parameters
        assert weechat.ping_relay('127.0.0.1', 443, secure=False)
        assert not weechat.ping_relay('127.0.0.1', 9001, secure=True)

    def test_apply_user_config(self, weechat):
        weechat.charm_config['user-config'] = '/set test command'
        weechat.apply_user_config()
        with open(weechat.fifo_file, 'r') as fifo:
            contents = fifo.read()
            assert '*/set test command' in contents
        weechat.charm_config['user-config'] = '''/set test command\r\n/set test command2'''
        weechat.apply_user_config()
        with open(weechat.fifo_file, 'r') as fifo:
            contents = fifo.read()
            assert '*/set test command' in contents
            assert '*/set test command2' in contents
