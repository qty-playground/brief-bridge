from fastapi import APIRouter, Depends, HTTPException
from typing import List
from brief_bridge.web.schemas import SubmitCommandRequestSchema, SubmitCommandResponseSchema, CommandSchema
from brief_bridge.web.dependencies import get_submit_command_use_case, get_command_repository
from brief_bridge.use_cases.submit_command_use_case import SubmitCommandUseCase, CommandSubmissionRequest
from brief_bridge.repositories.command_repository import CommandRepository

router = APIRouter(prefix="/commands", tags=["commands"])


@router.post("/submit", response_model=SubmitCommandResponseSchema)
async def submit_command_to_client(
    request: SubmitCommandRequestSchema,
    use_case: SubmitCommandUseCase = Depends(get_submit_command_use_case)
) -> SubmitCommandResponseSchema:
    """API endpoint: Submit command to target client"""
    use_case_request: CommandSubmissionRequest = CommandSubmissionRequest(
        target_client_id=request.target_client_id,
        command_content=request.command_content,
        command_type=request.command_type
    )
    
    submission_response = await use_case.execute_command_submission(use_case_request)
    
    return SubmitCommandResponseSchema(
        command_id=submission_response.command_id,
        target_client_id=submission_response.target_client_id,
        submission_successful=submission_response.submission_successful,
        submission_message=submission_response.submission_message
    )


@router.get("/{command_id}", response_model=CommandSchema)
async def get_command_by_id(
    command_id: str,
    repository: CommandRepository = Depends(get_command_repository)
) -> CommandSchema:
    """API endpoint: Retrieve specific command by ID"""
    command = await repository.find_command_by_id(command_id)
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    return CommandSchema(
        command_id=command.command_id,
        target_client_id=command.target_client_id,
        content=command.content,
        type=command.type,
        status=command.status,
        created_at=str(command.created_at) if command.created_at else None
    )


@router.get("/", response_model=List[CommandSchema])
async def get_all_commands(
    repository: CommandRepository = Depends(get_command_repository)
) -> List[CommandSchema]:
    """API endpoint: List all commands in the system"""
    all_commands = await repository.get_all_commands()
    return [
        CommandSchema(
            command_id=command.command_id,
            target_client_id=command.target_client_id,
            content=command.content,
            type=command.type,
            status=command.status,
            created_at=str(command.created_at) if command.created_at else None
        )
        for command in all_commands
    ]


@router.get("/client/{client_id}", response_model=List[CommandSchema])
async def get_commands_by_client_id(
    client_id: str,
    repository: CommandRepository = Depends(get_command_repository)
) -> List[CommandSchema]:
    """API endpoint: Retrieve all commands for specific client"""
    client_commands = await repository.find_commands_by_client_id(client_id)
    return [
        CommandSchema(
            command_id=command.command_id,
            target_client_id=command.target_client_id,
            content=command.content,
            type=command.type,
            status=command.status,
            created_at=str(command.created_at) if command.created_at else None
        )
        for command in client_commands
    ]