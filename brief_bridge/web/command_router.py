from fastapi import APIRouter, Depends, HTTPException
from typing import List
import os
from brief_bridge.web.schemas import SubmitCommandRequestSchema, SubmitCommandResponseSchema, CommandSchema, SubmitResultRequestSchema, SubmitResultResponseSchema
from brief_bridge.web.dependencies import get_submit_command_use_case, get_command_repository, get_client_repository
from brief_bridge.use_cases.submit_command_use_case import SubmitCommandUseCase, CommandSubmissionRequest
from brief_bridge.repositories.command_repository import CommandRepository
from brief_bridge.repositories.client_repository import ClientRepository

router = APIRouter(prefix="/commands", tags=["commands"])


@router.post("/submit", 
             response_model=SubmitCommandResponseSchema,
             summary="Submit Command to Client",
             description="""
Submit a command to a target client for execution. 

**Base64 Encoding Recommended For:**
- Commands longer than 3 lines
- Commands with both single and double quotes  
- Multi-line scripts or complex syntax
- Commands with special characters that need shell escaping

**Examples:**
- Simple command: `"echo 'Hello World'"`
- Complex command (base64): `"V3JpdGUtSG9zdCAiSGVsbG8gJ1dvcmxkJyIgLUZvcmVncm91bmRDb2xvciBHcmVlbg=="` 
  (decodes to: `Write-Host "Hello 'World'" -ForegroundColor Green`)

The API waits for command execution and returns results synchronously.
             """)
async def submit_command_to_client(
    request: SubmitCommandRequestSchema,
    use_case: SubmitCommandUseCase = Depends(get_submit_command_use_case)
) -> SubmitCommandResponseSchema:
    """Submit command to target client with optional base64 encoding support"""
    use_case_request: CommandSubmissionRequest = CommandSubmissionRequest(
        target_client_id=request.target_client_id,
        command_content=request.command_content,
        command_type=request.command_type,
        encoding=request.encoding
    )
    
    submission_response = await use_case.execute_command_submission(use_case_request)
    
    return SubmitCommandResponseSchema(
        command_id=submission_response.command_id,
        target_client_id=submission_response.target_client_id,
        submission_successful=submission_response.submission_successful,
        submission_message=submission_response.submission_message,
        result=submission_response.result,
        error=submission_response.error,
        execution_time=submission_response.execution_time
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
        encoding=command.encoding,
        created_at=str(command.created_at) if command.created_at else None,
        started_at=str(command.started_at) if command.started_at else None,
        completed_at=str(command.completed_at) if command.completed_at else None,
        result=command.result,
        error=command.error,
        execution_time=command.execution_time
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
            encoding=command.encoding,
            created_at=str(command.created_at) if command.created_at else None,
            started_at=str(command.started_at) if command.started_at else None,
            completed_at=str(command.completed_at) if command.completed_at else None,
            result=command.result,
            error=command.error,
            execution_time=command.execution_time
        )
        for command in all_commands
    ]


@router.get("/client/{client_id}", response_model=List[CommandSchema])
async def get_commands_by_client_id(
    client_id: str,
    repository: CommandRepository = Depends(get_command_repository),
    client_repository: ClientRepository = Depends(get_client_repository)
) -> List[CommandSchema]:
    """API endpoint: Client retrieves pending commands and marks them as processing"""
    # Update client activity when polling
    client = await client_repository.find_client_by_id(client_id)
    if client:
        client.update_activity()
        await client_repository.save_registered_client(client)
    
    # Get only pending commands for this client
    pending_commands = await repository.get_pending_commands_for_client(client_id)
    
    # If there are pending commands, mark the first one as processing
    if pending_commands:
        command = pending_commands[0]  # Only return one command for single execution
        command.mark_as_processing()
        await repository.save_command(command)
        
        return [CommandSchema(
            command_id=command.command_id,
            target_client_id=command.target_client_id,
            content=command.content,
            type=command.type,
            status=command.status,
            encoding=command.encoding,
            created_at=str(command.created_at) if command.created_at else None,
            started_at=str(command.started_at) if command.started_at else None,
            completed_at=str(command.completed_at) if command.completed_at else None,
            result=command.result,
            error=command.error,
            execution_time=command.execution_time
        )]
    
    return []  # No pending commands


@router.post("/poll", response_model=dict)
async def poll_for_commands(
    request: dict,
    repository: CommandRepository = Depends(get_command_repository)
) -> dict:
    """API endpoint: Client polls for pending commands"""
    client_id = request.get("client_id")
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id is required")
    
    # Get only pending commands for this client
    pending_commands = await repository.get_pending_commands_for_client(client_id)
    
    # If there are pending commands, mark the first one as processing and return it
    if pending_commands:
        command = pending_commands[0]  # Only return one command for single execution
        command.mark_as_processing()
        await repository.save_command(command)
        
        return {
            "command_id": command.command_id,
            "command_content": command.content,
            "timeout": int(float(os.getenv('BRIEF_BRIDGE_COMMAND_TIMEOUT', '300.0')))  # Use configured timeout
        }
    
    # No pending commands - return empty response
    return {}


@router.post("/result", response_model=SubmitResultResponseSchema)
async def submit_command_result(
    request: SubmitResultRequestSchema,
    repository: CommandRepository = Depends(get_command_repository)
) -> SubmitResultResponseSchema:
    """API endpoint: Client submits command execution result"""
    # Find the command by ID
    command = await repository.find_command_by_id(request.command_id)
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    # Update command with execution result
    if request.error:
        command.mark_as_failed(request.error, request.execution_time or 0.0)
    else:
        command.mark_as_completed(request.output or "", request.execution_time or 0.0)
    
    # Save updated command
    await repository.save_command(command)
    
    return SubmitResultResponseSchema(
        status="success",
        message="Result received successfully"
    )