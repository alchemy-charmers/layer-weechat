from lib_weechat import WeechatHelper
from charmhelpers.core import hookenv, host
from charms.reactive import set_flag, when, when_not, endpoint_from_name
from pathlib import Path

import os
import socket
import subprocess
import time

helper = WeechatHelper()


def setup_encfs():
    try:
        os.mkdir(helper.weechat_folder, mode=0o700)
    except FileExistsError:
        pass  # Proceed if directory exists
    try:
        os.mkdir(helper.encweechat_folder, mode=0o700)
    except FileExistsError:
        pass  # Proceed if directory exists
    host.chownr(helper.encweechat_folder, 'weechat', 'weechat',
                chowntopdir=True)
    enc_pass = helper.encfs_password
    cmd = (f'echo "{enc_pass}" | encfs -S --standard --public'
           f' {helper.encweechat_folder} {helper.weechat_folder}')
    subprocess.check_call(cmd, shell=True)
    host.chownr(helper.weechat_folder, 'weechat', 'weechat',
                chowntopdir=True)
    helper.install_enc_mount()
    os.chmod(helper.mount_file, 0o700)
    host.service('enable', 'home-weechat-.weechat.mount')


@when_not('weechat.installed')
@when('apt.installed.weechat-curses')
def install_weechat():
    host.adduser('weechat', 'password')
    subprocess.check_call(['passwd', '-d', 'weechat'])
    if helper.charm_config['encfs-enabled']:
        setup_encfs()
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
    if helper.charm_config['enable-relay']:
        helper.enable_relay()
    hookenv.status_set('active', '')
    set_flag('weechat.configured')


@when('config.changed.user-config')
@when('weechat.configured')
def apply_user_config():
    helper.apply_user_config()


@when('reverseproxy.ready')
@when_not('reverseproxy.configured')
def configure_reverseproxy():
    interface = endpoint_from_name('reverseproxy')
    config = {
        'mode': 'http',
        'urlbase': '/weechat',
        'external_port': 443,
        'internal_host': socket.getfqdn(),
        'internal_port': helper.charm_config['relay-port'],
        'proxypass': True,
        'ssl': True,
        'ssl-verify': False,
    }
    interface.configure(config)
