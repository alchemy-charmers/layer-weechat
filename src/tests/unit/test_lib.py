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
            assert 'ExecStart=/usr/bin/screen -d -m -S weechat /usr/bin/weechat' in content
