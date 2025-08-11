"""Given clients with different statuses table - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from brief_bridge.entities.client import Client
from brief_bridge.repositories.client_repository import InMemoryClientRepository
import asyncio

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: test.data_setup - create multiple test clients from table data
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain with hardcoded behavior
    if not hasattr(ctx, 'client_repository'):
        ctx.client_repository = InMemoryClientRepository()
    
    async def setup_clients():
        # pytest-bdd passes table data as list of lists, convert to dict format
        if hasattr(ctx.clients_table, '__iter__'):
            rows = list(ctx.clients_table)
            if len(rows) > 0 and isinstance(rows[0], (list, tuple)):
                # Convert list format to dict format using header row
                headers = rows[0] if len(rows) > 0 else []
                data_rows = rows[1:] if len(rows) > 1 else []
                
                for data_row in data_rows:
                    row_dict = dict(zip(headers, data_row))
                    client_id = row_dict['client_id']
                    status = row_dict['status']
                    
                    client = Client.register_new_client(client_id, None)
                    client.status = status
                    await ctx.client_repository.save_registered_client(client)
            else:
                # Already in dict format
                for row in rows:
                    client_id = row['client_id']
                    status = row['status']
                    
                    client = Client.register_new_client(client_id, None)
                    client.status = status
                    await ctx.client_repository.save_registered_client(client)
    
    asyncio.run(setup_clients())