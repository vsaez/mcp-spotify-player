#!/usr/bin/env python3
"""
MCP Spotify Player - Servidor principal
Controla Spotify desde Claude usando el protocolo MCP
"""

import uvicorn
from src.config import Config
from src.mcp_server import app

def main():
    """Función principal para ejecutar el servidor"""
    config = Config()
    
    print("🎵 MCP Spotify Player")
    print("=" * 50)
    print(f"Servidor iniciando en http://{config.HOST}:{config.PORT}")
    print(f"Modo debug: {config.DEBUG}")
    print()
    print("📋 Endpoints disponibles:")
    print(f"  • Servidor: http://{config.HOST}:{config.PORT}")
    print(f"  • Autenticación: http://{config.HOST}:{config.PORT}/auth")
    print(f"  • Estado: http://{config.HOST}:{config.PORT}/status")
    print(f"  • Documentación: http://{config.HOST}:{config.PORT}/docs")
    print()
    print("🔧 Para usar con Claude:")
    print("1. Visita /auth para autenticarte con Spotify")
    print("2. Configura Claude para usar este servidor MCP")
    print("3. ¡Disfruta controlando tu música con comandos naturales!")
    print()
    
    # Iniciar el servidor
    print(f"🚀 Iniciando servidor en http://{config.HOST}:{config.PORT}")
    print("⏳ Espera un momento...")
    
    try:
        uvicorn.run(
            app,
            host=config.HOST,
            port=config.PORT,
            reload=config.DEBUG,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando el servidor: {e}")
        print("💡 Verifica que el puerto 8000 no esté en uso")

if __name__ == "__main__":
    main() 