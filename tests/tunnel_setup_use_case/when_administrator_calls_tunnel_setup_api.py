"""When administrator calls tunnel setup API - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json

def invoke(ctx: ScenarioContext, request_body: str) -> None:
    """
    Execute tunnel setup API request
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Parse request body and execute tunnel setup
    
    # GREEN Stage 1: Call real production code
    from brief_bridge.use_cases.tunnel_setup_use_case import TunnelSetupUseCase
    import json
    import asyncio
    
    request_data = json.loads(request_body)
    use_case = TunnelSetupUseCase()
    
    # Execute tunnel setup through production use case
    result = asyncio.run(use_case.setup_tunnel(
        provider=request_data["provider"],
        config=request_data.get("config", {})
    ))
    
    # Store result for verification
    ctx.tunnel_setup_response = result
