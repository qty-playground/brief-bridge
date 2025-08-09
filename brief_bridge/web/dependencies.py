from brief_bridge.repositories.client_repository import ClientRepository, FileBasedClientRepository
from brief_bridge.repositories.command_repository import CommandRepository, FileBasedCommandRepository
from brief_bridge.use_cases.register_client_use_case import RegisterClientUseCase
from brief_bridge.use_cases.submit_command_use_case import SubmitCommandUseCase
from fastapi import Depends

# File-based repository instances for persistent storage
_client_repository_instance: ClientRepository = FileBasedClientRepository()
_command_repository_instance: CommandRepository = FileBasedCommandRepository()


def get_client_repository() -> ClientRepository:
    """FastAPI dependency: File-based client repository"""
    return _client_repository_instance


def get_command_repository() -> CommandRepository:
    """FastAPI dependency: File-based command repository"""
    return _command_repository_instance


def get_register_client_use_case(
    client_repository: ClientRepository = Depends(get_client_repository)
) -> RegisterClientUseCase:
    """FastAPI dependency: Register client use case with repository injection"""
    return RegisterClientUseCase(client_repository)


def get_submit_command_use_case(
    client_repository: ClientRepository = Depends(get_client_repository),
    command_repository: CommandRepository = Depends(get_command_repository)
) -> SubmitCommandUseCase:
    """FastAPI dependency: Submit command use case with repository injection"""
    return SubmitCommandUseCase(client_repository, command_repository)# Force reload
# Force reload test
