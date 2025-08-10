#!/usr/bin/env python3
"""
Brief Bridge CLI - Command line interface for the Brief Bridge server
"""
import argparse
import uvicorn
import sys
import asyncio
import signal
import os
from pathlib import Path

def print_banner(port: int, host: str = "localhost", command_timeout: float = 300.0):
    """Print startup banner with connection information"""
    timeout_minutes = command_timeout / 60
    banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            🌉 Brief Bridge                                   ║
║              Remote Command Execution Bridge for AI Assistants              ║
╚══════════════════════════════════════════════════════════════════════════════╝

🚀 Server Starting...
   • Local URL:  http://{host}:{port}
   • Host:       {host}
   • Port:       {port}
   • Command Timeout: {timeout_minutes:.1f} minutes ({command_timeout:.0f}s)

📋 For AI Assistants (use localhost URLs):
   • GET  http://{host}:{port}/          - Complete API guide and endpoint reference
   • GET  http://{host}:{port}/docs      - Interactive Swagger documentation  
   • GET  http://{host}:{port}/health    - Health check endpoint

💡 Quick Start for AI:
   1. Tell your AI assistant: "Please visit http://{host}:{port}/"
   2. The AI can find all available endpoints and usage examples there
   3. For remote client access, AI should setup tunnel first

🌐 For Remote Client Installation:
   1. Setup tunnel: POST http://{host}:{port}/tunnel/setup
   2. Use tunnel URL for client installation scripts
   3. AI uses localhost, clients use tunnel URL

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
   → Tell them: "Please visit http://{host}:{port}/ to see available APIs"
   → AI should use localhost URLs for all API calls
   → Complete endpoint reference and examples available at root

🌐 For Remote Client Installation:
   → First setup tunnel: POST http://{host}:{port}/tunnel/setup
   → Then use tunnel URL for client install scripts
   → Clients will connect to tunnel, AI uses localhost
""")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Brief Bridge - Remote Command Execution Bridge for AI Assistants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  brief-bridge                       # Start on default port 2266
  brief-bridge --port 8080          # Start on custom port
  brief-bridge --external           # Accept external connections
  brief-bridge --reload             # Enable auto-reload for development
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
    
    parser.add_argument(
        "--command-timeout",
        type=float,
        default=None,
        help="Maximum time to wait for command execution (in seconds, default: 300 = 5 minutes)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Brief Bridge 0.1.0"
    )

    args = parser.parse_args()
    
    # Handle external connections
    if args.external:
        args.host = "0.0.0.0"
    
    # Set command timeout: CLI parameter overrides environment variable, which overrides default
    if args.command_timeout is not None:
        # CLI parameter specified - use it
        final_timeout = args.command_timeout
        os.environ['BRIEF_BRIDGE_COMMAND_TIMEOUT'] = str(final_timeout)
    else:
        # No CLI parameter - use environment variable or default
        final_timeout = float(os.getenv('BRIEF_BRIDGE_COMMAND_TIMEOUT', '300.0'))
    
    # Print startup banner
    display_host = "localhost" if args.host in ["127.0.0.1", "0.0.0.0"] else args.host
    print_banner(args.port, display_host, final_timeout)
    
    try:
        print("🔄 Starting uvicorn server...")
        print_running_info(args.port, display_host)
        
        # Import here to avoid import issues
        from brief_bridge.main import app
        
        # Configure and run uvicorn
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n\n🔄 Shutting down Brief Bridge...")
        print("✅ Server stopped. Thank you for using Brief Bridge!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()