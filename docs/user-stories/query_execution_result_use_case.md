# Query Execution Result Use Case

## API Specification
- **Endpoint**: `GET /commands/{command_id}`
- **Path Parameter**: `command_id` (string, UUID)
- **Success Response**: `{"command_id": "string", "status": "string", "result": {...}}`
- **Error Responses**: `{"error": "string", "code": "string"}`

## Test Scenarios

### Scenario: Query result of completed successful command
```
Given command "cmd-12345" exists with:
  - command_id: "cmd-12345"
  - client_id: "client-001"
  - content: "echo 'test output'"
  - status: "COMPLETED"
And execution result exists with:
  - command_id: "cmd-12345"
  - status: "COMPLETED"
  - stdout: "test output\n"
  - stderr: ""
  - exit_code: 0
  - duration: 125
  - completed_at: "2024-01-15T10:30:45.123Z"
When I GET "/commands/cmd-12345"
Then response status code should be 200
And response body should be:
  {
    "command_id": "cmd-12345",
    "client_id": "client-001",
    "content": "echo 'test output'",
    "status": "COMPLETED",
    "result": {
      "stdout": "test output\n",
      "stderr": "",
      "exit_code": 0,
      "duration": 125,
      "completed_at": "2024-01-15T10:30:45.123Z"
    }
  }
```

### Scenario: Query result of running command
```
Given command "cmd-67890" exists with:
  - command_id: "cmd-67890"
  - client_id: "client-002"
  - content: "sleep 30"
  - status: "RUNNING"
  - started_at: "2024-01-15T10:30:00.000Z"
And no execution result exists for "cmd-67890"
When I GET "/commands/cmd-67890"
Then response status code should be 200
And response body should be:
  {
    "command_id": "cmd-67890",
    "client_id": "client-002", 
    "content": "sleep 30",
    "status": "RUNNING",
    "started_at": "2024-01-15T10:30:00.000Z",
    "result": null
  }
```

### Scenario: Query result of failed command
```
Given command "cmd-error" exists with:
  - command_id: "cmd-error"
  - status: "FAILED"
And execution result exists with:
  - command_id: "cmd-error"
  - status: "FAILED"
  - stdout: ""
  - stderr: "command not found: invalid-cmd\n"
  - exit_code: 127
  - duration: 45
  - completed_at: "2024-01-15T10:31:00.456Z"
When I GET "/commands/cmd-error"
Then response status code should be 200
And response body should be:
  {
    "command_id": "cmd-error",
    "status": "FAILED",
    "result": {
      "stdout": "",
      "stderr": "command not found: invalid-cmd\n",
      "exit_code": 127,
      "duration": 45,
      "completed_at": "2024-01-15T10:31:00.456Z"
    }
  }
```

### Scenario: Query result of timed-out command
```
Given command "cmd-timeout" exists with:
  - command_id: "cmd-timeout"
  - status: "TIMEOUT"
And execution result exists with:
  - command_id: "cmd-timeout"
  - status: "TIMEOUT"
  - stdout: "partial output before timeout"
  - stderr: ""
  - exit_code: -1
  - duration: 30000
  - completed_at: "2024-01-15T10:45:00.000Z"
When I GET "/commands/cmd-timeout"
Then response status code should be 200
And response body should be:
  {
    "command_id": "cmd-timeout",
    "status": "TIMEOUT", 
    "result": {
      "stdout": "partial output before timeout",
      "stderr": "",
      "exit_code": -1,
      "duration": 30000,
      "completed_at": "2024-01-15T10:45:00.000Z"
    }
  }
```

### Scenario: Query non-existent command
```
Given no command exists with id "invalid-cmd-id"
When I GET "/commands/invalid-cmd-id"
Then response status code should be 404
And response body should be:
  {
    "error": "Command not found",
    "code": "COMMAND_NOT_FOUND"
  }
```

## Reusable Step Definitions

### Given Steps
- `Given command "{command_id}" exists with: {properties}`
- `Given execution result exists with: {properties}`
- `Given no execution result exists for "{command_id}"`
- `Given no command exists with id "{command_id}"`

### When Steps
- `When I GET "{endpoint}"`

### Then Steps
- `Then response status code should be {status_code}`
- `Then response body should be: {json_exact}`

## Business Rules Validation
- **execution_result.completeness**: Verified by presence check
- **execution_result.full_output**: All fields included in response
- **execution_result.error_preservation**: stderr preserved in failed commands
- **command.timeout**: Timeout status properly returned