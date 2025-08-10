from fastapi import FastAPI
from brief_bridge.web.client_router import router as client_router
from brief_bridge.web.command_router import router as command_router
from brief_bridge.web.tunnel_router import router as tunnel_router

app = FastAPI(
    title="Brief Bridge",
    description="A lightweight tool that bridges AI coding assistants with distributed clients through HTTP polling",
    version="0.1.0"
)

# 包含路由
app.include_router(client_router)
app.include_router(command_router)
app.include_router(tunnel_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Brief Bridge API"}