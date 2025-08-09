"""Then client should be saved in repository - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json

# Simplified Architecture imports
from brief_bridge.repositories.client_repository import ClientRepository

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify client was properly saved in repository
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # Get expected data from cross-phase storage
    expected_client_data_str = ctx.get_cross_phase_data('expected_client_data')
    if not expected_client_data_str:
        raise ValueError("Expected client data not provided")
    
    expected_client_data = json.loads(expected_client_data_str)
    
    # GREEN Stage 2: Real business rule verification - client.registration 
    # Business rule: registered client should be saved with correct attributes
    client_id = expected_client_data["client_id"]
    
    # Verify client exists in repository
    import asyncio
    saved_client = asyncio.run(ctx.test_repository.find_client_by_id(client_id))
    assert saved_client is not None, f"Client {client_id} should be saved in repository but not found"
    
    # Verify saved client matches expected attributes
    assert saved_client.client_id == expected_client_data["client_id"], f"Expected client_id {expected_client_data['client_id']}, got {saved_client.client_id}"
    assert saved_client.name == expected_client_data["name"], f"Expected name {expected_client_data['name']}, got {saved_client.name}"
    assert saved_client.status == expected_client_data["status"], f"Expected status {expected_client_data['status']}, got {saved_client.status}"