"""Tunnel entity for tunnel management"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Tunnel:
    """Tunnel entity representing a tunnel connection"""
    tunnel_id: str
    provider: str
    public_url: str
    status: str = "inactive"
    config: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    uptime: Optional[int] = None
    connections: Optional[int] = None
    
    def activate(self):
        """Activate the tunnel"""
        self.status = "active"
        
    def deactivate(self):
        """Deactivate the tunnel"""
        self.status = "inactive"
        
    def get_install_urls(self) -> Dict[str, str]:
        """Get install URLs for different platforms"""
        return {
            "powershell": f"{self.public_url}/install.ps1",
            "bash": f"{self.public_url}/install.sh"
        }
        
    def get_install_commands(self) -> Dict[str, str]:
        """Get install commands for different platforms"""
        return {
            "windows": f"iex ((Invoke-WebRequest '{self.public_url}/install.ps1').Content)",
            "linux": f"curl -sSL {self.public_url}/install.sh | bash"
        }