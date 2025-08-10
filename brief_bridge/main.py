from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from brief_bridge.web.client_router import router as client_router
from brief_bridge.web.command_router import router as command_router
from brief_bridge.web.tunnel_router import router as tunnel_router
from brief_bridge.web.install_router import router as install_router
from brief_bridge.web.client_download_router import router as client_download_router
from brief_bridge.services.ngrok_manager import cleanup_all_ngrok_tunnels

# Global flag to prevent multiple cleanup attempts
_cleanup_done = False

async def cleanup_handler():
    """Cleanup handler for graceful shutdown"""
    global _cleanup_done
    if _cleanup_done:
        return
    
    _cleanup_done = True
    try:
        print("🔄 Initiating cleanup...")
        await cleanup_all_ngrok_tunnels()
        print("✅ Ngrok tunnels cleaned up successfully")
    except Exception as e:
        print(f"⚠️ Error during ngrok cleanup: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Brief Bridge started")
    
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
app.include_router(client_download_router)


@app.get("/health", 
         summary="Health Check",
         description="Check if the Brief Bridge server is running and healthy",
         tags=["health"])
async def health_check():
    """Health check endpoint to verify server status"""
    return {"status": "healthy"}


@app.get("/", 
         summary="API Guide for AI Assistants", 
         description="Complete API reference and usage guide specifically designed for AI coding assistants",
         tags=["documentation"])
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
            "tunnel_setup_example": {
                "description": "How to setup tunnel for remote client access",
                "required_parameters": {
                    "provider": "Tunnel provider name (currently supported: 'ngrok')"
                },
                "optional_parameters": {
                    "auth_token": "Authentication token for tunnel provider (uses system config if omitted)",
                    "config": "Additional configuration options (JSON object)"
                },
                "basic_setup": f"curl -X POST {base_url}/tunnel/setup -H \"Content-Type: application/json\" -d '{{\"provider\": \"ngrok\"}}'",
                "with_auth_token": f"curl -X POST {base_url}/tunnel/setup -H \"Content-Type: application/json\" -d '{{\"provider\": \"ngrok\", \"auth_token\": \"your-ngrok-token\"}}'",
                "expected_response": {
                    "status": "active",
                    "public_url": "https://abc123.ngrok-free.app", 
                    "remote_client_installation": {
                        "instructions": "Use these commands on remote machines to install Brief Bridge clients:",
                        "powershell_direct": "irm https://abc123.ngrok-free.app/install.ps1 | iex",
                        "bash_direct": "curl -sSL https://abc123.ngrok-free.app/install.sh | bash"
                    }
                }
            },
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
            "example_command_submission": f"curl -X POST {base_url}/commands/submit -H \"Content-Type: application/json\" -d '{{\"target_client_id\": \"your-client\", \"command_content\": \"Get-Date\", \"command_type\": \"shell\"}}'"
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