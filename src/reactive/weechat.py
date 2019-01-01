from lib_weechat import WeechatHelper
from charmhelpers.core import hookenv, host
from charms.reactive import set_flag, when, when_not, endpoint_from_name
from pathlib import Path

import socket
import subprocess
import time

helper = WeechatHelper()


@when_not('weechat.installed')
@when('apt.installed.weechat-curses')
def install_weechat():
    host.adduser('weechat', 'password')
    subprocess.check_call(['passwd', '-d', 'weechat'])
    helper.install_systemd()
    host.service('enable', 'weechat.service')
    host.service_start('weechat.service')
    timeout = 10
    while not Path(helper.fifo_file).exists():
        time.sleep(1)
        timeout -= 1
        if not timeout:
            hookenv.status_set('blocked', 'weechat.service failed to start')
            return
    set_flag('weechat.installed')


@when('weechat.installed')
@when_not('weechat.configured')
def configure_weechat():
    helper.generate_certificate()
    host.chownr(helper.relay_cert_folder, 'weechat', 'weechat', chowntopdir=True)
    helper.enable_relay()
    hookenv.status_set('active', '')
    set_flag('weechat.configured')


@when('reverseproxy.ready')
@when_not('reverseproxy.configured')
def configure_reverseproxy():
    interface = endpoint_from_name('reverseproxy')
    config = {
        'mode': 'http',
        'urlbase': '/weechat',
        'external_port': 443,
        'internal_host': socket.getfqdn(),
        'internal_port': 9001,
        'proxypass': True,
        'ssl': True,
        'ssl-verify': False,
    }
    interface.configure(config)
