import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Brief Bridge application...")
    yield
    logger.info("Shutting down Brief Bridge application...")


app = FastAPI(
    title="Brief Bridge",
    description="A lightweight tool that bridges AI coding assistants with distributed clients through HTTP polling",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "brief-bridge"}


@app.get("/")
async def root(request: Request):
    """Usage instructions for Brief Bridge"""
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    return {
        "title": "Brief Bridge",
        "description": "A lightweight tool that bridges AI coding assistants with distributed clients through HTTP polling",
        "version": "0.1.0",
        "real_world_example": {
            "scenario": "You're developing on macOS with Claude Code, but need to write PowerShell 5.1 compatible scripts",
            "steps": [
                "Start a Windows client: Run the one-liner on your Windows machine",
                "Ask Claude Code: 'Test this PowerShell script on Windows'",
                "Claude executes remotely: Gets real PowerShell 5.1 output and compatibility issues",
                "Iterate faster: Fix issues without leaving your macOS environment"
            ]
        },
        "quick_start": {
            "windows": f"& ([scriptblock]::Create((Invoke-WebRequest '{base_url}/client.ps1').Content))",
            "linux_macos": f"curl -sSL {base_url}/client.sh | bash"
        },
        "features": [
            "AI coding assistants execute commands on remote machines",
            "Zero installation - pure shell scripts", 
            "Works behind firewalls via tunneling",
            "Collect runtime context from heterogeneous environments"
        ],
        "architecture": "AI Assistant → HTTP Server → Public Endpoint → Clients (polling)",
        "api_endpoints": {
            "GET /": "Usage instructions (this page)",
            "POST /commands": "Submit command",
            "GET /commands/{id}": "Get result",
            "GET /clients": "List clients"
        },
        "api_documentation": {
            "openapi_json": f"{base_url}/openapi.json",
            "swagger_ui": f"{base_url}/docs",
            "redoc": f"{base_url}/redoc"
        },
        "use_cases": [
            "Cross-platform development: Write PowerShell on macOS, test on Windows",
            "Real environment testing: Debug issues in actual target environments",
            "Runtime context collection: Get OS-specific logs, error messages, system info",
            "Compatibility verification: Ensure scripts work across different OS versions"
        ],
        "status": "🚧 MVP in development - Core polling mechanism and command execution"
    }