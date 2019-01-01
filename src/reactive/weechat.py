from lib_weechat import WeechatHelper
from charmhelpers.core import hookenv, host
from charms.reactive import set_flag, when, when_not
import subprocess

helper = WeechatHelper()


@when_not('weechat.installed')
@when('apt.installed.weechat-curses')
def install_weechat():
    host.adduser('weechat', 'password')
    subprocess.check_call(['passwd', '-d', 'weechat'])
    helper.install_systemd()
    host.service('enable', 'weechat.service')
    host.service_start('weechat.service')
    set_flag('weechat.installed')


@when('weechat.installed')
@when_not('weechat.configured')
def configure_weechat():
    helper.generate_certificate()
    host.chownr(helper.relay_cert_folder, 'weechat', 'weechat', chowntopdir=True)
    helper.enable_relay()
    hookenv.status_set('active', '')
    set_flag('weechat.configured')