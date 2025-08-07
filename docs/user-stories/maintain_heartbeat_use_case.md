# Maintain Heartbeat Use Case

## API Specification
- **Endpoint**: `PUT /clients/{client_id}/heartbeat`
- **Path Parameter**: `client_id` (string, UUID)
- **Request Body**: `{}` (empty JSON object)
- **Success Response**: `{"status": "acknowledged", "next_heartbeat_in": number}`
- **Error Responses**: `{"error": "string", "code": "string"}`

## Test Scenarios

### Scenario: Send heartbeat for online client
```
Given client "client-001" exists with:
  - client_id: "client-001"
  - status: "ONLINE"
  - availability: "IDLE"
  - last_heartbeat: "2024-01-15T10:29:30.000Z"
When I PUT to "/clients/client-001/heartbeat" with: {}
Then response status code should be 200
And response body should be:
  {
    "status": "acknowledged",
    "next_heartbeat_in": 30
  }
And client "client-001" should be updated with:
  - last_heartbeat: <current_timestamp>
  - status: "ONLINE"
```

### Scenario: Send heartbeat for offline client (reactivation)
```
Given client "client-002" exists with:
  - client_id: "client-002"
  - status: "OFFLINE"
  - availability: "IDLE"
  - last_heartbeat: "2024-01-15T09:00:00.000Z"
When I PUT to "/clients/client-002/heartbeat" with: {}
Then response status code should be 200
And response body should be:
  {
    "status": "acknowledged",
    "next_heartbeat_in": 30
  }
And client "client-002" should be updated with:
  - last_heartbeat: <current_timestamp>
  - status: "ONLINE"
  - availability: "IDLE"
```

### Scenario: Send heartbeat for busy client
```
Given client "client-003" exists with:
  - client_id: "client-003"
  - status: "ONLINE"
  - availability: "BUSY"
  - last_heartbeat: "2024-01-15T10:29:00.000Z"
When I PUT to "/clients/client-003/heartbeat" with: {}
Then response status code should be 200
And response body should be:
  {
    "status": "acknowledged", 
    "next_heartbeat_in": 30
  }
And client "client-003" should be updated with:
  - last_heartbeat: <current_timestamp>
  - status: "ONLINE"
  - availability: "BUSY"
```

### Scenario: Send heartbeat for non-existent client
```
Given no client exists with id "invalid-client"
When I PUT to "/clients/invalid-client/heartbeat" with: {}
Then response status code should be 404
And response body should be:
  {
    "error": "Client not found",
    "code": "CLIENT_NOT_FOUND"
  }
```

### Scenario: Send heartbeat with invalid request body
```
Given client "client-004" exists with client_id "client-004"
When I PUT to "/clients/client-004/heartbeat" with:
  {
    "invalid": "data"
  }
Then response status code should be 400
And response body should be:
  {
    "error": "Invalid request body for heartbeat",
    "code": "INVALID_HEARTBEAT_DATA"
  }
```

### Scenario: System detects offline client due to missed heartbeats
```
Given client "client-005" exists with:
  - client_id: "client-005"
  - status: "ONLINE"
  - last_heartbeat: "2024-01-15T10:00:00.000Z"
And current time is "2024-01-15T10:05:00.000Z"
And heartbeat timeout is 60 seconds
When heartbeat timeout check runs
Then client "client-005" status should remain "ONLINE"

Given current time is "2024-01-15T10:02:00.000Z"  
And heartbeat timeout is 60 seconds
When heartbeat timeout check runs
Then client "client-005" status should be updated to "OFFLINE"
And client "client-005" availability should be updated to "IDLE"
```

## Reusable Step Definitions

### Given Steps
- `Given client "{client_id}" exists with: {properties}`
- `Given no client exists with id "{client_id}"`
- `Given current time is "{timestamp}"`
- `Given heartbeat timeout is {seconds} seconds`

### When Steps
- `When I PUT to "{endpoint}" with: {json_payload}`
- `When heartbeat timeout check runs`

### Then Steps
- `Then response status code should be {status_code}`
- `Then response body should be: {json_exact}`
- `Then client "{client_id}" should be updated with: {properties}`
- `Then client "{client_id}" status should remain "{status}"`
- `Then client "{client_id}" status should be updated to "{status}"`
- `Then client "{client_id}" availability should be updated to "{availability}"`

## Business Rules Validation
- **client.heartbeat**: Timestamp updated on successful heartbeat
- **client.offline_detection**: Clients marked offline after timeout
- **client.availability**: Offline clients reset to IDLE availability