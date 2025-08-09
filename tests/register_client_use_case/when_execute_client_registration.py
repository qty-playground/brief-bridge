"""When I execute client registration - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json
import asyncio

# Simplified Architecture imports
from brief_bridge.use_cases.register_client_use_case import RegisterClientUseCase, ClientRegistrationRequest
from brief_bridge.repositories.client_repository import ClientRepository, InMemoryClientRepository

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute client registration through use case layer
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.WHEN
    # Can access input state from GIVEN phase, collect results here
    
    request_data = json.loads(ctx.request_body)
    
    # Create request object
    registration_request = ClientRegistrationRequest(
        client_id=request_data["client_id"],
        client_name=request_data.get("client_name")
    )
    
    # GREEN Stage 1: Real production invoke chain with hardcoded repository
    repository = InMemoryClientRepository()
    use_case = RegisterClientUseCase(repository)
    ctx.registration_response = asyncio.run(use_case.execute_client_registration(registration_request))