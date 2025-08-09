"""Then command submission should be successful - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify command submission was successful
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # GREEN Stage 1: Simple assertion on production response
    assert ctx.submission_response.submission_successful is True, f"Command submission should be successful, but got: {ctx.submission_response.submission_successful}"
    assert ctx.submission_response.command_id is not None, "Command ID should be generated"