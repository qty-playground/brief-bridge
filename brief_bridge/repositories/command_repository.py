from abc import ABC, abstractmethod
from typing import Optional, List
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