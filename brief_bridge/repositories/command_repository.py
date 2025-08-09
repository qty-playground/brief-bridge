from abc import ABC, abstractmethod
from typing import Optional, List
import json
import os
from pathlib import Path
import asyncio
from datetime import datetime
from brief_bridge.entities.command import Command


class CommandRepository(ABC):
    @abstractmethod
    async def save_command(self, command: Command) -> Command:
        """Business rule: command.persistence - store command for execution"""
        pass
    
    @abstractmethod
    async def find_command_by_id(self, command_id: str) -> Optional[Command]:
        """Business rule: command.lookup - retrieve command by unique identifier"""
        pass
    
    @abstractmethod
    async def get_pending_commands_for_client(self, client_id: str) -> List[Command]:
        """Business rule: command.dispatch - get commands waiting for client execution"""
        pass
    
    @abstractmethod
    async def get_all_commands(self) -> List[Command]:
        """Business rule: command.listing - retrieve all commands"""
        pass
    
    @abstractmethod
    async def find_commands_by_client_id(self, client_id: str) -> List[Command]:
        """Business rule: command.client_filtering - retrieve all commands for specific client"""
        pass


class InMemoryCommandRepository(CommandRepository):
    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}
    
    async def save_command(self, command: Command) -> Command:
        """Business rule: command.persistence - store command in memory"""
        self._commands[command.command_id] = command
        return command
    
    async def find_command_by_id(self, command_id: str) -> Optional[Command]:
        """Business rule: command.lookup - find command by ID from memory store"""
        return self._commands.get(command_id)
    
    async def get_pending_commands_for_client(self, client_id: str) -> List[Command]:
        """Business rule: command.dispatch - filter pending commands for specific client"""
        return [
            cmd for cmd in self._commands.values()
            if cmd.target_client_id == client_id and cmd.status == "pending"
        ]
    
    async def get_all_commands(self) -> List[Command]:
        """Business rule: command.listing - return all commands from memory store"""
        return list(self._commands.values())
    
    async def find_commands_by_client_id(self, client_id: str) -> List[Command]:
        """Business rule: command.client_filtering - filter all commands for specific client"""
        return [
            cmd for cmd in self._commands.values()
            if cmd.target_client_id == client_id
        ]


class FileBasedCommandRepository(CommandRepository):
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.commands_file = self.data_dir / "commands.json"
        self._lock = asyncio.Lock()
    
    async def _load_commands(self) -> dict[str, dict]:
        """Load commands from JSON file"""
        if not self.commands_file.exists():
            return {}
        
        try:
            with open(self.commands_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load commands file: {e}")
            return {}
    
    async def _save_commands(self, commands_data: dict[str, dict]) -> None:
        """Save commands to JSON file"""
        try:
            # Atomic write: write to temp file first, then rename
            temp_file = self.commands_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(commands_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Atomic rename
            temp_file.replace(self.commands_file)
        except OSError as e:
            print(f"Error: Failed to save commands file: {e}")
            raise
    
    def _dict_to_command(self, command_data: dict) -> Command:
        """Convert dictionary to Command object"""
        # Parse created_at if it exists
        created_at = None
        if command_data.get("created_at"):
            try:
                # Try parsing ISO format datetime string
                created_at = datetime.fromisoformat(command_data["created_at"].replace('Z', '+00:00'))
            except ValueError:
                # Fallback to string format
                created_at = command_data.get("created_at")
        
        # Reconstruct Command object manually (since we need to preserve existing data)
        command = Command.create_new_command(
            target_client_id=command_data["target_client_id"],
            content=command_data["content"],
            command_type=command_data.get("type", "shell")
        )
        
        # Override with stored values
        command.command_id = command_data["command_id"]
        command.status = command_data.get("status", "pending")
        if created_at:
            command.created_at = created_at
        
        return command
    
    def _command_to_dict(self, command: Command) -> dict:
        """Convert Command object to dictionary"""
        return {
            "command_id": command.command_id,
            "target_client_id": command.target_client_id,
            "content": command.content,
            "type": command.type,
            "status": command.status,
            "created_at": command.created_at.isoformat() if command.created_at else None
        }
    
    async def save_command(self, command: Command) -> Command:
        """Business rule: command.persistence - persist command to file"""
        async with self._lock:
            commands_data = await self._load_commands()
            commands_data[command.command_id] = self._command_to_dict(command)
            await self._save_commands(commands_data)
            return command
    
    async def find_command_by_id(self, command_id: str) -> Optional[Command]:
        """Business rule: command.lookup - find command by ID from file store"""
        async with self._lock:
            commands_data = await self._load_commands()
            command_dict = commands_data.get(command_id)
            if command_dict:
                return self._dict_to_command(command_dict)
            return None
    
    async def get_pending_commands_for_client(self, client_id: str) -> List[Command]:
        """Business rule: command.dispatch - filter pending commands for specific client from file"""
        async with self._lock:
            commands_data = await self._load_commands()
            commands = [self._dict_to_command(data) for data in commands_data.values()]
            return [
                cmd for cmd in commands
                if cmd.target_client_id == client_id and cmd.status == "pending"
            ]
    
    async def get_all_commands(self) -> List[Command]:
        """Business rule: command.listing - return all commands from file store"""
        async with self._lock:
            commands_data = await self._load_commands()
            return [self._dict_to_command(data) for data in commands_data.values()]
    
    async def find_commands_by_client_id(self, client_id: str) -> List[Command]:
        """Business rule: command.client_filtering - filter all commands for specific client from file"""
        async with self._lock:
            commands_data = await self._load_commands()
            commands = [self._dict_to_command(data) for data in commands_data.values()]
            return [
                cmd for cmd in commands
                if cmd.target_client_id == client_id
            ]