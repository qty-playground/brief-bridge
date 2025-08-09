from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


@dataclass
class Command:
    command_id: str
    target_client_id: str
    content: str
    type: str = "shell"
    status: str = "pending"
    created_at: Optional[datetime] = None
    
    @classmethod
    def create_new_command(cls, target_client_id: str, content: str, command_type: str = "shell") -> "Command":
        """Business rule: command.unique_id - create new command with generated unique ID"""
        return cls(
            command_id=str(uuid.uuid4()),
            target_client_id=target_client_id,
            content=content,
            type=command_type,
            status="pending",
            created_at=datetime.utcnow()
        )
    
    def is_pending(self) -> bool:
        """Business rule: command.pending_state - check if command is waiting for execution"""
        return self.status == "pending"
    
    def to_api_response(self) -> Dict[str, Any]:
        """Convert command to API response format"""
        return {
            "command_id": self.command_id,
            "target_client_id": self.target_client_id,
            "content": self.content,
            "type": self.type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }