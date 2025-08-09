Feature: Submit Command Use Case

  Scenario: Submit command to registered client successfully
    Given client "test-client-001" is registered in system
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
        "submission_message": "Command submitted successfully"
      }
      """
    And command should be saved in repository with:
      """
      {
        "target_client_id": "test-client-001",
        "content": "echo 'Hello from AI'",
        "type": "shell",
        "status": "pending"
      }
      """

  @skip
  Scenario: Submit command with minimal information
    Given client "minimal-client" is registered in system
    When I submit command with:
      """
      {
        "target_client_id": "minimal-client",
        "command_content": "pwd"
      }
      """
    Then command submission should be successful
    And submission response should contain:
      """
      {
        "target_client_id": "minimal-client",
        "submission_successful": true
      }
      """
    And command should be saved in repository with:
      """
      {
        "target_client_id": "minimal-client",
        "content": "pwd",
        "type": "shell",
        "status": "pending"
      }
      """

  @skip
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

  @skip
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

  @skip
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