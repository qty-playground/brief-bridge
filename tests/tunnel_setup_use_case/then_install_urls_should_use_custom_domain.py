"""Then install URLs should use custom domain - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify install URLs are using custom domain
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Assert install URLs contain custom domain
    
    # GREEN Stage 2: Real implementation
    custom_tunnel_response = ctx.custom_tunnel_response
    
    # Verify install URLs use the custom domain
    expected_domain = "https://brief-bridge.example.com"
    install_urls = custom_tunnel_response.get("install_urls", {})
    
    # Check PowerShell install URL
    powershell_url = install_urls.get("powershell")
    assert powershell_url and powershell_url.startswith(expected_domain), \
        f"PowerShell install URL should start with {expected_domain}, got: {powershell_url}"
    
    # Check Bash install URL  
    bash_url = install_urls.get("bash")
    assert bash_url and bash_url.startswith(expected_domain), \
        f"Bash install URL should start with {expected_domain}, got: {bash_url}"
        
    # Verify URLs have correct endpoints
    assert powershell_url.endswith("/install.ps1"), f"PowerShell URL should end with /install.ps1, got: {powershell_url}"
    assert bash_url.endswith("/install.sh"), f"Bash URL should end with /install.sh, got: {bash_url}"
