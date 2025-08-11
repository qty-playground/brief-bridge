Feature: Base64 Command Execution
  As a user of Brief Bridge
  I want to execute commands that contain complex quotes and special characters
  So that I can avoid shell escaping issues by using base64 encoding

  Background:
    Given the Brief Bridge server is running
    And a client is registered

  Scenario: Execute a simple base64 encoded command
    Given I have a command "echo 'Hello World'"
    When I encode the command to base64
    And I submit the command with encoding type "base64"
    Then the command should be executed successfully
    And the output should contain "Hello World"

  Scenario: Execute a complex command with quotes using base64
    Given I have a command with complex quotes: echo "Message with 'single' and \"double\" quotes"
    When I encode the command to base64
    And I submit the command with encoding type "base64"
    Then the command should be executed successfully
    And the output should contain "Message with 'single' and \"double\" quotes"

  Scenario: Execute a multi-line script using base64
    Given I have a multi-line script:
      """
      #!/bin/bash
      echo "Starting script..."
      VAR="value with 'quotes'"
      echo "Variable: $VAR"
      echo "Script completed"
      """
    When I encode the script to base64
    And I submit the command with encoding type "base64"
    Then the command should be executed successfully
    And the output should contain "Starting script..."
    And the output should contain "Variable: value with 'quotes'"
    And the output should contain "Script completed"

  Scenario: Execute Docker command with complex parameters using base64
    Given I have a Docker command: docker run -e VAR="value with 'quotes'" --name "container-name" ubuntu echo "Hello from Docker"
    When I encode the command to base64
    And I submit the command with encoding type "base64"
    Then the command should be executed successfully

  Scenario: Handle base64 decoding errors gracefully
    Given I have an invalid base64 string "not-valid-base64!!!"
    When I submit the command with encoding type "base64"
    Then the command should fail with a base64 decoding error
    And the error message should indicate "Invalid base64 encoding"

  Scenario: Backward compatibility with regular commands
    Given I have a simple command "echo 'test'"
    When I submit the command without encoding type
    Then the command should be executed successfully as before
    And the output should contain "test"

  Scenario: Client indicates support for base64 commands
    Given a client connects to the server
    When the client registers
    Then the client should indicate base64 command support in capabilities
    And the server should acknowledge the capability

  Scenario: Server sends base64 command to supporting client
    Given a client that supports base64 commands is registered
    When I submit a base64 encoded command
    Then the server should send the command with encoding type "base64"
    And the client should decode and execute the command correctly

  Scenario: Server falls back to regular command for non-supporting clients
    Given a client that does not support base64 commands is registered
    When I submit a base64 encoded command
    Then the server should decode the command first
    And send it as a regular command to the client
    Or reject the command with an appropriate error message