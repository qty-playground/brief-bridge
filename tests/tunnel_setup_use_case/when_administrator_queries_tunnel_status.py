"""When administrator queries tunnel status - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute tunnel status query
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Query current tunnel status and collect response
    
    # GREEN Stage 1: Call real tunnel status query
    import asyncio
    
    # Use existing tunnel use case to query status
    status_response = asyncio.run(ctx.tunnel_use_case.get_tunnel_status())
    
    # Store status response for verification
    ctx.tunnel_status_response = status_response
