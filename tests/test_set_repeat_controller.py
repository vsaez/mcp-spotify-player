from src.playback_controller import PlaybackController


def test_set_repeat_controller():
    class DummyPlayback:
        def set_repeat(self, state):
            self.state = state
            return True

    dummy_client = type('Dummy', (), {'playback': DummyPlayback(), 'playlists': None})()
    controller = PlaybackController(dummy_client)

    result = controller.set_repeat('context')
    assert result['success'] is True
    assert 'context' in result['message']
