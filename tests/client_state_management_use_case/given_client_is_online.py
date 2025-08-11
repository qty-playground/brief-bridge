"""Given client is online - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.status_online - setup online client
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Online client setup not implemented")