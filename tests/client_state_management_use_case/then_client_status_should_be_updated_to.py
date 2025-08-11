"""Then client status should be updated to - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext, expected_status: str) -> None:
    """
    Verify client status has been updated to new value
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production verification
    assert hasattr(ctx, 'updated_client'), "Client should have been updated"
    assert ctx.updated_client.status == expected_status, f"Client status should be updated to {expected_status} but was {ctx.updated_client.status}"