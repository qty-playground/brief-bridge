from dataclasses import dataclass
from typing import Optional
from brief_bridge.repositories.command_repository import CommandRepository
from brief_bridge.repositories.client_repository import ClientRepository


@dataclass
class CommandSubmissionRequest:
    target_client_id: str
    command_content: str
    command_type: Optional[str] = "shell"


@dataclass
class CommandSubmissionResponse:
    command_id: Optional[str] = None
    target_client_id: Optional[str] = None
    submission_successful: bool = False
    submission_message: str = ""


class SubmitCommandUseCase:
    def __init__(self, client_repository: ClientRepository, command_repository: CommandRepository) -> None:
        self._client_repository = client_repository
        self._command_repository = command_repository
    
    async def execute_command_submission(self, request: CommandSubmissionRequest) -> CommandSubmissionResponse:
        """Business rule: command.target_validation - submit command to registered client"""
        from brief_bridge.entities.command import Command
        
        # Business rule: command.target_validation - validate target client ID not empty
        if not request.target_client_id or request.target_client_id.strip() == "":
            return CommandSubmissionResponse(
                submission_successful=False,
                submission_message="Target client ID cannot be empty"
            )
        
        # Business rule: command.content_validation - validate command content not empty
        if not request.command_content or request.command_content.strip() == "":
            return CommandSubmissionResponse(
                submission_successful=False,
                submission_message="Command content cannot be empty"
            )
        
        # Business rule: command.target_validation - check if client exists
        target_client = await self._client_repository.find_client_by_id(request.target_client_id)
        if not target_client:
            return CommandSubmissionResponse(
                submission_successful=False,
                submission_message="Target client not found"
            )
        
        # Business rule: command.unique_id - create command with unique ID
        command = Command.create_new_command(
            target_client_id=request.target_client_id,
            content=request.command_content,
            command_type=request.command_type or "shell"
        )
        
        # Business rule: command.persistence - save command to repository
        saved_command = await self._command_repository.save_command(command)
        
        return CommandSubmissionResponse(
            command_id=saved_command.command_id,
            target_client_id=saved_command.target_client_id,
            submission_successful=True,
            submission_message="Command submitted successfully"
        )