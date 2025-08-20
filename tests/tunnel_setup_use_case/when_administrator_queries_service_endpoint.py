"""When administrator queries service endpoint - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import asyncio

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute service endpoint query
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Query service endpoint via use case
    
    # GREEN Stage 1: Use existing tunnel use case if available, otherwise create new one
    from brief_bridge.use_cases.tunnel_setup_use_case import TunnelSetupUseCase
    
    # If we have an existing use case with tunnel setup, use it
    if hasattr(ctx, 'tunnel_use_case') and ctx.tunnel_use_case:
        use_case = ctx.tunnel_use_case
    else:
        use_case = TunnelSetupUseCase()
    
    # Execute service endpoint query
    result = asyncio.run(use_case.get_current_service_endpoint())
    
    ctx.service_endpoint_response = result