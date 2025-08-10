"""Tunnel setup use case for managing tunnel connections"""
from typing import Dict, Any
from datetime import datetime
import uuid
from ..entities.tunnel import Tunnel


class TunnelSetupUseCase:
    """Use case for setting up tunnel connections"""
    
    def __init__(self):
        self.active_tunnel = None
        
    async def setup_tunnel(self, provider: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Set up a tunnel with specified provider"""
        config = config or {}
        
        # Business rule: tunnel.setup - deactivate existing tunnel
        self._deactivate_existing_tunnel()
        
        # Business rule: tunnel.provider_validation - validate provider
        self._validate_provider(provider)
        
        # Business rule: tunnel.url_generation - generate URL based on provider
        public_url = self._generate_public_url(provider, config)
        
        # Business rule: tunnel.lifecycle - create and activate tunnel
        tunnel = self._create_and_activate_tunnel(provider, public_url, config)
        
        self.active_tunnel = tunnel
        
        # Business rule: tunnel.response - return structured tunnel information
        return self._build_setup_response(tunnel)
    
    def _deactivate_existing_tunnel(self) -> None:
        """Deactivate existing tunnel before setting up new one"""
        if self.active_tunnel:
            self.active_tunnel.deactivate()
    
    def _validate_provider(self, provider: str) -> None:
        """Validate that the provider is supported"""
        supported_providers = ["ngrok"]
        if provider not in supported_providers:
            raise ValueError(f"Unsupported provider: {provider}. Supported: {supported_providers}")
    
    def _generate_public_url(self, provider: str, config: Dict[str, Any]) -> str:
        """Generate public URL based on provider type"""
        if provider == "ngrok":
            return self._generate_ngrok_url()
        else:
            raise ValueError(f"URL generation not implemented for provider: {provider}")
    
    def _generate_ngrok_url(self) -> str:
        """Generate ngrok tunnel URL"""
        subdomain = str(uuid.uuid4())[:8]
        return f"https://{subdomain}.ngrok.io"
    
    
    def _create_and_activate_tunnel(self, provider: str, public_url: str, config: Dict[str, Any]) -> Tunnel:
        """Create new tunnel and activate it"""
        tunnel_id = f"tunnel-{str(uuid.uuid4())[:8]}"
        tunnel = Tunnel(
            tunnel_id=tunnel_id,
            provider=provider,
            public_url=public_url,
            config=config,
            created_at=datetime.now()
        )
        tunnel.activate()
        return tunnel
    
    def _build_setup_response(self, tunnel: Tunnel) -> Dict[str, Any]:
        """Build standardized tunnel setup response"""
        return {
            "status": tunnel.status,
            "public_url": tunnel.public_url,
            "provider": tunnel.provider,
            "install_urls": tunnel.get_install_urls()
        }
        
    async def get_tunnel_status(self) -> Dict[str, Any]:
        """Get current tunnel status"""
        # Business rule: tunnel.status - return inactive status if no tunnel exists
        if not self.active_tunnel:
            return self._build_inactive_status_response()
        
        # Business rule: tunnel.status - check if tunnel is currently active
        if not self._is_tunnel_active():
            return self._build_inactive_status_response(self.active_tunnel.provider)
        
        # Business rule: tunnel.monitoring - build active status with metrics
        return self._build_active_status_response()
    
    def _build_inactive_status_response(self, provider: str = None) -> Dict[str, Any]:
        """Build response for inactive tunnel status"""
        return {
            "active": False,
            "provider": provider,
            "public_url": None
        }
    
    def _is_tunnel_active(self) -> bool:
        """Check if the current tunnel is active"""
        return self.active_tunnel.status == "active"
    
    def _build_active_status_response(self) -> Dict[str, Any]:
        """Build response for active tunnel with monitoring data"""
        uptime_seconds = self._calculate_tunnel_uptime()
        
        return {
            "active": True,
            "provider": self.active_tunnel.provider,
            "public_url": self.active_tunnel.public_url,
            "uptime": uptime_seconds,
            "connections": 5,  # Would be tracked in real implementation
            "install_commands": self.active_tunnel.get_install_commands()
        }
    
    def _calculate_tunnel_uptime(self) -> int:
        """Calculate tunnel uptime in seconds"""
        if not self.active_tunnel.created_at:
            return 0
        return int((datetime.now() - self.active_tunnel.created_at).total_seconds())