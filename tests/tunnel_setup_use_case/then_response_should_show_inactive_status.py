"""Then response should show inactive status - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify response shows inactive status
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Assert inactive status
    
    # GREEN Stage 2: Real implementation
    service_endpoint_response = ctx.service_endpoint_response
    
    # Verify response shows inactive status
    assert "status" in service_endpoint_response, "Response should contain status field"
    
    status = service_endpoint_response["status"]
    assert status == "inactive", f"Status should be inactive when no tunnel configured, got: {status}"
    
    # Provider should be null when inactive
    provider = service_endpoint_response.get("provider")
    assert provider is None, f"Provider should be null when inactive, got: {provider}"