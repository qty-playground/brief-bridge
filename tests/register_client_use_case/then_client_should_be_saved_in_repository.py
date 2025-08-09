"""Then client should be saved in repository - Screaming Architecture naming"""
import asyncio
import json
from conftest import ScenarioContext, BDDPhase

# Simplified Architecture imports
from brief_bridge.repositories.client_repository import ClientRepository

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify client was properly saved in repository
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    expected_client_data = _get_expected_client_data(ctx)
    saved_client = _get_saved_client_from_repository(ctx, expected_client_data["client_id"])
    _verify_client_attributes_match(saved_client, expected_client_data)

def _get_expected_client_data(ctx: ScenarioContext) -> dict:
    """Extract and parse expected client data from cross-phase storage"""
    expected_client_data_str = ctx.get_cross_phase_data('expected_client_data')
    if not expected_client_data_str:
        raise ValueError("Expected client data not provided")
    return json.loads(expected_client_data_str)

def _get_saved_client_from_repository(ctx: ScenarioContext, client_id: str):
    """Retrieve saved client from repository and verify existence"""
    saved_client = asyncio.run(ctx.test_repository.find_client_by_id(client_id))
    assert saved_client is not None, f"Client {client_id} should be saved in repository but not found"
    return saved_client

def _verify_client_attributes_match(saved_client, expected_client_data: dict) -> None:
    """Verify saved client attributes match expected values - Business rule: client.registration"""
    attribute_checks = [
        ("client_id", saved_client.client_id, expected_client_data["client_id"]),
        ("name", saved_client.name, expected_client_data["name"]),
        ("status", saved_client.status, expected_client_data["status"])
    ]
    
    for attr_name, actual_value, expected_value in attribute_checks:
        assert actual_value == expected_value, f"Expected {attr_name} {expected_value}, got {actual_value}"