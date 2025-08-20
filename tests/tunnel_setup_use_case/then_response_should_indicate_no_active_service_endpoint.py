"""Then response should indicate no active service endpoint - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify response indicates no active service endpoint
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Assert no active service endpoint
    
    # GREEN Stage 2: Real implementation
    service_endpoint_response = ctx.service_endpoint_response
    
    # Verify response indicates no service endpoint
    assert "service_endpoint" in service_endpoint_response, "Response should contain service_endpoint field"
    
    service_endpoint = service_endpoint_response["service_endpoint"]
    assert service_endpoint is None, f"Service endpoint should be null when no tunnel configured, got: {service_endpoint}"