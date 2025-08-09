from conftest import ScenarioContext, BDDPhase
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor


def invoke(ctx: ScenarioContext, commands_data: str) -> None:
    """Submit multiple commands to different clients simultaneously"""
    from brief_bridge.use_cases.submit_command_use_case import SubmitCommandUseCase, CommandSubmissionRequest
    
    # Parse commands data from docstring
    commands = json.loads(commands_data)
    
    # Get repositories from GIVEN phase - handle both naming conventions
    client_repository = getattr(ctx, 'client_repository', None) or ctx.test_client_repository
    command_repository = getattr(ctx, 'command_repository', None) or ctx.test_command_repository
    
    # Create use case
    use_case = SubmitCommandUseCase(client_repository, command_repository)
    
    # Function to submit a single command and simulate client execution
    async def submit_and_execute_command(command_data):
        submission_request = CommandSubmissionRequest(
            target_client_id=command_data["target_client_id"],
            command_content=command_data["command_content"],
            command_type=command_data.get("command_type", "shell")
        )
        
        client_id = command_data["target_client_id"]
        
        # Get execution settings for this client
        execution_settings = ctx.client_execution_settings.get(client_id, {
            'success': True, 
            'delay': 0.1, 
            'result': 'default result'
        })
        
        # Simulate client execution in background while use case is waiting
        async def simulate_client_execution():
            # Wait for the specified delay to simulate different execution times
            await asyncio.sleep(execution_settings['delay'])
            
            # Find the pending command for this client (the one we just submitted)
            pending_commands = await command_repository.get_pending_commands_for_client(client_id)
            if pending_commands:
                command = pending_commands[-1]  # Get the latest command
                # Simulate client picking up and completing the command
                command.mark_as_completed(execution_settings['result'], execution_settings['delay'])
                await command_repository.save_command(command)
        
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
        
        return await run_with_simulation()
    
    # Submit commands concurrently to test isolation
    async def submit_all_commands():
        tasks = [submit_and_execute_command(cmd) for cmd in commands]
        return await asyncio.gather(*tasks)
    
    # Store responses for later verification
    responses = asyncio.run(submit_all_commands())
    
    # Store in context using the result collection mechanism for WHEN phase
    ctx._results['multi_command_responses'] = responses