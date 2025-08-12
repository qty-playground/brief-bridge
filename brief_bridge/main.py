from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from contextlib import asynccontextmanager
import os
from brief_bridge.web.client_router import router as client_router
from brief_bridge.web.command_router import router as command_router
from brief_bridge.web.tunnel_router import router as tunnel_router
from brief_bridge.web.install_router import router as install_router
from brief_bridge.web.file_router import router as file_router
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

# Static files removed - use /prompts.md for documentation

# 包含路由
app.include_router(client_router)
app.include_router(command_router)
app.include_router(tunnel_router)
app.include_router(install_router)
app.include_router(file_router)


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
        "description": "Remote command execution platform for AI coding assistants",
        "status": "active",
        "architecture": "AI ↔ Brief Bridge ↔ Tunnel ↔ Remote Clients",
        "documentation": {
            "comprehensive_guide": f"{base_url}/prompts.md",
            "interactive_api": f"{base_url}/docs"
        },
        "message": "📖 Visit /prompts.md for complete usage guide, workflows, and best practices"
    }


@app.get("/prompts.md",
         response_class=PlainTextResponse,
         summary="AI Assistant Prompts Guide",
         description="Markdown documentation guide for AI assistants")
async def get_prompts_md():
    """
    Get markdown documentation for AI assistants.
    
    Returns the prompts.md file content dynamically loaded from filesystem.
    """
    prompts_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts.md")
    
    try:
        with open(prompts_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "# Brief Bridge Prompts Guide\n\nPrompts guide file not found."
    except Exception as e:
        return f"# Brief Bridge Prompts Guide\n\nError loading prompts guide: {str(e)}"