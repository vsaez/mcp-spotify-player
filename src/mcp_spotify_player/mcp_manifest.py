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
            "name": "queue_add",
            "description": "Add a track/episode URI to the active device queue (optionally to a specific device).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "uri": {"type": "string"},
                    "device_id": {"type": "string"}
                },
                "required": ["uri"]
            }
        },
        {
            "name": "queue_list",
            "description": "Get the current playing item and the upcoming queue (may be truncated by Spotify).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1}
                }
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
            "name": "set_repeat",
            "description": "Set the repeat mode for playback (track, context, or off)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "enum": [
                            "track",
                            "context",
                            "off"
                        ],
                        "description": "Repeat mode"
                    }
                },
                "required": [
                    "state"
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
            "name": "get_devices",
            "description": "Retrieve available Spotify devices",
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
            "name": "search_collections",
            "description": "Search for playlists or albums on Spotify",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Search term",
                    },
                    "type": {
                        "type": "string",
                        "enum": ["playlist", "album"],
                        "description": "Type of collection to search",
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 20,
                        "description": "Number of items to return",
                    },
                    "offset": {
                        "type": "integer",
                        "minimum": 0,
                        "default": 0,
                        "description": "Index of the first result to return",
                    },
                    "market": {
                        "type": "string",
                        "description": "ISO 3166-1 alpha-2 market code",
                    },
                },
                "required": ["q", "type"],
            },
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
            "name": "get_artist",
            "description": "Retrieve artist information by its ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "artist_id": {
                        "type": "string",
                        "description": "Spotify artist ID",
                    }
                },
                "required": ["artist_id"],
            },
        },
        {
            "name": "get_album",
            "description": "Retrieve album information by its ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "album_id": {
                        "type": "string",
                        "description": "Spotify album ID"
                    }
                },
                "required": [
                    "album_id"
                ]
            }
        },
        {
            "name": "get_albums",
            "description": "Retrieve information for multiple albums by their IDs",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "album_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Spotify album IDs"
                    }
                },
                "required": ["album_ids"]
            }
        },
        {
            "name": "get_album_tracks",
            "description": "Retrieve tracks from a given album",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "album_id": {
                        "type": "string",
                        "description": "Album ID"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    }
                },
                "required": ["album_id"]
            }
        },
        {
            "name": "get_saved_albums",
            "description": "Retrieve the user's saved albums",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 20
                    }
                }
            }
        },
        {
            "name": "check_saved_albums",
            "description": "Check if the specified albums are saved in the user's library",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "album_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Spotify album IDs"
                    }
                },
                "required": ["album_ids"]
            }
        },
        {
            "name": "save_albums",
            "description": "Save one or more albums to the user's library",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "album_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Spotify album IDs"
                    }
                },
                "required": ["album_ids"]
            }
        },
        {
            "name": "delete_saved_albums",
            "description": "Remove one or more albums from the user's library",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "album_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Spotify album IDs"
                    }
                },
                "required": ["album_ids"]
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
        },
        {
            "name": "diagnose",
            "description": "Display diagnostic information about authentication and environment",
            "inputSchema": {"type": "object", "properties": {}}
        }
    ]
}
