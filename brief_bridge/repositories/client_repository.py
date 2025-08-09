from abc import ABC, abstractmethod
from typing import Optional, List
from brief_bridge.entities.client import Client


class ClientRepository(ABC):
    @abstractmethod
    async def save_registered_client(self, client: Client) -> Client:
        """Business rule: client.registration - persist newly registered client"""
        pass
    
    @abstractmethod
    async def find_client_by_id(self, client_id: str) -> Optional[Client]:
        """Business rule: client.lookup - retrieve client by unique identifier"""
        pass
    
    @abstractmethod
    async def get_all_registered_clients(self) -> List[Client]:
        """Business rule: client.listing - retrieve all registered clients"""
        pass


class InMemoryClientRepository(ClientRepository):
    def __init__(self) -> None:
        self._registered_clients: dict[str, Client] = {}
    
    async def save_registered_client(self, client: Client) -> Client:
        """Business rule: client.registration - store client in memory"""
        self._registered_clients[client.client_id] = client
        return client
    
    async def find_client_by_id(self, client_id: str) -> Optional[Client]:
        """Business rule: client.lookup - find client by ID from memory store"""
        return self._registered_clients.get(client_id)
    
    async def get_all_registered_clients(self) -> List[Client]:
        """Business rule: client.listing - return all clients from memory store"""
        return list(self._registered_clients.values())