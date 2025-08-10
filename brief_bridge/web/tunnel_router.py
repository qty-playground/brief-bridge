"""Tunnel management router for Web API"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..use_cases.tunnel_setup_use_case import TunnelSetupUseCase
from .dependencies import get_tunnel_setup_use_case

router = APIRouter(prefix="/tunnel", tags=["tunnel"])


class TunnelSetupRequest(BaseModel):
    """Request schema for tunnel setup"""
    provider: str
    auth_token: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class RemoteClientInstallation(BaseModel):
    """Schema for remote client installation commands"""
    instructions: str
    commands: Dict[str, str]
    powershell_direct: str
    bash_direct: str


class TunnelSetupResponse(BaseModel):
    """Response schema for tunnel setup"""
    status: str
    public_url: str
    provider: str
    install_urls: Dict[str, str]
    remote_client_installation: RemoteClientInstallation


class TunnelStatusResponse(BaseModel):
    """Response schema for tunnel status"""
    active: bool
    provider: Optional[str] = None
    public_url: Optional[str] = None
    uptime: Optional[int] = None
    connections: Optional[int] = None
    install_commands: Optional[Dict[str, str]] = None


@router.post("/setup", response_model=TunnelSetupResponse)
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


@router.get("/status", response_model=TunnelStatusResponse)
async def get_tunnel_status(
    tunnel_use_case: TunnelSetupUseCase = Depends(get_tunnel_setup_use_case)
):
    """Get current tunnel status"""
    try:
        status = await tunnel_use_case.get_tunnel_status()
        
        return TunnelStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))