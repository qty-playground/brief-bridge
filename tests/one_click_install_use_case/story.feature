Feature: One-Click Install

  @skip
  Scenario: PowerShell one-click install success
    Given server is running and accessible via public URL
    When user executes PowerShell install command:
      """
      iex ((Invoke-WebRequest 'http://server-url/install.ps1').Content)
      """
    Then client script should be downloaded
    And client should automatically register with server
    And client should start polling for commands
    And user should see success message

  @skip
  Scenario: Bash one-click install success
    Given server is running and accessible via public URL
    When user executes Bash install command:
      """
      curl -sSL http://server-url/install.sh | bash
      """
    Then client script should be downloaded
    And client should automatically register with server
    And client should start polling for commands
    And user should see success message

  @skip
  Scenario: Install with custom client ID
    Given server is running and accessible via public URL
    When user executes install command with specified client ID:
      """
      iex ((Invoke-WebRequest 'http://server-url/install.ps1?client_id=my-laptop').Content)
      """
    Then client should register with ID "my-laptop"
    And client should start polling for commands

  @skip
  Scenario: Install with multiple parameters
    Given server is running and accessible via public URL
    When user executes install command with multiple parameters:
      """
      iex ((Invoke-WebRequest 'http://server-url/install.ps1?client_id=laptop&poll_interval=5&debug=true').Content)
      """
    Then client should run with specified parameters:
      """
      {
        "client_id": "laptop",
        "poll_interval": 5,
        "debug": true
      }
      """

  @skip
  Scenario: Background execution mode
    Given server is running and accessible via public URL
    When user executes install command with background flag:
      """
      iex ((Invoke-WebRequest 'http://server-url/install.ps1').Content) -Background
      """
    Then client should run in background
    And user should be able to continue using terminal
    And client process should continue polling for commands

  @skip
  Scenario: Install failure - server unreachable
    Given server URL is not accessible
    When user executes install command
    Then connection error message should be displayed
    And installation should abort
    And no client process should be running

  @skip
  Scenario: Handle duplicate installation
    Given client is already running
    When user executes install command again
    Then should detect existing client
    And should ask user to choose:
      """
      - Stop existing client and reinstall
      - Keep existing client running
      - Cancel installation
      """