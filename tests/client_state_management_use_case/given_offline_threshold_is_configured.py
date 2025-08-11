"""Given offline threshold is configured - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.configurable_timeout - setup production-like threshold
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain
    ctx.offline_threshold_seconds = ctx.threshold_seconds