"""Then system should use provided URL - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify system is using the custom provided URL
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Assert custom URL is configured
    
    # GREEN Stage 1: Verify custom URL is used
    assert hasattr(ctx, "custom_tunnel_response"), "Custom tunnel response not found"
    response = ctx.custom_tunnel_response
    assert response["public_url"] == "https://brief-bridge.example.com", f"Expected custom URL, got {response['public_url']}"
