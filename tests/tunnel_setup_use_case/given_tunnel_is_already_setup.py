"""Given tunnel is already setup and running - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: tunnel.status - establish existing tunnel state
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Setup test environment with active tunnel
    
    # GREEN Stage 1: Create and store existing tunnel via use case
    from brief_bridge.use_cases.tunnel_setup_use_case import TunnelSetupUseCase
    import asyncio
    
    # Create tunnel use case and set up a tunnel
    use_case = TunnelSetupUseCase()
    tunnel_response = asyncio.run(use_case.setup_tunnel("ngrok", {"auth_token": "test-token"}))
    
    # Store use case instance for later status query
    ctx.tunnel_use_case = use_case
    ctx.existing_tunnel_response = tunnel_response
