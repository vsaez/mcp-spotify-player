from src.playback_controller import PlaybackController


def test_get_devices_controller():
    class DummyPlayback:
        def get_devices(self):
            return {
                "devices": [
                    {
                        "id": "1",
                        "name": "Computer",
                        "type": "Computer",
                        "is_active": True,
                        "volume_percent": 50,
                    },
                    {
                        "id": "2",
                        "name": "Speaker",
                        "type": "Speaker",
                        "is_active": False,
                        "volume_percent": 100,
                    },
                ]
            }

    dummy_client = type("Dummy", (), {"playback": DummyPlayback(), "playlists": None})()
    controller = PlaybackController(dummy_client)

    result = controller.get_devices()
    assert result["success"] is True
    assert len(result["devices"]) == 2
    assert result["devices"][0]["name"] == "Computer"
    assert result["devices"][1]["is_active"] is False
