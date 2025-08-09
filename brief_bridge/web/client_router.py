from fastapi import APIRouter, Depends, HTTPException
from typing import List
from brief_bridge.web.schemas import RegisterClientRequestSchema, RegisterClientResponseSchema, ClientSchema
from brief_bridge.web.dependencies import get_register_client_use_case, get_client_repository
from brief_bridge.use_cases.register_client_use_case import RegisterClientUseCase, ClientRegistrationRequest
from brief_bridge.repositories.client_repository import ClientRepository

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/register", response_model=RegisterClientResponseSchema)
async def register_new_client(
    request: RegisterClientRequestSchema,
    use_case: RegisterClientUseCase = Depends(get_register_client_use_case)
) -> RegisterClientResponseSchema:
    """API endpoint: Register new client in the system"""
    use_case_request: ClientRegistrationRequest = ClientRegistrationRequest(
        client_id=request.client_id,
        client_name=request.name
    )
    
    registration_response = await use_case.execute_client_registration(use_case_request)
    
    return RegisterClientResponseSchema(
        client_id=registration_response.client_id,
        name=registration_response.client_name,
        status=registration_response.client_status,
        success=registration_response.registration_successful,
        message=registration_response.registration_message
    )


@router.get("/{client_id}", response_model=ClientSchema)
async def get_registered_client_by_id(
    client_id: str,
    repository: ClientRepository = Depends(get_client_repository)
) -> ClientSchema:
    """API endpoint: Retrieve specific client by ID"""
    client = await repository.find_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return ClientSchema(
        client_id=client.client_id,
        name=client.name,
        status=client.status
    )


@router.get("/", response_model=List[ClientSchema])
async def get_all_registered_clients(
    repository: ClientRepository = Depends(get_client_repository)
) -> List[ClientSchema]:
    """API endpoint: List all registered clients in the system"""
    registered_clients = await repository.get_all_registered_clients()
    return [
        ClientSchema(
            client_id=client.client_id,
            name=client.name,
            status=client.status
        )
        for client in registered_clients
    ]