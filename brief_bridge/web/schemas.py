from pydantic import BaseModel, Field
from typing import Optional


class RegisterClientRequestSchema(BaseModel):
    client_id: str
    name: Optional[str] = None


class RegisterClientResponseSchema(BaseModel):
    client_id: str
    name: Optional[str]
    status: str
    success: bool = True
    message: str = "Client registered successfully"


class ClientSchema(BaseModel):
    client_id: str
    name: Optional[str]
    status: str
    last_seen: Optional[str] = None


class SubmitCommandRequestSchema(BaseModel):
    target_client_id: str = Field(..., description="ID of the target client to execute the command")
    command_content: str = Field(..., description="Command content to execute", json_schema_extra={"examples": ["echo 'Hello World'", "Get-Process | Where-Object Name -like 'powershell*'"]})
    command_type: str = Field(default="shell", description="Type of command to execute", json_schema_extra={"examples": ["shell", "powershell"]})


class SubmitCommandResponseSchema(BaseModel):
    command_id: Optional[str]
    target_client_id: str
    submission_successful: bool
    submission_message: str
    # New fields for execution results
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class CommandSchema(BaseModel):
    command_id: str
    target_client_id: str
    content: str = Field(..., description="Command content")
    type: str
    status: str
    created_at: Optional[str] = None
    # New fields for execution results
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class SubmitResultRequestSchema(BaseModel):
    command_id: str
    success: bool = True
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class SubmitResultResponseSchema(BaseModel):
    status: str = "success"
    message: str = "Result received successfully"