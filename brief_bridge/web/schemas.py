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


class CommandSchema(BaseModel):
    command_id: str
    target_client_id: str
    content: str
    type: str
    status: str
    created_at: Optional[str] = None