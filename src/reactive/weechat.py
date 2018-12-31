from lib_weechat import WeechatHelper
from charmhelpers.core import hookenv, host
from charms.reactive import set_flag, when, when_not

helper = WeechatHelper()


@when_not('weechat.installed')
@when('apt.installed.weechat-curses')
def install_weechat():
    host.adduser('weechat')
    hookenv.status_set('active', '')
    set_flag('weechat.installed')
