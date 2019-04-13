#!/usr/bin/python3
import mock
import os
import pytest


# If layer options are used, add this to weechat
# and import layer in lib_weechat
@pytest.fixture
def mock_layers(monkeypatch):
    import sys
    sys.modules['charms.layer'] = mock.Mock()
    sys.modules['reactive'] = mock.Mock()
    # Mock any functions in layers that need to be mocked here

    def options(layer):
        # mock options for layers here
        if layer == 'example-layer':
            options = {'port': 9999}
            return options
        else:
            return None

    monkeypatch.setattr('lib_weechat.layer.options', options)


@pytest.fixture
def mock_hookenv_config(monkeypatch):
    import yaml

    def mock_config():
        cfg = {}
        yml = yaml.load(open('./config.yaml'))

        # Load all defaults
        for key, value in yml['options'].items():
            cfg[key] = value['default']
        cfg['enable-slack'] = True

        # Manually add cfg from other layers
        # cfg['my-other-layer'] = 'mock'
        return cfg

    monkeypatch.setattr('lib_weechat.hookenv.config', mock_config)


@pytest.fixture
def mock_hookenv_action(monkeypatch):
    monkeypatch.setattr('lib_weechat.hookenv.action_set', mock.Mock())
    monkeypatch.setattr('lib_weechat.hookenv.action_get', mock.Mock())


@pytest.fixture
def mock_remote_unit(monkeypatch):
    monkeypatch.setattr('lib_weechat.hookenv.remote_unit', lambda: 'unit-mock/0')


@pytest.fixture
def mock_charm_dir(monkeypatch):
    monkeypatch.setattr('lib_weechat.hookenv.charm_dir', lambda: '.')


@pytest.fixture
def mock_fchown(monkeypatch):
    monkeypatch.setattr('lib_weechat.templating.os.fchown', mock.Mock())


@pytest.fixture
def mock_install_remote(monkeypatch):

    def return_tmp_dir(uri):
        return '/tmp'

    mock_method = mock.Mock()
    mock_method.side_effect = return_tmp_dir
    monkeypatch.setattr('lib_weechat.fetch.install_remote',
                        mock_method)
    return mock_method


@pytest.fixture
def mock_makedirs(monkeypatch):
    mock_method = mock.Mock()
    monkeypatch.setattr('lib_weechat.os.makedirs',
                        mock_method)
    return mock_method


@pytest.fixture
def mock_chownr(monkeypatch):
    mock_method = mock.Mock()
    monkeypatch.setattr('lib_weechat.host.chownr',
                        mock_method)
    return mock_method


@pytest.fixture
def mock_isfile(monkeypatch):

    def return_true(filename):
        return True

    mock_method = mock.Mock()
    mock_method.side_effect = return_true
    monkeypatch.setattr('lib_weechat.os.path.isfile',
                        mock_method)
    return mock_method


@pytest.fixture
def mock_copyfile(monkeypatch):
    mock_method = mock.Mock()
    monkeypatch.setattr('lib_weechat.shutil.copyfile',
                        mock_method)
    return mock_method


@pytest.fixture
def mock_symlink(monkeypatch):
    mock_method = mock.Mock()
    monkeypatch.setattr('lib_weechat.host.symlink',
                        mock_method)
    return mock_method


@pytest.fixture
def mock_websocket(monkeypatch):
    mock_connection = mock.Mock()
    return_values = [b'\x00\x00\x00\x1a\x00\x00\x00\x00\x05_pongstr\x00\x00\x00\x0DHello Weechat',
                     b'\x00\x00\x00\x1a\x00\x00\x00\x00\x05_pongstr\x00\x00\x00\x05Hello']
    recv = mock.Mock(side_effect=return_values)
    mock_connection.recv = recv
    monkeypatch.setattr('weechat_relay.create_connection', lambda *x, **y: mock_connection)


@pytest.fixture
def weechat_relay(mock_websocket):
    import weechat_relay
    return weechat_relay


@pytest.fixture
def weechat(tmpdir, mock_hookenv_config, mock_charm_dir, monkeypatch,
            mock_fchown, mock_makedirs, mock_chownr, mock_isfile,
            mock_copyfile, mock_symlink, mock_websocket,
            mock_install_remote, mock_hookenv_action):
    from lib_weechat import WeechatHelper
    helper = WeechatHelper()

    # Example config file patching
    # cfg_file = tmpdir.join('example.cfg')
    # with open('./tests/unit/example.cfg', 'r') as src_file:
    #     cfg_file.write(src_file.read())
    # helper.example_config_file = cfg_file.strpath

    helper.service_file = tmpdir.join('weechat.service').strpath
    helper.fifo_file = tmpdir.strpath + '/fifo'
    os.mkfifo(helper.fifo_file, 0o777)
    helper.relay_cert_folder = tmpdir.strpath + "/ssl"
    helper.relay_cert_file = helper.relay_cert_folder + "/relay.pem"

    # Any other functions that load helper will get this version
    monkeypatch.setattr('lib_weechat.WeechatHelper', lambda: helper)

    return helper
