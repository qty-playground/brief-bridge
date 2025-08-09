from conftest import ScenarioContext, BDDPhase


def invoke(ctx: ScenarioContext) -> None:
    """Verify command submission failed due to timeout"""
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # Verify response indicates timeout failure
    assert ctx.submission_response is not None, "Should have submission response"
    assert ctx.submission_response.submission_successful is False, "Command submission should have failed due to timeout"
    
    # Verify timeout-specific message
    assert "timeout" in ctx.submission_response.submission_message.lower(), f"Expected timeout message, got: {ctx.submission_response.submission_message}"