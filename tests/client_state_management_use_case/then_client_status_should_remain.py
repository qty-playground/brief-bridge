"""Then client status should remain unchanged - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext, expected_status: str) -> None:
    """
    Verify client status has not changed from expected value
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production verification with hardcoded expectations
    assert hasattr(ctx, 'updated_client'), "Client should have been updated"
    assert ctx.updated_client.status == expected_status, f"Client status should remain {expected_status} but was {ctx.updated_client.status}"