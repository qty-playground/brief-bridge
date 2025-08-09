from brief_bridge.repositories.client_repository import ClientRepository, InMemoryClientRepository
from brief_bridge.repositories.command_repository import CommandRepository, InMemoryCommandRepository
from brief_bridge.use_cases.register_client_use_case import RegisterClientUseCase
from brief_bridge.use_cases.submit_command_use_case import SubmitCommandUseCase
from fastapi import Depends


def get_client_repository() -> ClientRepository:
    """FastAPI dependency: Client repository"""
    return InMemoryClientRepository()


def get_command_repository() -> CommandRepository:
    """FastAPI dependency: Command repository"""
    return InMemoryCommandRepository()


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
    return SubmitCommandUseCase(client_repository, command_repository)