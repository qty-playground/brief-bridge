"""When I submit command with data - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json
import asyncio

# Simplified Architecture imports
from brief_bridge.use_cases.submit_command_use_case import SubmitCommandUseCase, CommandSubmissionRequest
from brief_bridge.repositories.client_repository import InMemoryClientRepository

def invoke(ctx: ScenarioContext, command_data: str) -> None:
    """
    Execute command submission through use case layer
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.WHEN
    # Can access input state from GIVEN phase, collect results here
    
    # Parse command data from docstring
    request_data = json.loads(command_data)
    
    # Create request object
    submission_request = CommandSubmissionRequest(
        target_client_id=request_data["target_client_id"],
        command_content=request_data["command_content"],
        command_type=request_data.get("command_type", "shell"),
        encoding=request_data.get("encoding", None)
    )
    
    # GREEN Stage 2: Real production invoke chain with simulated client execution
    
    # Get repositories from GIVEN phase - handle both naming conventions
    client_repository = getattr(ctx, 'client_repository', None) or ctx.test_client_repository
    command_repository = getattr(ctx, 'command_repository', None) or ctx.test_command_repository
    
    # Create use case - use short timeout for offline clients to speed up testing
    if getattr(ctx, 'test_client_online', True):
        # Online client - use default timeout
        use_case = SubmitCommandUseCase(client_repository, command_repository)
    else:
        # Offline client - use very short timeout for testing (2 seconds instead of 30)
        use_case = SubmitCommandUseCase(client_repository, command_repository, max_wait_time=2.0, poll_interval=0.5)
    
    # Simulate client execution in background while use case is waiting
    async def simulate_client_execution():
        # Only simulate if client is online (not for timeout scenarios)
        if getattr(ctx, 'test_client_online', True):  # Default to online if not set
            # Wait a bit to let the use case start waiting
            await asyncio.sleep(0.1)
            
            # Find the pending command (the one we just submitted)
            pending_commands = await command_repository.get_all_commands()
            if pending_commands:
                command = pending_commands[-1]  # Get the latest command
                # Simulate client picking up and completing the command
                if hasattr(ctx, 'expected_result'):
                    command.mark_as_completed(ctx.expected_result, 0.15)
                else:
                    command.mark_as_completed("Hello from AI", 0.15)
                await command_repository.save_command(command)
        # If client is offline, don't simulate execution - let it timeout
    
    async def execute_use_case():
        return await use_case.execute_command_submission(submission_request)
    
    # Run both coroutines concurrently
    async def run_with_simulation():
        simulation_task = asyncio.create_task(simulate_client_execution())
        use_case_task = asyncio.create_task(execute_use_case())
        
        # Wait for use case to complete
        response = await use_case_task
        
        # Make sure simulation finishes too
        await simulation_task
        
        return response
    
    ctx.submission_response = asyncio.run(run_with_simulation())