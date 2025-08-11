# Client State Management Use Case

## Business Context
The Client State Management system tracks client activity on the server side through polling behavior and provides terminate command functionality. This ensures accurate client status and enables server-initiated client termination.

## Use Case Specification
- **Use Case**: ClientStateManagementUseCase.update_client_activity() and .send_terminate_command()
- **Input**: Client polling requests, terminate command requests
- **Output**: Updated client status, command submission results
- **Dependencies**: ClientRepository, CommandRepository interfaces

## Business Rules
- **client.activity_tracking**: Each client polling updates last_seen timestamp
- **client.online_threshold**: Clients with activity within threshold time are "online"
- **client.offline_detection**: Clients inactive for threshold+ time are marked "offline"
- **client.auto_recovery**: Offline clients automatically become "online" when they poll again
- **client.terminate_command**: Server can send "terminate" type commands to clients
- **client.configurable_timeout**: Offline threshold is configurable (default 600 seconds)

## Test Scenarios

### Scenario: Update client last_seen on polling
```
Given client "active-client" is registered with status "online"
When client polls server for commands
Then client last_seen should be updated to current timestamp
And client status should remain "online"
```

### Scenario: Mark client as offline after threshold time
```
Given offline threshold is set to 1 second for testing
And client "idle-client" was last seen 2 seconds ago
When system checks client status
Then client should be marked as "offline"
```

### Scenario: Auto-recover offline client on polling
```
Given client "offline-client" has status "offline" 
When client polls server for commands
Then client status should be updated to "online"
And client last_seen should be updated to current timestamp
```

### Scenario: Server sends terminate command to client
```
Given client "target-client" is online
When server submits terminate command to client
Then command should be created with type "terminate"
And command should be queued for client to receive
And command submission should be successful
```

### Scenario: Get active clients excludes offline ones
```
Given clients with different statuses:
  | client_id  | status  |
  | online-1   | online  |
  | offline-1  | offline |
When server retrieves active clients list
Then response should include "online-1"
And response should not include "offline-1"
```

### Scenario: Client status check with configurable threshold
```
Given offline threshold is configured to 5 seconds
And client "test-client" was last seen 6 seconds ago
When system performs status check
Then client should be marked as "offline"
```

## Implementation Notes
- Client activity tracking happens on every polling request
- Status checking can be done on-demand or via background task
- Terminate command uses existing command submission flow
- Offline threshold configurable via CLIENT_OFFLINE_THRESHOLD_SECONDS environment variable
- Default threshold is 600 seconds (10 minutes) for production
- Tests use short thresholds (1-5 seconds) for rapid validation
- Client-side termination behavior is handled separately