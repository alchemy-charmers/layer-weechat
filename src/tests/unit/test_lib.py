#!/usr/bin/python3


class TestLib():
    def test_pytest(self):
        assert True

    def test_weechat(self, weechat):
        ''' See if the helper fixture works to load charm configs '''
        assert isinstance(weechat.charm_config, dict)

    # Include tests for functions in lib_weechat
