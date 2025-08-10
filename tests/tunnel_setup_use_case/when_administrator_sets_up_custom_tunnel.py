"""When administrator sets up custom tunnel - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json

def invoke(ctx: ScenarioContext, request_body: str) -> None:
    """
    Execute custom tunnel configuration
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Parse custom tunnel config and apply
    
    # GREEN Stage 1: Call real production code for custom tunnel
    from brief_bridge.use_cases.tunnel_setup_use_case import TunnelSetupUseCase
    import json
    import asyncio
    
    request_data = json.loads(request_body)
    use_case = TunnelSetupUseCase()
    
    # Execute custom tunnel setup
    result = asyncio.run(use_case.setup_tunnel(
        provider=request_data["provider"],
        config=request_data
    ))
    
    ctx.custom_tunnel_response = result
