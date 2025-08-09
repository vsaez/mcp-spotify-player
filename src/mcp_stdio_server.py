#!/usr/bin/env python3
"""
Servidor MCP para Spotify Player usando stdio
Implementa el protocolo MCP sobre JSON-RPC para comunicación con Cursor
"""

import json
import sys
import logging
from typing import Dict, Any, Optional
from src.config import Config
from src.spotify_controller import SpotifyController

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self):
        self.config = Config()
        self.controller = SpotifyController()
        self.request_id = 0
        
        # Manifiesto MCP
        self.manifest = {
            "schema_url": "https://json-schema.org/draft/2020-12/schema",
            "nameForHuman": "Spotify Player",
            "nameForModel": "spotify_player",
            "descriptionForHuman": "Controla tu música de Spotify usando comandos naturales",
            "descriptionForModel": "Herramienta para controlar la reproducción de música en Spotify. Puedes reproducir canciones, pausar, saltar, cambiar volumen, buscar música y más.",
            "auth": {
                "type": "oauth",
                "instructions": "Necesitas autenticarte con Spotify para usar esta herramienta"
            },
            "tools": [
                {
                    "name": "play_music",
                    "description": "Reproduce música en Spotify. Puedes especificar una canción, artista, playlist o simplemente reanudar la reproducción.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Búsqueda de canción o artista (ej: 'REM', 'Bohemian Rhapsody')"
                            },
                            "playlist_name": {
                                "type": "string",
                                "description": "Nombre de la playlist a reproducir"
                            },
                            "track_uri": {
                                "type": "string",
                                "description": "URI específica de la canción"
                            },
                            "artist_uri": {
                                "type": "string",
                                "description": "URI específica del artista"
                            }
                        }
                    }
                },
                {
                    "name": "pause_music",
                    "description": "Pausa la reproducción actual de música",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "skip_next",
                    "description": "Salta a la siguiente canción en la cola de reproducción",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "skip_previous",
                    "description": "Salta a la canción anterior en la cola de reproducción",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "set_volume",
                    "description": "Establece el volumen de reproducción (0-100%)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "volume_percent": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100,
                                "description": "Volumen entre 0 y 100"
                            }
                        },
                        "required": ["volume_percent"]
                    }
                },
                {
                    "name": "get_current_playing",
                    "description": "Obtiene información sobre la canción actualmente reproduciéndose",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "get_playback_state",
                    "description": "Obtiene el estado completo de reproducción incluyendo dispositivo, volumen, etc.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "search_music",
                    "description": "Busca música en Spotify por canción, artista o álbum",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Término de búsqueda"
                            },
                            "search_type": {
                                "type": "string",
                                "enum": ["track", "artist", "album"],
                                "default": "track",
                                "description": "Tipo de búsqueda"
                            },
                            "limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 50,
                                "default": 10,
                                "description": "Número máximo de resultados"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_playlists",
                    "description": "Obtiene la lista de playlists del usuario",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }

    def send_response(self, response: Dict[str, Any]):
        """Envía una respuesta JSON-RPC por stdout"""
        json_response = json.dumps(response, ensure_ascii=False) + "\n"
        sys.stdout.write(json_response)
        sys.stdout.flush()
        logger.info(f"Enviando respuesta: {response}")

    def send_error(self, request_id: Any, code: int, message: str):
        """Envía un error JSON-RPC"""
        # Manejar el caso donde request_id es None
        if request_id is None:
            return  # No enviar respuesta para notificaciones sin ID
        
        error_response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        self.send_response(error_response)

    def handle_initialize(self, request_id: Any, params: Dict[str, Any]):
        """Maneja la inicialización del cliente MCP"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "spotify-player",
                    "version": "1.0.0"
                }
            }
        }
        self.send_response(response)

    def handle_tools_list(self, request_id: Any):
        """Lista las herramientas disponibles"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.manifest["tools"]
            }
        }
        self.send_response(response)

    def handle_tools_call(self, request_id: Any, params: Dict[str, Any]):
        """Ejecuta una herramienta"""
        try:
            # Manejar tanto formato de array como formato directo
            if "calls" in params:
                # Formato: {"calls": [{"name": "...", "arguments": {...}}]}
                calls = params.get("calls", [])
            else:
                # Formato: {"name": "...", "arguments": {...}}
                calls = [{"name": params.get("name"), "arguments": params.get("arguments", {})}]
            
            results = []
            
            for call in calls:
                tool_name = call.get("name")
                arguments = call.get("arguments", {})
                
                if not tool_name:
                    continue
                
                # Verificar autenticación para comandos que la requieren
                if tool_name in ["play_music", "pause_music", "skip_next", "skip_previous", 
                               "set_volume", "get_current_playing", "get_playback_state"]:
                    logger.info(f"Verificando autenticación para {tool_name}")
                    if not self.controller.is_authenticated():
                        logger.warning(f"No autenticado para {tool_name}")
                        results.append({
                            "name": tool_name,
                            "content": [
                                {
                                    "type": "text",
                                    "text": "No autenticado con Spotify. Necesitas autenticarte primero."
                                }
                            ]
                        })
                        continue
                    else:
                        logger.info(f"Autenticado correctamente para {tool_name}")
                
                # Ejecutar el comando
                logger.info(f"Ejecutando {tool_name} con argumentos: {arguments}")
                result = self.execute_tool(tool_name, arguments)
                logger.info(f"Resultado de {tool_name}: {result}")
                results.append({
                    "name": tool_name,
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                })

            if len(results) == 1:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": results[0]
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "calls": results
                    }
                }

            self.send_response(response)
            
        except Exception as e:
            logger.error(f"Error ejecutando herramienta: {str(e)}")
            self.send_error(request_id, -32603, f"Error interno: {str(e)}")

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Ejecuta una herramienta específica"""
        try:
            if tool_name == "play_music":
                result = self.controller.play_music(
                    query=arguments.get("query"),
                    playlist_name=arguments.get("playlist_name"),
                    track_uri=arguments.get("track_uri"),
                    artist_uri=arguments.get("artist_uri")
                )
                if result.get('success'):
                    return f"{result.get('message', 'Reproducción iniciada')}"
                else:
                    return f"{result.get('message', 'No se pudo reproducir la música')}"
            
            elif tool_name == "pause_music":
                result = self.controller.pause_music()
                if result.get('success'):
                    return f"{result.get('message', 'Reproducción pausada')}"
                else:
                    return f"{result.get('message', 'No se pudo pausar')}"
            
            elif tool_name == "skip_next":
                result = self.controller.skip_next()
                if result.get('success'):
                    return f"{result.get('message', 'Saltando a la siguiente canción')}"
                else:
                    return f"{result.get('message', 'No se pudo saltar')}"
            
            elif tool_name == "skip_previous":
                result = self.controller.skip_previous()
                if result.get('success'):
                    return f"{result.get('message', 'Saltando a la canción anterior')}"
                else:
                    return f"{result.get('message', 'No se pudo saltar')}"
            
            elif tool_name == "set_volume":
                volume = arguments.get("volume_percent")
                if volume is None:
                    raise ValueError("volume_percent es requerido")
                result = self.controller.set_volume(volume)
                if result.get('success'):
                    return f"{result.get('message', f'Volumen establecido al {volume}%')}"
                else:
                    return f"{result.get('message', 'No se pudo cambiar el volumen')}"
            
            elif tool_name == "get_current_playing":
                result = self.controller.get_current_playing()
                if result.get('success'):
                    track = result.get('track', {})
                    is_playing = result.get('is_playing', False)
                    progress_ms = result.get('progress_ms', 0)
                    
                    if track:
                        status = "Reproduciendo" if is_playing else "Pausado"
                        logger.info("Debug: ejecutando get_current_playing")
                        return f"{status}: {track.get('name', 'Desconocida')} por {track.get('artist', 'Desconocido')}"
                    else:
                        return "No hay música reproduciéndose actualmente"
                else:
                    return f"No se pudo obtener información: {result.get('message', 'Error desconocido')}"
            
            elif tool_name == "get_playback_state":
                result = self.controller.get_playback_state()
                if result.get('success'):
                    state = result.get('state', {})
                    current_track = state.get('current_track', {})
                    is_playing = state.get('is_playing', False)
                    volume = state.get('volume_percent', 0)
                    device = state.get('device_name', 'Desconocido')
                    
                    if current_track:
                        status = "Reproduciendo" if is_playing else "Pausado"
                        track_info = f"{current_track.get('name', 'Desconocida')} - {current_track.get('artist', 'Desconocido')}"
                        return f"{status}: {track_info} | Volumen: {volume}% | Dispositivo: {device}"
                    else:
                        return f"No hay música reproduciéndose | Volumen: {volume}% | Dispositivo: {device}"
                else:
                    return f"No se pudo obtener el estado: {result.get('message', 'Error desconocido')}"
            
            elif tool_name == "search_music":
                query = arguments.get("query")
                if not query:
                    raise ValueError("query es requerido")
                result = self.controller.search_music(
                    query=query,
                    search_type=arguments.get("search_type", "track"),
                    limit=arguments.get("limit", 10)
                )
                if result.get('success'):
                    tracks = result.get('tracks', [])
                    total = result.get('total_results', 0)
                    if tracks:
                        track_list = []
                        for i, track in enumerate(tracks[:5], 1):
                            track_list.append(f"{i}. {track.get('name', 'Desconocida')} - {track.get('artist', 'Desconocido')}")
                        return f"Encontradas {len(tracks)} canciones para '{query}' (de {total} total):\n" + "\n".join(track_list)
                    else:
                        return f"No se encontraron canciones para '{query}'"
                else:
                    return f"Error en la búsqueda: {result.get('message', 'Error desconocido')}"
            
            elif tool_name == "get_playlists":
                result = self.controller.get_playlists()
                if result.get('success'):
                    playlists = result.get('playlists', [])
                    total = result.get('total_playlists', 0)
                    if playlists:
                        playlist_list = []
                        #for i, playlist in enumerate(playlists[:10], 1):
                        for i, playlist in enumerate(playlists, 1):
                            playlist_list.append(f"{i}. {playlist.get('name', 'Desconocida')} ({playlist.get('track_count', 0)} canciones)")
                        return f"Encontradas {len(playlists)} playlists (de {total} total):\n" + "\n".join(playlist_list)
                    else:
                        return f"No se encontraron playlists"
                else:
                    return f"Error obteniendo playlists: {result.get('message', 'Error desconocido')}"
            
            else:
                raise ValueError(f"Herramienta '{tool_name}' no soportada")
                
        except Exception as e:
            logger.error(f"Error ejecutando {tool_name}: {str(e)}")
            return f"Error: {str(e)}"

    def run(self):
        """Ejecuta el servidor MCP"""
        logger.info("Iniciando servidor MCP Spotify Player...")
        
        try:
            while True:
                # Leer línea de stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                try:
                    # Parsear JSON-RPC
                    request = json.loads(line.strip())
                    method = request.get("method")
                    request_id = request.get("id")
                    params = request.get("params", {})
                    
                    logger.info(f"Recibido: {method}")
                    
                    # Manejar métodos MCP
                    if method == "initialize":
                        self.handle_initialize(request_id, params)
                    elif method == "notifications/initialized":
                        # No hacer nada para notificaciones de inicialización
                        logger.info("Cliente inicializado correctamente")
                    elif method == "tools/list":
                        self.handle_tools_list(request_id)
                    elif method == "tools/call":
                        self.handle_tools_call(request_id, params)
                    elif method in ["resources/list", "prompts/list"]:
                        # Métodos opcionales que no implementamos
                        logger.info(f"Método opcional no implementado: {method}")
                        if request_id is not None:
                            self.send_error(request_id, -32601, f"Método '{method}' no implementado")
                    else:
                        logger.warning(f"Método no soportado: {method}")
                        if request_id is not None:
                            self.send_error(request_id, -32601, f"Método '{method}' no soportado")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Error parseando JSON: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error procesando petición: {e}")
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Servidor detenido por el usuario")
        except Exception as e:
            logger.error(f"Error en el servidor: {e}")

if __name__ == "__main__":
    server = MCPServer()
    server.run() 