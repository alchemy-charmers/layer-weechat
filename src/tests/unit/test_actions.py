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
