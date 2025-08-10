"""Install script router for serving one-click install scripts"""
from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse
from typing import Optional
from ..use_cases.install_script_use_case import InstallScriptUseCase

router = APIRouter()

@router.get("/install.ps1", 
           response_class=PlainTextResponse,
           summary="Get PowerShell Install Script",
           description="Generate a one-click PowerShell installation script for Windows clients. This script will automatically download, configure, and start the Brief Bridge client.",
           tags=["installation"])
async def get_powershell_install(
    request: Request,
    client_id: Optional[str] = Query(None, description="Custom client ID (defaults to hostname)"),
    client_name: Optional[str] = Query(None, description="Human-readable client name"), 
    poll_interval: int = Query(5, description="Polling interval in seconds"),
    debug: bool = Query(False, description="Enable debug mode for verbose output")
):
    """Get PowerShell one-click install script"""
    # Get the server URL from the request
    server_url = f"{request.url.scheme}://{request.url.netloc}"
    use_case = InstallScriptUseCase(server_url=server_url)
    script = use_case.generate_powershell_script(
        client_id=client_id,
        client_name=client_name,
        poll_interval=poll_interval,
        debug=debug
    )
    return script

