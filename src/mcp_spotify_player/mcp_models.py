from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class MCPRequest(BaseModel):
    """Modelo base para las peticiones MCP"""
    jsonrpc: str = "2.0"
    id: Union[str, int]
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    """Base model for MCP requests"""
    jsonrpc: str = "2.0"
    id: Union[str, int]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class MCPError(BaseModel):
    """Model for MCP errors"""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

# Models for specific Spotify commands
class PlayRequest(BaseModel):
    """Model for playback request"""
    query: Optional[str] = Field(None, description="Búsqueda de canción o artista")
    playlist_name: Optional[str] = Field(None, description="Nombre de la playlist")
    track_uri: Optional[str] = Field(None, description="URI específica de la canción")
    artist_uri: Optional[str] = Field(None, description="URI específica del artista")

class VolumeRequest(BaseModel):
    """Model for volume change request"""
    volume_percent: int = Field(..., ge=0, le=100, description="Volumen entre 0 y 100")

class SearchRequest(BaseModel):
    """Model for search request"""
    query: str = Field(..., description="Término de búsqueda")
    search_type: str = Field("track", description="Tipo de búsqueda: track, artist, album")
    limit: int = Field(10, ge=1, le=50, description="Número máximo de resultados")

class PlaylistRequest(BaseModel):
    """Model for playlist request"""
    playlist_name: Optional[str] = Field(None, description="Nombre de la playlist")
    playlist_id: Optional[str] = Field(None, description="ID de la playlist")

# Models to requests
class TrackInfo(BaseModel):
    """Tracks information"""
    name: str
    artist: str
    album: str
    uri: str
    duration_ms: int
    external_url: str

class PlaybackState(BaseModel):
    """Playback state"""
    is_playing: bool
    current_track: Optional[TrackInfo] = None
    volume_percent: int
    device_name: Optional[str] = None
    shuffle_state: bool
    repeat_state: str

class SearchResult(BaseModel):
    """Search result"""
    tracks: List[TrackInfo] = []
    artists: List[Dict[str, Any]] = []
    albums: List[Dict[str, Any]] = []

class PlaylistInfo(BaseModel):
    id: str
    name: str
    owner: Optional[Union[str, dict]] = "unknown"  # Hacerlo opcional con valor predeterminado
    track_count: int

    @field_validator('owner')
    def validate_owner(cls, v):
        if v is None:
            return "unknown"
        if isinstance(v, dict):
            # Si es un objeto, extrae el ID del propietario
            return v.get('id', 'unknown')
        return v

# Models for MCP manifest
class MCPTool(BaseModel):
    """MCP tool"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

class MCPManifest(BaseModel):
    """MCP server manifest"""
    schema_url: str = "https://json-schema.org/draft/2020-12/schema"
    nameForHuman: str
    nameForModel: str
    descriptionForHuman: str
    descriptionForModel: str
    auth: Dict[str, Any]
    api: Dict[str, Any]
    contactEmail: Optional[str] = None
    legalInfoUrl: Optional[str] = None
    tools: List[MCPTool] 