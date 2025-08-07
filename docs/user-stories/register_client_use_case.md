# Register Client Use Case

## API Specification
- **Endpoint**: `POST /clients/register`
- **Request Body**: `{"client_info": {"os": "string", "architecture": "string", "version": "string"}}`
- **Success Response**: `{"client_id": "string", "status": "ONLINE", "heartbeat_interval": number}`
- **Error Responses**: `{"error": "string", "code": "string"}`

## Test Scenarios

### Scenario: Register new client successfully
```
Given no client exists with system fingerprint "Windows|x64|10.0.19042"
When I POST to "/clients/register" with:
  {
    "client_info": {
      "os": "Windows",
      "architecture": "x64", 
      "version": "10.0.19042"
    }
  }
Then response status code should be 201
And response body should match:
  {
    "client_id": "<uuid>",
    "status": "ONLINE",
    "availability": "IDLE",
    "heartbeat_interval": 30
  }
And client record should exist with:
  - client_id: <generated_uuid>
  - status: "ONLINE"
  - availability: "IDLE"
  - client_info: {"os": "Windows", "architecture": "x64", "version": "10.0.19042"}
  - last_heartbeat: <current_timestamp>
  - created_at: <current_timestamp>
```

### Scenario: Re-register existing client
```
Given client "existing-client-123" exists with:
  - client_id: "existing-client-123"
  - status: "OFFLINE"
  - client_info: {"os": "Linux", "architecture": "x86_64", "version": "Ubuntu 20.04"}
  - last_heartbeat: "2024-01-15T09:00:00.000Z"
When I POST to "/clients/register" with:
  {
    "client_info": {
      "os": "Linux", 
      "architecture": "x86_64",
      "version": "Ubuntu 20.04"
    }
  }
Then response status code should be 200
And response body should be:
  {
    "client_id": "existing-client-123",
    "status": "ONLINE", 
    "availability": "IDLE",
    "heartbeat_interval": 30
  }
And client record should be updated with:
  - client_id: "existing-client-123"
  - status: "ONLINE"
  - availability: "IDLE"
  - last_heartbeat: <current_timestamp>
```

### Scenario: Register with missing client info
```
When I POST to "/clients/register" with:
  {
    "client_info": {
      "os": "Windows"
    }
  }
Then response status code should be 400
And response body should be:
  {
    "error": "Missing required client information",
    "code": "INVALID_CLIENT_INFO",
    "missing_fields": ["architecture", "version"]
  }
And no client record should be created
```

### Scenario: Register with invalid client info
```
When I POST to "/clients/register" with:
  {
    "client_info": {
      "os": "",
      "architecture": "x64",
      "version": "10.0"
    }
  }
Then response status code should be 400
And response body should be:
  {
    "error": "Invalid client information provided",
    "code": "INVALID_CLIENT_INFO",
    "details": "OS cannot be empty"
  }
```

### Scenario: Register without request body
```
When I POST to "/clients/register" with empty body
Then response status code should be 400
And response body should be:
  {
    "error": "Request body is required",
    "code": "MISSING_REQUEST_BODY"
  }
```

## Reusable Step Definitions

### Given Steps
- `Given no client exists with system fingerprint "{fingerprint}"`
- `Given client "{client_id}" exists with: {properties}`

### When Steps
- `When I POST to "{endpoint}" with: {json_payload}`
- `When I POST to "{endpoint}" with empty body`

### Then Steps
- `Then response status code should be {status_code}`
- `Then response body should match: {json_schema}`
- `Then response body should be: {json_exact}`
- `Then client record should exist with: {properties}`
- `Then client record should be updated with: {properties}`
- `Then no client record should be created`

## Business Rules Validation
- **client.registration**: Verified by successful client record creation
- **client.heartbeat**: Initial heartbeat timestamp set on registration  
- **client.availability**: New clients start with IDLE availability