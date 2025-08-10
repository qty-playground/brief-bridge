"""Then system should start specified tunnel service - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify specified tunnel service was started
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Assert tunnel service is active
    
    # GREEN Stage 1: Verify tunnel service started
    assert hasattr(ctx, "tunnel_setup_response"), "Tunnel setup response not found"
    assert ctx.tunnel_setup_response["status"] == "active", f"Expected tunnel status 'active', got {ctx.tunnel_setup_response['status']}"
