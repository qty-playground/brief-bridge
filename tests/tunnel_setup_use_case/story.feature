Feature: Tunnel Setup

  @skip
  Scenario: Auto tunnel setup with ngrok
    Given Brief Bridge server is running locally
    And ngrok is installed on the system
    When administrator starts server with --enable-tunnel parameter
    Then system should automatically start ngrok tunnel
    And should display public URL with pattern "https://[a-z0-9]+.ngrok.io"
    And API should be accessible through public URL

  @wip
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

  @skip
  Scenario: Setup with custom domain
    Given administrator has custom domain and SSL certificate
    When administrator sets up custom tunnel with:
      """
      {
        "provider": "custom",
        "public_url": "https://brief-bridge.example.com"
      }
      """
    Then system should use provided URL
    And should not start any tunnel service
    And install URLs should use custom domain

  @skip
  Scenario: Cloudflare tunnel setup
    Given administrator has Cloudflare account
    When administrator sets up Cloudflare tunnel with:
      """
      {
        "provider": "cloudflare",
        "config": {
          "tunnel_name": "brief-bridge-tunnel",
          "credentials": "..."
        }
      }
      """
    Then system should setup Cloudflare tunnel
    And provide stable public URL

  @skip
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

  @skip
  Scenario: Tunnel disconnection and reconnection
    Given tunnel is running
    When tunnel connection is interrupted
    Then system should automatically attempt reconnection
    And if reconnection fails should:
      """
      - Log error
      - Send notification if configured
      - Attempt fallback tunnel service
      """

  @skip
  Scenario: Multiple tunnel provider fallback
    Given system configured with multiple tunnel providers priority:
      """
      1. ngrok
      2. cloudflare
      3. localtunnel
      """
    When primary tunnel service fails
    Then system should automatically switch to next available service
    And update all related URLs