"""Then command submission should fail - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify command submission failed appropriately
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # GREEN Stage 1: Simple assertion on production response
    assert ctx.submission_response.submission_successful is False, f"Command submission should fail, but got: {ctx.submission_response.submission_successful}"
    assert ctx.submission_response.command_id is None, "Command ID should not be generated for failed submission"