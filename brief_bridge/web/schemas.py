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