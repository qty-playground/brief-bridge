"""Given offline threshold is set for testing - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.configurable_timeout - setup test threshold
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain with hardcoded behavior
    ctx.offline_threshold_seconds = ctx.threshold_seconds