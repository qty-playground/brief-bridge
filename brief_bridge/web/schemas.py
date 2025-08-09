from pydantic import BaseModel
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


class SubmitCommandRequestSchema(BaseModel):
    target_client_id: str
    command_content: str
    command_type: str = "shell"


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
    content: str
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
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class SubmitResultResponseSchema(BaseModel):
    status: str = "success"
    message: str = "Result received successfully"