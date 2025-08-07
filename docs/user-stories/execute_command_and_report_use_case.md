# Execute Command And Report Use Case

## API Specification
- **Endpoint**: `POST /clients/{client_id}/results`
- **Path Parameter**: `client_id` (string, UUID)
- **Request Body**: `{"command_id": "string", "result": {...}}`
- **Success Response**: `{"status": "accepted"}`
- **Error Responses**: `{"error": "string", "code": "string"}`

## Test Scenarios

### Scenario: Report successful command execution
```
Given client "client-001" exists with:
  - client_id: "client-001"
  - status: "ONLINE"
  - availability: "BUSY"
And command "cmd-123" exists with:
  - command_id: "cmd-123"
  - client_id: "client-001"
  - status: "RUNNING"
When I POST to "/clients/client-001/results" with:
  {
    "command_id": "cmd-123",
    "result": {
      "status": "COMPLETED",
      "stdout": "hello world\n",
      "stderr": "",
      "exit_code": 0,
      "duration": 250
    }
  }
Then response status code should be 200
And response body should be:
  {
    "status": "accepted"
  }
And execution result should be created with:
  - command_id: "cmd-123"
  - status: "COMPLETED"
  - stdout: "hello world\n"
  - stderr: ""
  - exit_code: 0
  - duration: 250
  - completed_at: <current_timestamp>
And command "cmd-123" status should be updated to "COMPLETED"
And client "client-001" availability should be updated to "IDLE"
```

### Scenario: Report failed command execution
```
Given client "client-002" exists with:
  - client_id: "client-002"
  - availability: "BUSY"
And command "cmd-456" exists with:
  - command_id: "cmd-456"
  - client_id: "client-002"
  - status: "RUNNING"
When I POST to "/clients/client-002/results" with:
  {
    "command_id": "cmd-456",
    "result": {
      "status": "FAILED",
      "stdout": "",
      "stderr": "command not found: invalid-cmd\n",
      "exit_code": 127,
      "duration": 45
    }
  }
Then response status code should be 200
And execution result should be created with:
  - command_id: "cmd-456"
  - status: "FAILED"
  - stdout: ""
  - stderr: "command not found: invalid-cmd\n"
  - exit_code: 127
  - duration: 45
And command "cmd-456" status should be updated to "FAILED"
And client "client-002" availability should be updated to "IDLE"
```

### Scenario: Report timeout command execution
```
Given command "cmd-timeout" exists with:
  - command_id: "cmd-timeout"
  - client_id: "client-003"
  - status: "RUNNING"
When I POST to "/clients/client-003/results" with:
  {
    "command_id": "cmd-timeout",
    "result": {
      "status": "TIMEOUT",
      "stdout": "partial output before timeout",
      "stderr": "",
      "exit_code": -1,
      "duration": 30000
    }
  }
Then response status code should be 200
And execution result should be created with:
  - status: "TIMEOUT"
  - exit_code: -1
  - duration: 30000
And command "cmd-timeout" status should be updated to "TIMEOUT"
```

### Scenario: Report result for non-existent command
```
Given client "client-004" exists with client_id "client-004"
And no command exists with id "invalid-cmd"
When I POST to "/clients/client-004/results" with:
  {
    "command_id": "invalid-cmd",
    "result": {
      "status": "COMPLETED",
      "stdout": "output",
      "stderr": "",
      "exit_code": 0,
      "duration": 100
    }
  }
Then response status code should be 404
And response body should be:
  {
    "error": "Command not found",
    "code": "COMMAND_NOT_FOUND"
  }
And no execution result should be created
```

### Scenario: Report result with mismatched client
```
Given client "client-005" exists with client_id "client-005"
And command "cmd-mismatch" exists with:
  - command_id: "cmd-mismatch"
  - client_id: "different-client"
  - status: "RUNNING"
When I POST to "/clients/client-005/results" with:
  {
    "command_id": "cmd-mismatch",
    "result": {
      "status": "COMPLETED",
      "stdout": "output",
      "stderr": "",
      "exit_code": 0,
      "duration": 100
    }
  }
Then response status code should be 403
And response body should be:
  {
    "error": "Command does not belong to this client",
    "code": "COMMAND_CLIENT_MISMATCH"
  }
```

### Scenario: Report result with invalid data
```
Given command "cmd-invalid" exists with:
  - command_id: "cmd-invalid"
  - client_id: "client-006"
  - status: "RUNNING"
When I POST to "/clients/client-006/results" with:
  {
    "command_id": "cmd-invalid",
    "result": {
      "status": "INVALID_STATUS"
    }
  }
Then response status code should be 400
And response body should be:
  {
    "error": "Invalid result data",
    "code": "INVALID_RESULT_DATA",
    "details": "Missing required fields: stdout, stderr, exit_code, duration"
  }
```

## Reusable Step Definitions

### Given Steps
- `Given client "{client_id}" exists with: {properties}`
- `Given command "{command_id}" exists with: {properties}`
- `Given no command exists with id "{command_id}"`

### When Steps
- `When I POST to "{endpoint}" with: {json_payload}`

### Then Steps
- `Then response status code should be {status_code}`
- `Then response body should be: {json_exact}`
- `Then execution result should be created with: {properties}`
- `Then command "{command_id}" status should be updated to "{status}"`
- `Then client "{client_id}" availability should be updated to "{availability}"`
- `Then no execution result should be created`

## Business Rules Validation
- **execution_result.completeness**: Result created for every completed command
- **execution_result.full_output**: All output fields preserved
- **execution_result.error_preservation**: Error information maintained
- **client.availability**: Client becomes IDLE after completing command