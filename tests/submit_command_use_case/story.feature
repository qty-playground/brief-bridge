Feature: Submit Command Use Case

  Scenario: Submit command and wait for successful execution
    Given client "test-client-001" is registered and online
    And client will execute commands successfully
    When I submit command with:
      """
      {
        "target_client_id": "test-client-001",
        "command_content": "echo 'Hello from AI'",
        "command_type": "shell"
      }
      """
    Then command submission should be successful
    And submission response should contain:
      """
      {
        "target_client_id": "test-client-001",
        "submission_successful": true,
        "submission_message": "Command executed successfully",
        "result": "Hello from AI"
      }
      """
    And command should be saved in repository with:
      """
      {
        "target_client_id": "test-client-001",
        "content": "echo 'Hello from AI'",
        "type": "shell",
        "status": "completed",
        "result": "Hello from AI"
      }
      """

  Scenario: Submit command with timeout (no client response)
    Given client "offline-client" is registered but offline
    When I submit command with:
      """
      {
        "target_client_id": "offline-client",
        "command_content": "echo 'test'",
        "command_type": "shell"
      }
      """
    Then command submission should fail after timeout
    And submission response should contain:
      """
      {
        "target_client_id": "offline-client",
        "submission_successful": false,
        "submission_message": "Command execution timeout after 2.0 seconds"
      }
      """
    And command should be saved in repository with:
      """
      {
        "target_client_id": "offline-client",
        "content": "echo 'test'",
        "type": "shell",
        "status": "pending"
      }
      """

  Scenario: Submit command to unregistered client
    Given no client exists with id "nonexistent-client"
    When I submit command with:
      """
      {
        "target_client_id": "nonexistent-client",
        "command_content": "echo 'test'"
      }
      """
    Then command submission should fail
    And submission response should contain:
      """
      {
        "submission_successful": false,
        "submission_message": "Target client not found"
      }
      """
    And no command should be saved in repository

  Scenario: Submit command with empty content
    Given client "valid-client" is registered in system
    When I submit command with:
      """
      {
        "target_client_id": "valid-client",
        "command_content": ""
      }
      """
    Then command submission should fail
    And submission response should contain:
      """
      {
        "submission_successful": false,
        "submission_message": "Command content cannot be empty"
      }
      """
    And no command should be saved in repository

  Scenario: Submit command with empty target client ID
    Given no preconditions
    When I submit command with:
      """
      {
        "target_client_id": "",
        "command_content": "echo 'test'"
      }
      """
    Then command submission should fail
    And submission response should contain:
      """
      {
        "submission_successful": false,
        "submission_message": "Target client ID cannot be empty"
      }
      """
    And no command should be saved in repository

  Scenario: Multiple clients with isolated command execution
    Given client "client-A" is registered and online
    And client "client-B" is registered and online
    And client "client-A" will execute commands successfully with delay 1 second
    And client "client-B" will execute commands successfully with delay 2 seconds
    When I submit commands to both clients:
      """
      [
        {
          "target_client_id": "client-A",
          "command_content": "echo 'A result'",
          "command_type": "shell"
        },
        {
          "target_client_id": "client-B", 
          "command_content": "echo 'B result'",
          "command_type": "shell"
        }
      ]
      """
    Then both commands should execute independently
    And first command response should contain:
      """
      {
        "target_client_id": "client-A",
        "submission_successful": true,
        "submission_message": "Command executed successfully",
        "result": "A result"
      }
      """
    And second command response should contain:
      """
      {
        "target_client_id": "client-B",
        "submission_successful": true,
        "submission_message": "Command executed successfully", 
        "result": "B result"
      }
      """
    And client "client-A" should have only their command in repository
    And client "client-B" should have only their command in repository