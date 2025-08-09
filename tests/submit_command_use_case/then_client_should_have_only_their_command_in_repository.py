from conftest import ScenarioContext, BDDPhase
import asyncio


def invoke(ctx: ScenarioContext, client_id: str) -> None:
    """Verify client has only their own command in repository"""
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # Get repositories
    client_repository = getattr(ctx, 'client_repository', None) or ctx.test_client_repository
    command_repository = getattr(ctx, 'command_repository', None) or ctx.test_command_repository
    
    async def verify_client_isolation():
        # Get all commands for this specific client
        client_commands = await command_repository.find_commands_by_client_id(client_id)
        
        # Should have exactly one command
        assert len(client_commands) == 1, f"Client {client_id} should have exactly 1 command, found {len(client_commands)}"
        
        # Verify the command belongs to this client
        command = client_commands[0]
        assert command.target_client_id == client_id, f"Command should belong to {client_id}, but target is {command.target_client_id}"
        
        # Verify the command is completed
        assert command.status == "completed", f"Command should be completed, but status is {command.status}"
        
        # Verify the result matches expected pattern for this client
        expected_result_suffix = client_id.split('-')[-1].upper() + " result"  # "A result" or "B result"
        assert command.result == expected_result_suffix, f"Command result should be '{expected_result_suffix}', but got '{command.result}'"
        
        # Get all commands in the system to verify isolation
        all_commands = await command_repository.get_all_commands()
        
        # Should have exactly 2 commands total (one for each client)
        assert len(all_commands) == 2, f"Should have 2 commands total in system, found {len(all_commands)}"
        
        # Verify each command belongs to the correct client
        client_ids = {cmd.target_client_id for cmd in all_commands}
        expected_clients = {"client-A", "client-B"}
        assert client_ids == expected_clients, f"Commands should belong to {expected_clients}, but found {client_ids}"
    
    # Run async verification
    asyncio.run(verify_client_isolation())