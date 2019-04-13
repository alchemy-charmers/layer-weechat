import imp
import mock


def test_get_relay_password(weechat, monkeypatch):
    mock_kv = mock.Mock()
    monkeypatch.setattr(weechat, 'kv', mock_kv)
    mock_get = mock.PropertyMock()
    type(mock_kv).get = mock_get
    assert mock_get.call_count == 0
    imp.load_source('get_relay_password', './actions/get-relay-password')
    assert mock_get.call_count == 1


def test_update_weeslack(weechat, mock_install_remote,
                         mock_symlink, mock_chownr, mock_isfile,
                         mock_copyfile):
    imp.load_source('update_wee_slack', './actions/update-wee-slack')
    mock_install_remote.assert_called_once_with(
        'https://github.com/wee-slack/wee-slack/archive/master.tar.gz'
    )
    mock_isfile.assert_called_once_with(
        '/tmp/wee-slack-master/wee_slack.py'
    )
    mock_copyfile.assert_called_once_with(
        '/tmp/wee-slack-master/wee_slack.py',
        '/home/weechat/.weechat/python/wee_slack.py'
    )
    mock_symlink.assert_called_once_with(
        '/home/weechat/.weechat/python/wee_slack.py',
        '/home/weechat/.weechat/python/autoload/wee_slack.py'
    )
    mock_chownr.assert_called_once_with(
        weechat.python_plugin_dir,
        'weechat',
        'weechat',
        follow_links=True,
        chowntopdir=True
    )
