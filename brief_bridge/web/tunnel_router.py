"""Tunnel management router for Web API"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from ..use_cases.tunnel_setup_use_case import TunnelSetupUseCase
from .dependencies import get_tunnel_setup_use_case

router = APIRouter(prefix="/tunnel", tags=["tunnel"])


class TunnelSetupRequest(BaseModel):
    """Request schema for tunnel setup"""
    provider: str = Field(
        description="Tunnel provider name. Currently supported: 'ngrok'",
        example="ngrok"
    )
    auth_token: Optional[str] = Field(
        None, 
        description="Authentication token for the tunnel provider (optional). If not provided, will use system configuration or environment variables."
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional configuration options for the tunnel provider (optional)"
    )


class RemoteClientInstallation(BaseModel):
    """Schema for remote client installation commands"""
    instructions: str = Field(description="Human-readable instructions for installing remote clients")
    commands: Dict[str, str] = Field(description="Platform-specific installation commands")
    powershell_direct: str = Field(description="Direct PowerShell command for Windows installation")
    bash_direct: str = Field(description="Direct Bash command for Linux/macOS installation")


class TunnelSetupResponse(BaseModel):
    """Response schema for tunnel setup"""
    status: str = Field(description="Current tunnel status ('active' or 'inactive')")
    public_url: str = Field(description="Public URL of the established tunnel")
    provider: str = Field(description="Tunnel provider used (e.g., 'ngrok')")
    install_urls: Dict[str, str] = Field(description="URLs for downloading installation scripts")
    remote_client_installation: RemoteClientInstallation = Field(
        description="Complete remote client installation information and commands"
    )


class TunnelStatusResponse(BaseModel):
    """Response schema for tunnel status"""
    active: bool = Field(description="Whether the tunnel is currently active")
    provider: Optional[str] = Field(None, description="Tunnel provider name if active")
    public_url: Optional[str] = Field(None, description="Public URL if tunnel is active")
    uptime: Optional[int] = Field(None, description="Tunnel uptime in seconds")
    connections: Optional[int] = Field(None, description="Number of active connections")
    install_commands: Optional[Dict[str, str]] = Field(
        None, 
        description="Platform-specific installation commands if tunnel is active"
    )


@router.post("/setup", 
            response_model=TunnelSetupResponse,
            summary="Setup Tunnel",
            description="Set up ngrok tunnel to enable remote client connections. Returns public URL and installation commands for remote clients.",
            tags=["tunnel"])
async def setup_tunnel(
    request: TunnelSetupRequest,
    tunnel_use_case: TunnelSetupUseCase = Depends(get_tunnel_setup_use_case)
):
    """Set up tunnel with specified provider"""
    try:
        config = request.config or {}
        if request.auth_token:
            config["auth_token"] = request.auth_token
            
        result = await tunnel_use_case.setup_tunnel(request.provider, config)
        
        return TunnelSetupResponse(
            status=result["status"],
            public_url=result["public_url"],
            provider=result["provider"],
            install_urls=result["install_urls"],
            remote_client_installation=RemoteClientInstallation(**result["remote_client_installation"])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", 
            response_model=TunnelStatusResponse,
            summary="Get Tunnel Status",
            description="Check the current status of the tunnel connection, including uptime and remote installation commands.",
            tags=["tunnel"])
async def get_tunnel_status(
    tunnel_use_case: TunnelSetupUseCase = Depends(get_tunnel_setup_use_case)
):
    """Get current tunnel status"""
    try:
        status = await tunnel_use_case.get_tunnel_status()
        
        return TunnelStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))