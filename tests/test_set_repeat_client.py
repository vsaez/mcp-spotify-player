from mcp_spotify_player.spotify_client import SpotifyClient


def test_set_repeat_client():
    client = SpotifyClient()
    calls = []

    def fake_make_request(method, endpoint, **kwargs):
        calls.append({'method': method, 'endpoint': endpoint, 'params': kwargs.get('params')})
        return {}

    client._make_request = fake_make_request

    result = client.set_repeat('track')
    assert result is True
    assert calls[-1]['method'] == 'PUT'
    assert calls[-1]['endpoint'] == '/me/player/repeat'
    assert calls[-1]['params'] == {'state': 'track'}

    calls.clear()
    result = client.set_repeat('invalid')
    assert result is False
    assert calls == []
