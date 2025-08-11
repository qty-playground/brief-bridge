Feature: Client State Management

  @skip
  Scenario: Update client last_seen on polling
    Given client "active-client" is registered with status "online"
    When client polls server for commands
    Then client last_seen should be updated to current timestamp
    And client status should remain "online"

  @skip
  Scenario: Mark client as offline after threshold time
    Given offline threshold is set to 1 second for testing
    And client "idle-client" was last seen 2 seconds ago
    When system checks client status
    Then client should be marked as "offline"

  @skip
  Scenario: Auto-recover offline client on polling
    Given client "offline-client" has status "offline"
    When client polls server for commands
    Then client status should be updated to "online"
    And client last_seen should be updated to current timestamp

  @skip
  Scenario: Server sends terminate command to client
    Given client "target-client" is online
    When server submits terminate command to client
    Then command should be created with type "terminate"
    And command should be queued for client to receive
    And command submission should be successful

  @skip
  Scenario: Get active clients excludes offline ones
    Given clients with different statuses:
      | client_id  | status  |
      | online-1   | online  |
      | offline-1  | offline |
    When server retrieves active clients list
    Then response should include "online-1"
    And response should not include "offline-1"

  @skip
  Scenario: Client status check with configurable threshold
    Given offline threshold is configured to 5 seconds
    And client "test-client" was last seen 6 seconds ago
    When system performs status check
    Then client should be marked as "offline"