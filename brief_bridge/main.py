from fastapi import FastAPI
from contextlib import asynccontextmanager
import signal
import asyncio
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
    # Startup - register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    print("🚀 Brief Bridge started - ngrok cleanup handlers registered")
    
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

# 包含路由
app.include_router(client_router)
app.include_router(command_router)
app.include_router(tunnel_router)
app.include_router(install_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Brief Bridge API"}