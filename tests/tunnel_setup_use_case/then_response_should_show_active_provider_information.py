"""Then response should show active provider information - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify response shows active provider information
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Assert provider information is present
    
    # GREEN Stage 2: Real implementation
    service_endpoint_response = ctx.service_endpoint_response
    
    # Verify response has provider information
    assert "provider" in service_endpoint_response, "Response should contain provider field"
    assert "status" in service_endpoint_response, "Response should contain status field"
    
    provider = service_endpoint_response["provider"]
    status = service_endpoint_response["status"]
    
    assert provider is not None, "Provider should not be null when tunnel is active"
    assert provider in ["ngrok", "custom"], f"Provider should be valid type, got: {provider}"
    assert status == "active", f"Status should be active when tunnel is running, got: {status}"