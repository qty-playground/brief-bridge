# Submit Command Use Case

## API Specification
- **Endpoint**: `POST /commands`
- **Request Body**: `{"client_id": "string", "content": "string"}`
- **Success Response**: `{"command_id": "string", "status": "PENDING"}`
- **Error Responses**: `{"error": "string", "code": "string"}`

## Test Scenarios

### Scenario: Submit command to online idle client
```
Given client "client-001" exists with status "ONLINE" and availability "IDLE"
When I POST to "/commands" with:
  {
    "client_id": "client-001",
    "content": "echo 'hello world'"
  }
Then response status code should be 201
And response body should match:
  {
    "command_id": "<uuid>",
    "status": "PENDING",
    "client_id": "client-001"
  }
And command record should exist with:
  - command_id: <generated_uuid>
  - client_id: "client-001"  
  - content: "echo 'hello world'"
  - status: "PENDING"
  - created_at: <current_timestamp>
```

### Scenario: Submit command to offline client
```
Given client "client-002" exists with status "OFFLINE"
When I POST to "/commands" with:
  {
    "client_id": "client-002", 
    "content": "ls -la"
  }
Then response status code should be 400
And response body should be:
  {
    "error": "Client is not available for command execution",
    "code": "CLIENT_UNAVAILABLE",
    "client_status": "OFFLINE"
  }
And no command record should be created
```

### Scenario: Submit command to busy client
```
Given client "client-003" exists with status "ONLINE" and availability "BUSY"
When I POST to "/commands" with:
  {
    "client_id": "client-003",
    "content": "sleep 10"
  }
Then response status code should be 409
And response body should be:
  {
    "error": "Client is currently executing another command",
    "code": "CLIENT_BUSY"
  }
And no new command record should be created
```

### Scenario: Submit command to non-existent client
```
Given no client exists with id "invalid-client"
When I POST to "/commands" with:
  {
    "client_id": "invalid-client",
    "content": "whoami"
  }
Then response status code should be 404
And response body should be:
  {
    "error": "Client not found",
    "code": "CLIENT_NOT_FOUND"
  }
```

## Reusable Step Definitions

### Given Steps
- `Given client "{client_id}" exists with status "{status}" and availability "{availability}"`
- `Given no client exists with id "{client_id}"`

### When Steps  
- `When I POST to "{endpoint}" with: {json_payload}`

### Then Steps
- `Then response status code should be {status_code}`
- `Then response body should match: {json_schema}`
- `Then response body should be: {json_exact}`
- `Then command record should exist with: {properties}`
- `Then no command record should be created`
- `Then no new command record should be created`

## Business Rules Validation
- **command.target_validation**: Enforced by CLIENT_UNAVAILABLE error
- **client.concurrency**: Enforced by CLIENT_BUSY error  
- **system.no_queue**: No queuing - immediate accept/reject
- **client.availability**: Checked before command creation