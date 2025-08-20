"""Then response should contain service endpoint URL - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify response contains service endpoint URL
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Assert service endpoint URL is present
    
    # GREEN Stage 2: Real implementation
    service_endpoint_response = ctx.service_endpoint_response
    
    # Verify response has service endpoint URL
    assert "service_endpoint" in service_endpoint_response, "Response should contain service_endpoint field"
    
    service_endpoint = service_endpoint_response["service_endpoint"]
    assert service_endpoint is not None, "Service endpoint should not be null when tunnel is active"
    assert service_endpoint.startswith(("http://", "https://")), f"Service endpoint should be valid URL, got: {service_endpoint}"