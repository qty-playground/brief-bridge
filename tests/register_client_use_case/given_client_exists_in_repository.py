"""Given client exists in repository - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json

# Simplified Architecture imports
from brief_bridge.entities.client import Client
from brief_bridge.repositories.client_repository import ClientRepository, InMemoryClientRepository

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.registration - create test client in repository
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.GIVEN
    # Can access input state set in GIVEN phase
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Client creation in repository not implemented")