from brief_bridge.repositories.client_repository import ClientRepository, InMemoryClientRepository
from brief_bridge.use_cases.register_client_use_case import RegisterClientUseCase
from fastapi import Depends


def get_client_repository() -> ClientRepository:
    """FastAPI dependency: Client repository"""
    return InMemoryClientRepository()


def get_register_client_use_case(
    client_repository: ClientRepository = Depends(get_client_repository)
) -> RegisterClientUseCase:
    """FastAPI dependency: Register client use case with repository injection"""
    return RegisterClientUseCase(client_repository)