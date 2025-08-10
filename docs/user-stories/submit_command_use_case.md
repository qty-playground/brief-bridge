# Submit Command Use Case

## Business Context
The SubmitCommandUseCase is responsible for handling command submission from AI assistants to target clients in the Brief Bridge system. This use case manages command submission, waits for execution completion, and returns results to the AI assistant.

**Key Change**: The AI assistant now waits for command execution results instead of just submitting and returning immediately.

## Use Case Specification
- **Use Case**: SubmitCommandUseCase.execute_command_submission()
- **Input**: CommandSubmissionRequest(target_client_id, command_content, command_type)
- **Output**: CommandSubmissionResponse(command_id, target_client_id, submission_successful, submission_message, result, error, execution_time)
- **Dependencies**: ClientRepository, CommandRepository interfaces

## Business Rules
- **command.target_validation**: Commands can only be submitted to registered clients
- **command.unique_id**: Each command gets a unique identifier for tracking
- **command.pending_state**: Newly submitted commands start in "pending" status
- **command.execution_wait**: AI waits for command execution completion (up to 30 seconds)
- **command.status_flow**: pending → processing → completed/failed
- **command.result_capture**: Execution output, errors, and timing are captured
- **client.online_check**: Target client must be registered (availability check deferred)

## Test Scenarios

### Scenario: Submit command and wait for successful execution
```
Given client "test-client-001" is registered and online
And client will execute commands successfully
When I submit command with:
  - target_client_id: "test-client-001"
  - command_content: "echo 'Hello from AI'"
  - command_type: "shell"
Then command submission should be successful
And submission response should contain:
  - command_id: [generated-uuid]
  - target_client_id: "test-client-001"
  - submission_successful: true
  - submission_message: "Command executed successfully"
  - result: "Hello from AI"
  - execution_time: [positive-number]
And command should be saved in repository with:
  - command_id: [generated-uuid]
  - target_client_id: "test-client-001"
  - content: "echo 'Hello from AI'"
  - type: "shell"
  - status: "completed"
  - result: "Hello from AI"
  - completed_at: [current-timestamp]
  - execution_time: [positive-number]
```

### Scenario: Submit command and wait for failed execution
```
Given client "test-client-001" is registered and online
And client will execute commands with failure
When I submit command with:
  - target_client_id: "test-client-001"
  - command_content: "nonexistent-command"
  - command_type: "shell"
Then command submission should fail
And submission response should contain:
  - command_id: [generated-uuid]
  - target_client_id: "test-client-001"
  - submission_successful: false
  - submission_message: "Command execution failed"
  - error: "Command not found"
And command should be saved in repository with:
  - status: "failed"
  - error: "Command not found"
```

### Scenario: Submit command with timeout (no client response)
```
Given client "offline-client" is registered but offline
When I submit command with:
  - target_client_id: "offline-client"
  - command_content: "echo 'test'"
  - command_type: "shell"
Then command submission should fail after 30 seconds
And submission response should contain:
  - submission_successful: false
  - submission_message: "Command execution timeout"
  - error: "timeout"
And command should remain in repository with:
  - status: "pending"
```

### Scenario: Submit command with minimal information and wait for result
```
Given client "minimal-client" is registered and online
And client will execute commands successfully
When I submit command with:
  - target_client_id: "minimal-client"
  - command_content: "pwd"
Then command submission should be successful
And submission response should contain:
  - command_id: [generated-uuid]
  - target_client_id: "minimal-client"
  - submission_successful: true
  - result: [directory-path]
And command should be saved in repository with:
  - command_id: [generated-uuid]
  - target_client_id: "minimal-client"
  - content: "pwd"
  - type: "shell"  # default type
  - status: "completed"
  - result: [directory-path]
```

### Scenario: Submit command to unregistered client
```
Given no client exists with id "nonexistent-client"
When I submit command with:
  - target_client_id: "nonexistent-client"
  - command_content: "echo 'test'"
Then command submission should fail
And submission response should contain:
  - submission_successful: false
  - submission_message: "Target client not found"
And no command should be saved in repository
```

