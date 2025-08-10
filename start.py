#!/usr/bin/env python3
"""
Brief Bridge - Remote Command Execution Bridge
Startup script with user-friendly interface
"""
import asyncio
import argparse
import uvicorn
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_banner(port: int, host: str = "localhost"):
    """Print startup banner with connection information"""
    banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            🌉 Brief Bridge                                   ║
║              Remote Command Execution Bridge for AI Assistants              ║
╚══════════════════════════════════════════════════════════════════════════════╝

🚀 Server Starting...
   • Local URL:  http://{host}:{port}
   • Host:       {host}
   • Port:       {port}

📋 For AI Assistants:
   • GET  http://{host}:{port}/          - Complete API guide and endpoint reference
   • GET  http://{host}:{port}/docs      - Interactive Swagger documentation  
   • GET  http://{host}:{port}/health    - Health check endpoint

💡 Quick Start:
   1. Tell your AI assistant to visit: http://{host}:{port}/
   2. The AI can find all available endpoints and usage examples there
   3. Setup ngrok tunnel: POST http://{host}:{port}/tunnel/setup

⚡ Example for AI:
   "Please visit http://{host}:{port}/ to see what APIs are available"

🔧 Press Ctrl+C to stop the server
╔══════════════════════════════════════════════════════════════════════════════╗
"""
    print(banner)

def print_running_info(port: int, host: str = "localhost"):
    """Print information after server is running"""
    print(f"""
✅ Brief Bridge is running!

📍 Connection Info:
   • API Guide:      http://{host}:{port}/
   • Documentation:  http://{host}:{port}/static/index.html  
   • Swagger UI:     http://{host}:{port}/docs

🤖 For AI Assistants:
   → Tell them to check: http://{host}:{port}/
   → This provides a complete API reference with all endpoints and examples

🌐 To enable external access:
   → POST http://{host}:{port}/tunnel/setup with {{"provider": "ngrok"}}
""")

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(
        description="Brief Bridge - Remote Command Execution Bridge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py                    # Start on default port 2266
  python start.py --port 8080       # Start on custom port
  python start.py --host 0.0.0.0    # Accept external connections
        """
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=2266,
        help="Port to run the server on (default: 2266)"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--external",
        action="store_true",
        help="Accept external connections (sets host to 0.0.0.0)"
    )

    args = parser.parse_args()
    
    # Handle external connections
    if args.external:
        args.host = "0.0.0.0"
    
    # Print startup banner
    display_host = "localhost" if args.host in ["127.0.0.1", "0.0.0.0"] else args.host
    print_banner(args.port, display_host)
    
    try:
        # Configure uvicorn
        config = uvicorn.Config(
            "brief_bridge.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        # Custom startup message
        original_startup = server.config.on_startup
        
        def custom_startup():
            if original_startup:
                for func in original_startup:
                    func()
            print_running_info(args.port, display_host)
        
        # server.config.on_startup = [custom_startup]
        
        print("🔄 Starting uvicorn server...")
        server.run()
        
    except KeyboardInterrupt:
        print("\n\n🔄 Shutting down Brief Bridge...")
        print("✅ Server stopped. Thank you for using Brief Bridge!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()