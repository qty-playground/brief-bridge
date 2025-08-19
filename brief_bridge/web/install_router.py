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
    idle_timeout_minutes: int = Query(10, description="Idle timeout in minutes before client auto-terminates"),
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
        idle_timeout_minutes=idle_timeout_minutes,
        debug=debug
    )
    return script


@router.get("/install-modular.ps1", 
           response_class=PlainTextResponse,
           summary="Get Modular PowerShell Install Script",
           description="Generate a modular PowerShell installation script with reusable functions and built-in commands. This is an enhanced version of the basic install.ps1 with better code organization and additional functionality.",
           tags=["installation"])
async def get_modular_powershell_install(
    request: Request,
    client_id: Optional[str] = Query(None, description="Custom client ID (defaults to hostname)"),
    client_name: Optional[str] = Query(None, description="Human-readable client name"), 
    poll_interval: int = Query(5, description="Polling interval in seconds"),
    idle_timeout_minutes: int = Query(10, description="Idle timeout in minutes before client auto-terminates"),
    debug: bool = Query(False, description="Enable debug mode for verbose output")
):
    """Get Modular PowerShell one-click install script"""
    # Get the server URL from the request
    server_url = f"{request.url.scheme}://{request.url.netloc}"
    use_case = InstallScriptUseCase(server_url=server_url)
    script = use_case.generate_modular_powershell_script(
        client_id=client_id,
        client_name=client_name,
        poll_interval=poll_interval,
        idle_timeout_minutes=idle_timeout_minutes,
        debug=debug
    )
    return script


@router.get("/install.sh", 
           response_class=PlainTextResponse,
           summary="Get Bash Install Script",
           description="Generate a one-click Bash installation script for Linux/macOS clients. This script will automatically download, configure, and start the Brief Bridge client.",
           tags=["installation"])
async def get_bash_install(
    request: Request,
    client_id: Optional[str] = Query(None, description="Custom client ID (defaults to hostname)"),
    client_name: Optional[str] = Query(None, description="Human-readable client name"), 
    poll_interval: int = Query(5, description="Polling interval in seconds"),
    idle_timeout_minutes: int = Query(10, description="Idle timeout in minutes before client auto-terminates"),
    debug: bool = Query(False, description="Enable debug mode for verbose output")
):
    """Get Bash one-click install script"""
    # Get the server URL from the request
    server_url = f"{request.url.scheme}://{request.url.netloc}"
    use_case = InstallScriptUseCase(server_url=server_url)
    script = use_case.generate_bash_script(
        client_id=client_id,
        client_name=client_name,
        poll_interval=poll_interval,
        idle_timeout_minutes=idle_timeout_minutes,
        debug=debug
    )
    return script

