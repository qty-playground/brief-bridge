"""Tunnel setup use case for managing tunnel connections"""
from typing import Dict, Any
from datetime import datetime
from ..entities.tunnel import Tunnel


class TunnelSetupUseCase:
    """Use case for setting up tunnel connections"""
    
    def __init__(self):
        self.active_tunnel = None
        
    async def setup_tunnel(self, provider: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Set up a tunnel with specified provider"""
        # GREEN Stage 1: Hardcoded implementation
        public_url = "https://abc123.ngrok.io"  # Hardcoded for now
        
        tunnel = Tunnel(
            tunnel_id="tunnel-123",
            provider=provider,
            public_url=public_url,
            config=config,
            created_at=datetime.now()
        )
        tunnel.activate()
        
        self.active_tunnel = tunnel
        
        return {
            "status": "active",
            "public_url": public_url,
            "provider": provider,
            "install_urls": tunnel.get_install_urls()
        }
        
    async def get_tunnel_status(self) -> Dict[str, Any]:
        """Get current tunnel status"""
        if not self.active_tunnel:
            return {
                "active": False,
                "provider": None,
                "public_url": None
            }
            
        return {
            "active": True,
            "provider": self.active_tunnel.provider,
            "public_url": self.active_tunnel.public_url,
            "uptime": 3600,  # Hardcoded
            "connections": 5,  # Hardcoded
            "install_commands": self.active_tunnel.get_install_commands()
        }