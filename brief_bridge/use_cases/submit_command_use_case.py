from dataclasses import dataclass
from typing import Optional
from brief_bridge.repositories.command_repository import CommandRepository
from brief_bridge.repositories.client_repository import ClientRepository

# Configuration constants for command execution waiting
import os
DEFAULT_MAX_WAIT_TIME = float(os.getenv('BRIEF_BRIDGE_COMMAND_TIMEOUT', '300.0'))  # 5 minutes default
DEFAULT_POLL_INTERVAL = 0.5   # seconds


@dataclass
class CommandSubmissionRequest:
    target_client_id: str
    command_content: str
    command_type: Optional[str] = "shell"
    # encoding removed - no longer supporting base64


@dataclass
class CommandSubmissionResponse:
    command_id: Optional[str] = None
    target_client_id: Optional[str] = None
    submission_successful: bool = False
    submission_message: str = ""
    # New fields for execution results
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class SubmitCommandUseCase:
    def __init__(self, client_repository: ClientRepository, command_repository: CommandRepository, max_wait_time: float = DEFAULT_MAX_WAIT_TIME, poll_interval: float = DEFAULT_POLL_INTERVAL) -> None:
        self._client_repository = client_repository
        self._command_repository = command_repository
        self._max_wait_time = max_wait_time
        self._poll_interval = poll_interval
    
    async def _wait_for_command_completion(self, command_id: str, max_wait_time: float = None, poll_interval: float = None) -> CommandSubmissionResponse:
        """Wait for command completion and return appropriate response"""
        import asyncio
        
        # Use instance settings or provided parameters
        max_wait_time = max_wait_time or self._max_wait_time
        poll_interval = poll_interval or self._poll_interval
        waited_time = 0.0
        
        while waited_time < max_wait_time:
            # Refresh command from repository to check for updates
            refreshed_command = await self._command_repository.find_command_by_id(command_id)
            if refreshed_command and refreshed_command.is_completed():
                if refreshed_command.error:
                    # Command completed with error
                    return CommandSubmissionResponse(
                        command_id=refreshed_command.command_id,
                        target_client_id=refreshed_command.target_client_id,
                        submission_successful=False,
                        submission_message=f"Command execution failed: {refreshed_command.error}",
                        error=refreshed_command.error,
                        execution_time=refreshed_command.execution_time
                    )
                else:
                    # Command completed successfully
                    return CommandSubmissionResponse(
                        command_id=refreshed_command.command_id,
                        target_client_id=refreshed_command.target_client_id,
                        submission_successful=True,
                        submission_message="Command executed successfully",
                        result=refreshed_command.result,
                        execution_time=refreshed_command.execution_time
                    )
            
            # Wait for next poll
            await asyncio.sleep(poll_interval)
            waited_time += poll_interval
        
        # Timeout occurred - command did not complete within max_wait_time
        return CommandSubmissionResponse(
            command_id=command_id,
            target_client_id=refreshed_command.target_client_id if refreshed_command else None,
            submission_successful=False,
            submission_message=f"Command execution timeout after {max_wait_time} seconds",
            execution_time=waited_time
        )
    
    async def execute_command_submission(self, request: CommandSubmissionRequest) -> CommandSubmissionResponse:
        """Business rule: command.target_validation - submit command and wait for results"""
        from brief_bridge.entities.command import Command
        import asyncio
        # Business rule: command.target_validation - validate target client ID not empty
        if not request.target_client_id or request.target_client_id.strip() == "":
            return CommandSubmissionResponse(
                target_client_id=request.target_client_id,
                submission_successful=False,
                submission_message="Target client ID cannot be empty"
            )
        
        # Business rule: command.content_validation - validate command content not empty
        if not request.command_content or request.command_content.strip() == "":
            return CommandSubmissionResponse(
                target_client_id=request.target_client_id,
                submission_successful=False,
                submission_message="Command content cannot be empty"
            )
        
        # Use command content directly (no base64 decoding)
        decoded_content = request.command_content
        
        # Business rule: command.target_validation - check if client exists
        target_client = await self._client_repository.find_client_by_id(request.target_client_id)
        if not target_client:
            return CommandSubmissionResponse(
                target_client_id=request.target_client_id,
                submission_successful=False,
                submission_message="Target client not found"
            )
        
        # Business rule: command.unique_id - create command with unique ID
        command = Command.create_new_command(
            target_client_id=request.target_client_id,
            content=decoded_content,  # Use decoded content
            command_type=request.command_type or "shell",
            encoding=request.encoding  # Store original encoding info
        )
        
        # Business rule: command.persistence - save command to repository
        saved_command = await self._command_repository.save_command(command)
        
        # Business rule: command.execution_wait - wait for execution completion
        return await self._wait_for_command_completion(saved_command.command_id)