# Auto-generated MCP manifest
MANIFEST = {
    "schema_url": "https://json-schema.org/draft/2020-12/schema",
    "nameForHuman": "Spotify Player",
    "nameForModel": "spotify_player",
    "descriptionForHuman": "Control your Spotify music using natural commands",
    "descriptionForModel": "Tool for controlling music playback on Spotify. You can play songs, pause, skip, adjust volume, search for music, and more.",
    "auth": {
        "type": "oauth",
        "instructions": "You need to authenticate with Spotify to use this tool"
    },
    "tools": [
        {
            "name": "play_music",
            "description": "Play music on Spotify. You can specify a song, artist, playlist or simply resume playback.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Song or artist search (e.g., 'REM', 'Bohemian Rhapsody')"
                    },
                    "playlist_name": {
                        "type": "string",
                        "description": "Name of the playlist to play"
                    },
                    "track_uri": {
                        "type": "string",
                        "description": "Specific track URI"
                    },
                    "artist_uri": {
                        "type": "string",
                        "description": "Specific artist URI"
                    }
                }
            }
        },
        {
            "name": "pause_music",
            "description": "Pause the current music playback",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "skip_next",
            "description": "Skip to the next song in the playback queue",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "skip_previous",
            "description": "Skip to the previous song in the playback queue",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "set_volume",
            "description": "Set the playback volume (0-100%)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "volume_percent": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "Volume between 0 and 100"
                    }
                },
                "required": [
                    "volume_percent"
                ]
            }
        },
        {
            "name": "get_current_playing",
            "description": "Retrieve information about the currently playing song",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_playback_state",
            "description": "Retrieve the full playback state including device, volume, etc.",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "search_music",
            "description": "Search for music on Spotify by track, artist, or album",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term"
                    },
                    "search_type": {
                        "type": "string",
                        "enum": [
                            "track",
                            "artist",
                            "album"
                        ],
                        "default": "track",
                        "description": "Search type"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10,
                        "description": "Maximum number of results"
                    }
                },
                "required": [
                    "query"
                ]
            }
        },
        {
            "name": "get_playlists",
            "description": "Retrieve the user's playlists list",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_playlist_tracks",
            "description": "Retrieve tracks from a given playlist",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "playlist_id": {
                        "type": "string",
                        "description": "Playlist ID"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    }
                },
                "required": [
                    "playlist_id"
                ]
            }
        },
        {
            "name": "rename_playlist",
            "description": "Rename a Spotify playlist by its ID to a new name",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "playlist_id": {
                        "type": "string",
                        "description": "Spotify playlist ID"
                    },
                    "new_name": {
                        "type": "string",
                        "description": "New name for the playlist"
                    }
                },
                "required": [
                    "playlist_id",
                    "new_name"
                ]
            }
        },
        {
            "name": "clear_playlist",
            "description": "Remove all tracks from a Spotify playlist",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "playlist_id": {
                        "type": "string",
                        "description": "Spotify playlist ID"
                    }
                },
                "required": [
                    "playlist_id"
                ]
            }
        },
        {
            "name": "create_playlist",
            "description": "Create a new Spotify playlist with the given name",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "playlist_name": {
                        "type": "string",
                        "description": "Name for the new playlist"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional playlist description"
                    }
                },
                "required": [
                    "playlist_name"
                ]
            }
        },
        {
            "name": "add_tracks_to_playlist",
            "description": "Add tracks to a Spotify playlist by its ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "playlist_id": {
                        "type": "string",
                        "description": "Spotify playlist ID"
                    },
                    "track_uris": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of track URIs to add"
                    }
                },
                "required": [
                    "playlist_id",
                    "track_uris"
                ]
            }
        }
    ]
}
