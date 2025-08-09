"""Given client is registered in system - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

# Simplified Architecture imports  
from brief_bridge.entities.client import Client
from brief_bridge.repositories.client_repository import InMemoryClientRepository

def invoke(ctx: ScenarioContext, client_id: str) -> None:
    """
    Business rule: client.registration - setup test client in repository
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.GIVEN
    # Set up input state for scenario execution
    
    # GREEN Stage 1: Setup test client in repository
    import asyncio
    
    # Create a test client
    client = Client.register_new_client(client_id=client_id, name=f"Test Client {client_id}")
    
    # Store in repository for use in test
    test_repository = InMemoryClientRepository()
    asyncio.run(test_repository.save_registered_client(client))
    
    # Store repository in context for WHEN phase
    ctx.test_client_repository = test_repository