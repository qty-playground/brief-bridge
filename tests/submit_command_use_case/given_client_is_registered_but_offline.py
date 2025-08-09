from conftest import ScenarioContext, BDDPhase


def invoke(ctx: ScenarioContext, client_id: str) -> None:
    """Create and register an offline client"""
    from brief_bridge.entities.client import Client
    from brief_bridge.repositories.client_repository import InMemoryClientRepository
    from brief_bridge.repositories.command_repository import InMemoryCommandRepository
    import asyncio
    
    # Setup repositories if not already created
    if not hasattr(ctx, 'client_repository'):
        ctx.client_repository = InMemoryClientRepository()
    if not hasattr(ctx, 'command_repository'):
        ctx.command_repository = InMemoryCommandRepository()
    
    # Create and register offline client
    client = Client.register_new_client(client_id=client_id, name=f"Client {client_id}")
    # Mark as offline for testing
    client.status = "offline"
    
    # Store client in repository
    asyncio.run(ctx.client_repository.save_registered_client(client))
    
    # Store for later use in scenario
    ctx.test_client_id = client_id
    ctx.test_client_online = False