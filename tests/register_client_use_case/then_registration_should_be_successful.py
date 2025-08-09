"""Then registration should be successful - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify registration was successful
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # GREEN Stage 1: Simple assertion on production response
    assert ctx.registration_response.registration_successful is True, f"Registration should be successful, but got: {ctx.registration_response.registration_successful}"