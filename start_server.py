#!/usr/bin/env python3
"""
Script to start the MCP Spotify Player server
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import requests
        import pydantic
        print("✅ All dependencies are intalled")
        return True
    except ImportError as e:
        print(f"❌ Dependency not found: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False

def check_env_file():
    """Verify that the .env file is configured correctly"""
    print("🔍 Verififing .env file...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Copy env.example to .env and configure your credentials")
        return False
    

    # Verify that the .env file contains valid Spotify credentials
    with open(env_file, 'r') as f:
        content = f.read()
        if "tu_client_id_aqui" in content or "tu_client_secret_aqui" in content:
            print("❌ Spotify credentials not configured")
            print("💡 Edit .env with your real credentials")
            return False
    
    print("✅ File .env successfully configured")
    return True

def check_port_available(host, port):
    """Verify if a port is available on the given host"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0  # True if port is available
    except Exception:
        return False

def start_server():
    """Start the MCP Spotify Player server"""
    print("🚀 Starting MCP Spotify Player...")
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Verify .env file configuration
    if not check_env_file():
        return False
    
    # Verify port availability
    if not check_port_available("127.0.0.1", 8000):
        print("❌ Port 8000 is already in use")
        print("💡 Stop other services or change the port in .env")
        return False
    
    print("✅ Everything ok to start server")
    print("=" * 50)
    
    try:

        from src.config import Config
        from src.mcp_server import app
        import uvicorn
        
        config = Config()

        print(f"🎵 MCP Spotify Player")
        print(f"📍 Server: http://{config.HOST}:{config.PORT}")
        print(f"🔧 Debug mode: {config.DEBUG}")
        print()
        print("📋 Available endpoints:")
        print(f"  • Server: http://{config.HOST}:{config.PORT}")
        print(f"  • Authentication: http://{config.HOST}:{config.PORT}/auth")
        print(f"  • Status: http://{config.HOST}:{config.PORT}/status")
        print(f"  • Documentation: http://{config.HOST}:{config.PORT}/docs")
        print()
        print("🔧 How to use with Claude:")
        print("1. Visit /auth to authenticate with Spotify")
        print("2. Configure Claude to use this MCP server")
        print("3. Enjoy controlling your music with natural commands!")
        print()
        print("⏳ Starting server... (Ctrl+C to stop)")
        print("=" * 50)
        

        uvicorn.run(
            app,
            host=config.HOST,
            port=config.PORT,
            reload=config.DEBUG,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stoppped by user")
    except Exception as e:
        print(f"❌ Error initializing server: {e}")
        print("💡 Verify configuration and dependencies")
        return False
    
    return True

def main():
    """Main function to run the server initializer"""
    print("🎵 MCP Spotify Player - Server initializer")
    print("=" * 50)
    
    success = start_server()
    
    if not success:
        print("\n💡 Troubleshooting:")
        print("1. Make sure Python 3.8+ is installed")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Configure .env with your Spotify credentials")
        print("4. Ensure port 8000 is free")
        print("5. Run: python check_server.py for diagnostics")

if __name__ == "__main__":
    main() 