"""Given client is registered in system - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

# Simplified Architecture imports  
from brief_bridge.entities.client import Client
from brief_bridge.repositories.client_repository import InMemoryClientRepository

def invoke(ctx: ScenarioContext, client_id: str) -> None:
    """
    Business rule: client.registration - setup test client in repository
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.GIVEN
    # Set up input state for scenario execution
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Client registration setup not implemented")