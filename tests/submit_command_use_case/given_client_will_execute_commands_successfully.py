from conftest import ScenarioContext, BDDPhase


def invoke(ctx: ScenarioContext) -> None:
    """Mark that client will execute commands successfully"""
    # Hardcoded for GREEN Stage 1 - just mark the expectation
    ctx.client_execution_success = True
    ctx.expected_result = "Hello from AI"  # Expected output for our test command