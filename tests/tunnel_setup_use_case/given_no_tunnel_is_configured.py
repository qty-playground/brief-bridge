"""Given no tunnel is configured - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Ensure no tunnel is currently configured
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Set up scenario where no tunnel is active
    
    # GREEN Stage 1: No tunnel setup needed - this is the default state
    # Just ensure context is clean
    ctx.tunnel_response = None
    ctx.custom_tunnel_response = None