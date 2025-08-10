Feature: Tunnel Setup

  Scenario: Manual tunnel setup
    Given Brief Bridge server is running
    When administrator calls tunnel setup API with:
      """
      {
        "provider": "ngrok",
        "auth_token": "optional-auth-token"
      }
      """
    Then system should start specified tunnel service
    And response should contain:
      """
      {
        "status": "active",
        "public_url": "https://[a-z0-9]+.ngrok.io",
        "provider": "ngrok",
        "install_urls": {
          "powershell": "https://[a-z0-9]+.ngrok.io/install.ps1",
          "bash": "https://[a-z0-9]+.ngrok.io/install.sh"
        }
      }
      """

  Scenario: Get current tunnel status
    Given tunnel is already setup and running
    When administrator queries tunnel status
    Then response should show:
      """
      {
        "active": true,
        "provider": "ngrok",
        "public_url": "https://[a-z0-9]+.ngrok.io",
        "uptime": 3600,
        "connections": 5,
        "install_commands": {
          "windows": "iex ((Invoke-WebRequest 'https://[a-z0-9]+.ngrok.io/install.ps1').Content)",
          "linux": "curl -sSL https://[a-z0-9]+.ngrok.io/install.sh | bash"
        }
      }
      """