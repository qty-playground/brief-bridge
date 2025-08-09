# Submit Command Use Case

## Business Context
The SubmitCommandUseCase is responsible for handling command submission from AI assistants to target clients in the Brief Bridge system. This use case manages the business logic of command distribution, target validation, and command lifecycle management at the application layer level.

## Use Case Specification
- **Use Case**: SubmitCommandUseCase.execute_command_submission()
- **Input**: CommandSubmissionRequest(target_client_id, command_content, command_type)
- **Output**: CommandSubmissionResponse(command_id, target_client_id, submission_successful, submission_message)
- **Dependencies**: ClientRepository, CommandRepository interfaces

## Business Rules
- **command.target_validation**: Commands can only be submitted to registered clients
- **command.unique_id**: Each command gets a unique identifier for tracking
- **command.pending_state**: Newly submitted commands start in "pending" status
- **client.online_check**: Target client must be registered (availability check deferred)

## Test Scenarios

### Scenario: Submit command to registered client successfully
```
Given client "test-client-001" is registered in system
When I submit command with:
  - target_client_id: "test-client-001"
  - command_content: "echo 'Hello from AI'"
  - command_type: "shell"
Then command submission should be successful
And submission response should contain:
  - command_id: [generated-uuid]
  - target_client_id: "test-client-001"
  - submission_successful: true
  - submission_message: "Command submitted successfully"
And command should be saved in repository with:
  - command_id: [generated-uuid]
  - target_client_id: "test-client-001"
  - content: "echo 'Hello from AI'"
  - type: "shell"
  - status: "pending"
  - created_at: [current-timestamp]
```

### Scenario: Submit command with minimal information
```
Given client "minimal-client" is registered in system
When I submit command with:
  - target_client_id: "minimal-client"
  - command_content: "pwd"
Then command submission should be successful
And submission response should contain:
  - command_id: [generated-uuid]
  - target_client_id: "minimal-client"
  - submission_successful: true
And command should be saved in repository with:
  - command_id: [generated-uuid]
  - target_client_id: "minimal-client"
  - content: "pwd"
  - type: "shell"  # default type
  - status: "pending"
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

## Notes
- Command execution and result handling are separate use cases
- This use case focuses purely on command submission and validation
- Actual command dispatch to clients happens via polling mechanism
- Command status lifecycle: pending → dispatched → running → completed/failed