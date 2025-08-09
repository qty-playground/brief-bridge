from conftest import ScenarioContext, BDDPhase


def invoke(ctx: ScenarioContext) -> None:
    """Verify that both commands executed independently without interference"""
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # Verify we have responses for both commands
    assert 'multi_command_responses' in ctx._results, "Should have multi-command responses"
    responses = ctx._results['multi_command_responses']
    assert len(responses) == 2, f"Expected 2 responses, got {len(responses)}"
    
    # Verify both commands were successful
    for i, response in enumerate(responses):
        assert response.submission_successful is True, f"Command {i+1} should have been successful: {response.submission_message}"
        assert response.command_id is not None, f"Command {i+1} should have command_id"
        assert response.result is not None, f"Command {i+1} should have execution result"
    
    # Verify commands have different results (proving they executed independently)
    results = [response.result for response in responses]
    assert len(set(results)) == len(results), f"Commands should have different results, got: {results}"
    
    # Store individual responses for later verification steps using results storage
    ctx._results['first_command_response'] = responses[0]
    ctx._results['second_command_response'] = responses[1]