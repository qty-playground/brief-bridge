Feature: Register Client Use Case

  Scenario: Register new client successfully
    Given no client exists with id "new-client-001"
    When I execute client registration with:
      """
      {
        "client_id": "new-client-001",
        "client_name": "Test Client Alpha"
      }
      """
    Then registration should be successful
    And registration response should contain:
      """
      {
        "client_id": "new-client-001",
        "client_name": "Test Client Alpha",
        "client_status": "online",
        "registration_successful": true,
        "registration_message": "Client registered successfully"
      }
      """
    And client should be saved in repository with:
      """
      {
        "client_id": "new-client-001",
        "name": "Test Client Alpha",
        "status": "online"
      }
      """

  @skip
  Scenario: Register client with minimal information
    Given no client exists with id "minimal-client"
    When I execute client registration with:
      """
      {
        "client_id": "minimal-client",
        "client_name": null
      }
      """
    Then registration should be successful
    And registration response should contain:
      """
      {
        "client_id": "minimal-client",
        "client_name": null,
        "client_status": "online",
        "registration_successful": true
      }
      """
    And client should be saved in repository with:
      """
      {
        "client_id": "minimal-client",
        "name": null,
        "status": "online"
      }
      """

  @skip
  Scenario: Register client that already exists
    Given client "existing-client" exists in repository with:
      """
      {
        "client_id": "existing-client",
        "name": "Original Name",
        "status": "online"
      }
      """
    When I execute client registration with:
      """
      {
        "client_id": "existing-client",
        "client_name": "Updated Name"
      }
      """
    Then registration should be successful
    And registration response should contain:
      """
      {
        "client_id": "existing-client",
        "client_name": "Updated Name",
        "client_status": "online",
        "registration_successful": true
      }
      """
    And repository should contain updated client with:
      """
      {
        "client_id": "existing-client",
        "name": "Updated Name",
        "status": "online"
      }
      """

  @skip
  Scenario: Register client with empty client_id
    Given no preconditions
    When I execute client registration with:
      """
      {
        "client_id": "",
        "client_name": "Invalid Client"
      }
      """
    Then registration should fail
    And registration response should contain:
      """
      {
        "registration_successful": false,
        "registration_message": "Client ID cannot be empty"
      }
      """
    And no client should be saved in repository