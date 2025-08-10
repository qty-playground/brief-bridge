"""Tunnel management router for Web API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..use_cases.tunnel_setup_use_case import TunnelSetupUseCase

router = APIRouter(prefix="/tunnel", tags=["tunnel"])

# Global tunnel use case instance for simplicity in GREEN Stage 1
tunnel_use_case = TunnelSetupUseCase()


class TunnelSetupRequest(BaseModel):
    """Request schema for tunnel setup"""
    provider: str
    auth_token: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class TunnelSetupResponse(BaseModel):
    """Response schema for tunnel setup"""
    status: str
    public_url: str
    provider: str
    install_urls: Dict[str, str]


class TunnelStatusResponse(BaseModel):
    """Response schema for tunnel status"""
    active: bool
    provider: Optional[str] = None
    public_url: Optional[str] = None
    uptime: Optional[int] = None
    connections: Optional[int] = None
    install_commands: Optional[Dict[str, str]] = None


@router.post("/setup", response_model=TunnelSetupResponse)
async def setup_tunnel(request: TunnelSetupRequest):
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
            install_urls=result["install_urls"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=TunnelStatusResponse)
async def get_tunnel_status():
    """Get current tunnel status"""
    try:
        status = await tunnel_use_case.get_tunnel_status()
        
        return TunnelStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))