### Scenario: Submit command with empty content
```
Given client "valid-client" is registered in system
When I submit command with:
  - target_client_id: "valid-client"
  - command_content: ""
Then command submission should fail
And submission response should contain:
  - submission_successful: false
  - submission_message: "Command content cannot be empty"
And no command should be saved in repository
```

### Scenario: Submit command with empty target client ID
```
Given no preconditions
When I submit command with:
  - target_client_id: ""
  - command_content: "echo 'test'"
Then command submission should fail
And submission response should contain:
  - submission_successful: false
  - submission_message: "Target client ID cannot be empty"
And no command should be saved in repository
```

### Scenario: Multiple clients with isolated command execution
```
Given client "client-A" is registered and online
And client "client-B" is registered and online  
And client "client-A" will execute commands successfully with delay 1 second
And client "client-B" will execute commands successfully with delay 2 seconds
When I submit command to "client-A" with content "echo 'A result'"
And I submit command to "client-B" with content "echo 'B result'" 
Then both commands should execute independently
And "client-A" command should complete with result "A result" 
And "client-B" command should complete with result "B result"
And commands should not interfere with each other's execution
And each client should only see their own commands
```

**Business Rules for Multi-Client Isolation:**
- **command.client_isolation**: Commands are isolated by target_client_id
- **command.parallel_execution**: Multiple clients can execute commands simultaneously  
- **command.no_interference**: One client's command execution doesn't affect another's
- **command.client_filtering**: Each client only receives their assigned commands

### Scenario: Submit base64 encoded command with complex quotes
```
Given client "powershell-client" is registered and online
And client will execute commands successfully
When I submit command with:
  - target_client_id: "powershell-client"
  - command_content: "V3JpdGUtSG9zdCAiSGVsbG8gJ1dvcmxkJyIgLUZvcmVncm91bmRDb2xvciBHcmVlbg=="
  - command_type: "powershell"
  - encoding: "base64"
Then command submission should be successful
And submission response should contain:
  - command_id: [generated-uuid]
  - target_client_id: "powershell-client"
  - submission_successful: true
  - submission_message: "Command executed successfully"
  - result: "Hello 'World'"
And command should be saved in repository with:
  - content: "V3JpdGUtSG9zdCAiSGVsbG8gJ1dvcmxkJyIgLUZvcmVncm91bmRDb2xvciBHcmVlbg=="
  - encoding: "base64"
  - status: "completed"
```

### Scenario: Submit base64 encoded multi-line script
```
Given client "script-client" is registered and online
And client will execute commands successfully
When I submit command with:
  - target_client_id: "script-client"
  - command_content: "aWYgKCR0cnVlKSB7CiAgICBXcml0ZS1Ib3N0ICJMaW5lIDEiCiAgICBXcml0ZS1Ib3N0ICJMaW5lIDIiCn0="
  - command_type: "powershell"
  - encoding: "base64"
Then command submission should be successful
And the decoded script should execute properly
And submission response should contain:
  - submission_successful: true
  - result: [multi-line-output]
```

### Scenario: Submit invalid base64 encoded command
```
Given client "test-client" is registered and online
When I submit command with:
  - target_client_id: "test-client"
  - command_content: "invalid-base64-content!!!"
  - command_type: "shell"
  - encoding: "base64"
Then command submission should fail
And submission response should contain:
  - submission_successful: false
  - submission_message: "Invalid base64 encoding"
  - error: "Invalid base64 encoding"
```

## Notes
- This use case now handles both command submission AND result waiting
- AI assistants get synchronous response with execution results
- Client polling and result submission happen asynchronously
- Command status lifecycle: pending → processing → completed/failed
- Maximum wait time is 30 seconds before timeout
- New command fields: result, error, execution_time, started_at, completed_at
- **Base64 encoding support**: Use for commands > 3 lines or with complex quotes
- **Base64 validation**: Invalid base64 strings are rejected with clear error messages
- **Encoding preservation**: Original encoding information is stored for audit trail