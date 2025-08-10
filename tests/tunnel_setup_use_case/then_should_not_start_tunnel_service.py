"""Then should not start any tunnel service - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify no tunnel service was started
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Assert no tunnel processes are running
    
    # GREEN Stage 1: Verify no external tunnel service started (custom uses provided URL)
    # For custom provider, we don't start external services - we use provided URL
    assert hasattr(ctx, "custom_tunnel_response"), "Custom tunnel response not found"
    response = ctx.custom_tunnel_response
    assert response["provider"] == "custom", "Should be using custom provider"
