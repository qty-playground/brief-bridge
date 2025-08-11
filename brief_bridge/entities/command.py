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
    status: str = "pending"  # pending → processing → completed/failed
    # encoding removed - no longer supporting base64
    created_at: Optional[datetime] = None
    
    # New fields for result handling
    started_at: Optional[datetime] = None    # When execution started
    completed_at: Optional[datetime] = None  # When execution completed
    result: Optional[str] = None            # Execution output
    error: Optional[str] = None             # Error message
    execution_time: Optional[float] = None  # Execution time in seconds
    
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
    
    def mark_as_processing(self) -> None:
        """Business rule: command.status_flow - mark command as being executed"""
        self.status = "processing"
        self.started_at = datetime.utcnow()
    
    def mark_as_completed(self, result: str, execution_time: float) -> None:
        """Business rule: command.result_capture - mark command as completed with results"""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.result = result
        self.execution_time = execution_time
    
    def mark_as_failed(self, error: str, execution_time: float = 0.0) -> None:
        """Business rule: command.result_capture - mark command as failed with error"""
        self.status = "failed"
        self.completed_at = datetime.utcnow()
        self.error = error
        self.execution_time = execution_time
    
    def is_completed(self) -> bool:
        """Check if command execution is finished (success or failure)"""
        return self.status in ["completed", "failed"]
    
    def to_api_response(self) -> Dict[str, Any]:
        """Convert command to API response format"""
        response = {
            "command_id": self.command_id,
            "target_client_id": self.target_client_id,
            "content": self.content,
            "type": self.type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time
        }
        if self.encoding:
            response["encoding"] = self.encoding
        return response