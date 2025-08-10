from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import signal
import asyncio
import os
from brief_bridge.web.client_router import router as client_router
from brief_bridge.web.command_router import router as command_router
from brief_bridge.web.tunnel_router import router as tunnel_router
from brief_bridge.web.install_router import router as install_router
from brief_bridge.services.ngrok_manager import cleanup_all_ngrok_tunnels

async def cleanup_handler():
    """Cleanup handler for graceful shutdown"""
    try:
        await cleanup_all_ngrok_tunnels()
        print("✅ Ngrok tunnels cleaned up successfully")
    except Exception as e:
        print(f"⚠️ Error during ngrok cleanup: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🔄 Received signal {signum}, initiating cleanup...")
    asyncio.create_task(cleanup_handler())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - register signal handlers (only in main thread)
    try:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        print("🚀 Brief Bridge started - ngrok cleanup handlers registered")
    except ValueError as e:
        # Signal handling not available in tests
        print(f"🔄 Signal handlers not registered (test environment): {e}")
    
    yield
    
    # Shutdown - cleanup all ngrok tunnels
    print("🔄 Brief Bridge shutting down...")
    await cleanup_handler()


app = FastAPI(
    title="Brief Bridge",
    description="A lightweight tool that bridges AI coding assistants with distributed clients through HTTP polling",
    version="0.1.0",
    lifespan=lifespan
)

# Mount static files
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# 包含路由
app.include_router(client_router)
app.include_router(command_router)
app.include_router(tunnel_router)
app.include_router(install_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root(request: Request):
    """Brief Bridge API - Simple JSON guide for AI assistants"""
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    
    return {
        "service": "Brief Bridge",
        "description": "Remote command execution bridge for AI coding assistants",
        "status": "active",
        "base_url": base_url,
        "ai_assistant_guide": {
            "important_note": "AI assistants should use localhost URLs. Only clients need tunnel URLs for remote installation.",
            "recommended_workflow": [
                "🚀 START HERE: Setup tunnel first with POST /tunnel/setup (this is the primary use case)",
                "1. AI uses localhost: All API calls use localhost URLs", 
                "2. Setup tunnel: POST /tunnel/setup to enable remote client connections",
                "3. Install remote clients: Use tunnel URL from step 2 for client installation scripts",
                "4. List clients: GET /clients/ (localhost) to see connected remote clients",
                "5. Submit command: POST /commands/submit with target_client_id and command_content (localhost)",
                "6. Check results: GET /commands/ (localhost) to see execution results"
            ],
            "key_endpoints": {
                "tunnel_setup": "POST /tunnel/setup - ⭐ CRITICAL FIRST STEP for remote usage",
                "tunnel_status": "GET /tunnel/status - Check tunnel connection status",
                "list_clients": "GET /clients/",
                "submit_command": "POST /commands/submit", 
                "poll_commands": "POST /commands/poll",
                "submit_result": "POST /commands/result",
                "list_commands": "GET /commands/",
                "powershell_install": "GET /install.ps1 - Use tunnel URL for remote clients",
                "bash_install": "GET /install.sh - Use tunnel URL for remote clients"
            },
            "example_command": f"curl -X POST {base_url}/commands/submit -H \"Content-Type: application/json\" -d '{{\"target_client_id\": \"your-client\", \"command_content\": \"Get-Date\", \"command_type\": \"shell\"}}'"
        },
        "documentation": {
            "full_guide": f"{base_url}/static/index.html",
            "swagger_docs": f"{base_url}/docs",
            "health_check": f"{base_url}/health"
        },
        "quick_links": {
            "clients": f"{base_url}/clients/",
            "commands": f"{base_url}/commands/",
            "tunnel_status": f"{base_url}/tunnel/status"
        }
    }