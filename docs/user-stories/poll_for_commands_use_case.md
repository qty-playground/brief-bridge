# Poll For Commands Use Case

## API Specification
- **Endpoint**: `GET /clients/{client_id}/commands`
- **Path Parameter**: `client_id` (string, UUID)
- **Success Response**: `{"command": {...}}` or `{"command": null}`
- **Error Responses**: `{"error": "string", "code": "string"}`

## Test Scenarios

### Scenario: Poll when command is available
```
Given client "client-001" exists with:
  - client_id: "client-001"
  - status: "ONLINE"
  - availability: "IDLE"
And command "cmd-123" exists with:
  - command_id: "cmd-123"
  - client_id: "client-001"
  - content: "echo 'hello world'"
  - status: "PENDING"
When I GET "/clients/client-001/commands"
Then response status code should be 200
And response body should be:
  {
    "command": {
      "command_id": "cmd-123",
      "content": "echo 'hello world'",
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  }
And command "cmd-123" status should be updated to "RUNNING"
And client "client-001" availability should be updated to "BUSY"
```

### Scenario: Poll when no commands are available
```
Given client "client-002" exists with:
  - client_id: "client-002"
  - status: "ONLINE"
  - availability: "IDLE"
And no pending commands exist for "client-002"
When I GET "/clients/client-002/commands"
Then response status code should be 200
And response body should be:
  {
    "command": null
  }
And client "client-002" availability should remain "IDLE"
```

### Scenario: Poll with non-existent client
```
Given no client exists with id "invalid-client"
When I GET "/clients/invalid-client/commands"
Then response status code should be 404
And response body should be:
  {
    "error": "Client not found",
    "code": "CLIENT_NOT_FOUND"
  }
```

### Scenario: Poll when client is offline
```
Given client "client-003" exists with:
  - client_id: "client-003"
  - status: "OFFLINE"
  - availability: "IDLE"
When I GET "/clients/client-003/commands"
Then response status code should be 403
And response body should be:
  {
    "error": "Client is not online",
    "code": "CLIENT_NOT_ONLINE"
  }
```

### Scenario: Poll when client is already busy
```
Given client "client-004" exists with:
  - client_id: "client-004"
  - status: "ONLINE"
  - availability: "BUSY"
When I GET "/clients/client-004/commands"
Then response status code should be 409
And response body should be:
  {
    "error": "Client is currently busy",
    "code": "CLIENT_BUSY"
  }
```

## Reusable Step Definitions

### Given Steps
- `Given client "{client_id}" exists with: {properties}`
- `Given command "{command_id}" exists with: {properties}`
- `Given no pending commands exist for "{client_id}"`
- `Given no client exists with id "{client_id}"`

### When Steps
- `When I GET "{endpoint}"`

### Then Steps
- `Then response status code should be {status_code}`
- `Then response body should be: {json_exact}`
- `Then command "{command_id}" status should be updated to "{status}"`
- `Then client "{client_id}" availability should be updated to "{availability}"`
- `Then client "{client_id}" availability should remain "{availability}"`

## Business Rules Validation
- **client.availability**: Only IDLE clients can receive new commands
- **client.concurrency**: Client becomes BUSY when receiving command
- **system.no_queue**: Only one command at a time per client
- **command.wait_for_completion**: Commands must be completed before new ones