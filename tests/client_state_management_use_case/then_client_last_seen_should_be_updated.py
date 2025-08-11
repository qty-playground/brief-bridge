"""Then client last_seen should be updated - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from datetime import datetime, timezone

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify client activity timestamp was updated to current time
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # GREEN Stage 1: Production verification with hardcoded expectations
    assert hasattr(ctx, 'updated_client'), "Client should have been updated by polling"
    assert ctx.updated_client.last_seen is not None, "Client last_seen should not be None"
    
    # Verify timestamp is recent (within last few seconds)
    current_time = datetime.now(timezone.utc)
    time_diff = (current_time - ctx.updated_client.last_seen).total_seconds()
    assert time_diff < 5, f"last_seen should be recent, but was {time_diff} seconds ago"