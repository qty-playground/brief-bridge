from abc import ABC, abstractmethod
from typing import Optional, List
import json
import os
from pathlib import Path
import asyncio
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


class FileBasedClientRepository(ClientRepository):
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.clients_file = self.data_dir / "clients.json"
        self._lock = asyncio.Lock()
    
    async def _load_clients(self) -> dict[str, dict]:
        """Load clients from JSON file"""
        if not self.clients_file.exists():
            return {}
        
        try:
            with open(self.clients_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load clients file: {e}")
            return {}
    
    async def _save_clients(self, clients_data: dict[str, dict]) -> None:
        """Save clients to JSON file"""
        try:
            # Atomic write: write to temp file first, then rename
            temp_file = self.clients_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(clients_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_file.replace(self.clients_file)
        except OSError as e:
            print(f"Error: Failed to save clients file: {e}")
            raise
    
    def _dict_to_client(self, client_data: dict) -> Client:
        """Convert dictionary to Client object"""
        # Use Client.register_new_client factory method to maintain business rules
        return Client.register_new_client(
            client_id=client_data["client_id"],
            name=client_data.get("name")
        )
    
    def _client_to_dict(self, client: Client) -> dict:
        """Convert Client object to dictionary"""
        return {
            "client_id": client.client_id,
            "name": client.name,
            "status": client.status
        }
    
    async def save_registered_client(self, client: Client) -> Client:
        """Business rule: client.registration - persist client to file"""
        async with self._lock:
            clients_data = await self._load_clients()
            clients_data[client.client_id] = self._client_to_dict(client)
            await self._save_clients(clients_data)
            return client
    
    async def find_client_by_id(self, client_id: str) -> Optional[Client]:
        """Business rule: client.lookup - find client by ID from file store"""
        async with self._lock:
            clients_data = await self._load_clients()
            client_dict = clients_data.get(client_id)
            if client_dict:
                return self._dict_to_client(client_dict)
            return None
    
    async def get_all_registered_clients(self) -> List[Client]:
        """Business rule: client.listing - return all clients from file store"""
        async with self._lock:
            clients_data = await self._load_clients()
            return [self._dict_to_client(data) for data in clients_data.values()]