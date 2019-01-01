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
        weechat.weechat_command('/relay test')
        with open(weechat.fifo_file, 'r') as fifo:
            contents = fifo.read()
            assert '*/relay test' in contents

    def test_enable_relay(self, weechat):
        weechat.enable_relay()
        with open(weechat.fifo_file, 'r') as fifo:
            contents = fifo.read()
            assert '*/relay add ssl.weechat 9001' in contents
