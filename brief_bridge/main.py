from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
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

# Mount static files
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

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
        "description": "Remote command execution bridge for AI coding assistants",
        "status": "active",
        "base_url": base_url,
        "ai_assistant_guide": {
            "important_note": "AI assistants should use localhost URLs. Only clients need tunnel URLs for remote installation.",
            "architecture_overview": {
                "design": "AI (localhost) ↔ Brief Bridge (localhost) ↔ Tunnel ↔ Remote Clients",
                "url_strategy": {
                    "ai_operations": "Always use localhost URLs (http://localhost:port)",
                    "client_operations": "Use tunnel URLs provided by /tunnel/setup",
                    "future_note": "Remote AI access requires authentication & encryption (not implemented)"
                }
            },
            "quick_start_workflow": [
                "🚀 Step 1: POST /tunnel/setup to create tunnel",
                "📱 Step 2: Install clients using tunnel URL", 
                "👥 Step 3: GET /clients/ to list connected clients",
                "⚡ Step 4: Choose workflow based on task complexity"
            ],
            "file_transfer_workflows": {
                "simple_command_workflow": {
                    "description": "For simple tasks with small results",
                    "steps": [
                        "1. AI: POST /commands/submit with simple command",
                        "2. Client: Executes and uploads result file",
                        "3. Client: Reports 'FILE_UPLOADED: {file_id}' in output",
                        "4. AI: Extract file_id from command result",
                        "5. AI: GET /files/download/{file_id} to retrieve file",
                        "6. AI: Analyze file and DELETE /files/{file_id} to cleanup"
                    ],
                    "example": "Screenshots, system info, small logs"
                },
                "complex_script_workflow": {
                    "description": "For complex tasks requiring large scripts",
                    "steps": [
                        "1. AI: POST /files/upload to upload complex script",
                        "2. AI: Get script_id from upload response", 
                        "3. AI: POST /commands/submit with download-and-execute command",
                        "4. Client: Downloads script using tunnel URL",
                        "5. Client: Executes script and uploads result files",
                        "6. Client: Reports 'RESULT_UPLOADED: {file_id}' in output",
                        "7. AI: GET /files/download/{file_id} to retrieve results",
                        "8. AI: Cleanup both script and result files"
                    ],
                    "example": "System diagnostics, multi-step operations, large reports"
                },
                "batch_processing_workflow": {
                    "description": "For processing multiple files or repetitive tasks",
                    "steps": [
                        "1. AI: Upload processing script once",
                        "2. AI: Send multiple execution commands referencing same script",
                        "3. Clients: Download and execute same script with different parameters",
                        "4. AI: Collect and analyze multiple result files",
                        "5. AI: Cleanup script and result files when done"
                    ],
                    "example": "Log analysis across multiple machines, batch screenshots"
                }
            },
            "practical_examples": {
                "screenshot_task": {
                    "description": "Take screenshot from remote machine",
                    "ai_steps": [
                        "curl -X POST localhost:2266/files/upload -F 'file=@screenshot_script.ps1'",
                        "# Get script_id from response, e.g., 'abc123'",
                        "curl -X POST localhost:2266/commands/submit -d '{\"target_client_id\":\"client\",\"command_content\":\"$s=Invoke-WebRequest https://tunnel/files/download/abc123; & ([ScriptBlock]::Create($s.Content))\",\"command_type\":\"shell\"}'",
                        "# Wait for 'RESULT_UPLOADED: xyz789' in command output",
                        "curl localhost:2266/files/download/xyz789 > screenshot.png"
                    ]
                },
                "system_diagnostic": {
                    "description": "Collect system diagnostic information",
                    "command_template": "Get-ComputerInfo | ConvertTo-Json | Out-File -FilePath $env:TEMP\\diag.json; $r=Invoke-RestMethod -Uri 'TUNNEL_URL/files/upload' -Method POST -Form @{file=Get-Item $env:TEMP\\diag.json; client_id=$env:COMPUTERNAME}; Write-Output \"DIAGNOSTIC_UPLOADED: $($r.file_id)\""
                }
            },
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
                "upload_file": "POST /files/upload - Upload files from clients to server",
                "download_file": "GET /files/download/{file_id} - Download files by ID",
                "list_files": "GET /files/ - List all uploaded files",
                "delete_file": "DELETE /files/{file_id} - Delete files by ID",
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