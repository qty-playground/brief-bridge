# List Available Clients Use Case

## API Specification
- **Endpoint**: `GET /clients`
- **Query Parameters**: 
  - `available_only` (boolean, optional): Filter only available clients
- **Success Response**: `{"clients": [...]}`
- **Client Object**: `{"client_id": "string", "status": "string", "availability": "string", "client_info": {...}, "last_heartbeat": "string"}`

## Test Scenarios

### Scenario: List all clients with mixed statuses
```
Given client "client-001" exists with:
  - client_id: "client-001"
  - status: "ONLINE"
  - availability: "IDLE"
  - client_info: {"os": "Windows", "architecture": "x64", "version": "10.0.19042"}
  - last_heartbeat: "2024-01-15T10:30:00.000Z"
And client "client-002" exists with:
  - client_id: "client-002"
  - status: "ONLINE"
  - availability: "BUSY"
  - client_info: {"os": "Linux", "architecture": "x86_64", "version": "Ubuntu 20.04"}
  - last_heartbeat: "2024-01-15T10:29:45.000Z"
And client "client-003" exists with:
  - client_id: "client-003"
  - status: "OFFLINE"
  - availability: "IDLE"
  - client_info: {"os": "macOS", "architecture": "arm64", "version": "12.6"}
  - last_heartbeat: "2024-01-15T10:20:00.000Z"
When I GET "/clients"
Then response status code should be 200
And response body should be:
  {
    "clients": [
      {
        "client_id": "client-001",
        "status": "ONLINE",
        "availability": "IDLE",
        "client_info": {
          "os": "Windows",
          "architecture": "x64",
          "version": "10.0.19042"
        },
        "last_heartbeat": "2024-01-15T10:30:00.000Z"
      },
      {
        "client_id": "client-002",
        "status": "ONLINE", 
        "availability": "BUSY",
        "client_info": {
          "os": "Linux",
          "architecture": "x86_64",
          "version": "Ubuntu 20.04"
        },
        "last_heartbeat": "2024-01-15T10:29:45.000Z"
      },
      {
        "client_id": "client-003",
        "status": "OFFLINE",
        "availability": "IDLE",
        "client_info": {
          "os": "macOS",
          "architecture": "arm64", 
          "version": "12.6"
        },
        "last_heartbeat": "2024-01-15T10:20:00.000Z"
      }
    ]
  }
```

### Scenario: List only available clients
```
Given client "client-available" exists with:
  - client_id: "client-available"
  - status: "ONLINE"
  - availability: "IDLE"
  - client_info: {"os": "Linux", "architecture": "x86_64", "version": "Ubuntu 22.04"}
  - last_heartbeat: "2024-01-15T10:30:00.000Z"
And client "client-busy" exists with:
  - client_id: "client-busy"
  - status: "ONLINE"
  - availability: "BUSY"
  - last_heartbeat: "2024-01-15T10:29:50.000Z"
And client "client-offline" exists with:
  - client_id: "client-offline"
  - status: "OFFLINE"
  - availability: "IDLE"
  - last_heartbeat: "2024-01-15T10:15:00.000Z"
When I GET "/clients?available_only=true"
Then response status code should be 200
And response body should be:
  {
    "clients": [
      {
        "client_id": "client-available",
        "status": "ONLINE",
        "availability": "IDLE",
        "client_info": {
          "os": "Linux",
          "architecture": "x86_64",
          "version": "Ubuntu 22.04"
        },
        "last_heartbeat": "2024-01-15T10:30:00.000Z"
      }
    ]
  }
```

### Scenario: List clients when no clients exist
```
Given no clients exist in the system
When I GET "/clients"
Then response status code should be 200
And response body should be:
  {
    "clients": []
  }
```

### Scenario: List available clients when none are available
```
Given client "client-busy" exists with:
  - status: "ONLINE"
  - availability: "BUSY"
And client "client-offline" exists with:
  - status: "OFFLINE"
  - availability: "IDLE"
When I GET "/clients?available_only=true"
Then response status code should be 200
And response body should be:
  {
    "clients": []
  }
```

## Reusable Step Definitions

### Given Steps
- `Given client "{client_id}" exists with: {properties}`
- `Given no clients exist in the system`

### When Steps
- `When I GET "{endpoint}"`

### Then Steps
- `Then response status code should be {status_code}`
- `Then response body should be: {json_exact}`

## Business Rules Validation
- **client.registration**: Only registered clients appear in list
- **client.heartbeat**: last_heartbeat timestamp included
- **client.offline_detection**: Status reflects heartbeat timeout
- **client.availability**: Availability field indicates if ready for commands
- **client.concurrency**: Busy clients shown as unavailable