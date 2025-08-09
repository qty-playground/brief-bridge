from dataclasses import dataclass
from typing import Optional
from brief_bridge.entities.client import Client
from brief_bridge.repositories.client_repository import ClientRepository


@dataclass
class ClientRegistrationRequest:
    client_id: str
    client_name: Optional[str] = None


@dataclass
class ClientRegistrationResponse:
    client_id: str
    client_name: Optional[str]
    client_status: str
    registration_successful: bool = True
    registration_message: str = "Client registered successfully"


class RegisterClientUseCase:
    def __init__(self, client_repository: ClientRepository) -> None:
        self._client_repository = client_repository
    
    async def execute_client_registration(self, request: ClientRegistrationRequest) -> ClientRegistrationResponse:
        """Business rule: client.registration - register new client in system"""
        client: Client = Client.register_new_client(
            client_id=request.client_id,
            name=request.client_name
        )
        
        registered_client: Client = await self._client_repository.save_registered_client(client)
        
        return ClientRegistrationResponse(
            client_id=registered_client.client_id,
            client_name=registered_client.name,
            client_status=registered_client.status,
            registration_successful=True,
            registration_message="Client registered successfully"
        )