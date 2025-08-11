from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timezone


@dataclass
class Client:
    client_id: str
    name: Optional[str] = None
    status: str = "online"
    last_seen: Optional[datetime] = None
    
    @classmethod
    def register_new_client(cls, client_id: str, name: Optional[str] = None) -> "Client":
        """Business rule: client.registration - create new client with online status"""
        return cls(
            client_id=client_id, 
            name=name, 
            status="online", 
            last_seen=cls._current_utc_time()
        )
    
    def update_activity(self) -> None:
        """Business rule: client.activity_tracking - update client last activity timestamp"""
        self.last_seen = self._current_utc_time()
    
    @staticmethod
    def _current_utc_time() -> datetime:
        """Extract current UTC time for testability and consistency"""
        return datetime.now(timezone.utc)
    
    def is_online(self) -> bool:
        """Business rule: client.availability - check if client is available for commands"""
        return self.status == "online"
    
    def to_api_response(self) -> Dict[str, Any]:
        """Convert client to API response format"""
        return {
            "client_id": self.client_id,
            "name": self.name,
            "status": self.status,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None
        }