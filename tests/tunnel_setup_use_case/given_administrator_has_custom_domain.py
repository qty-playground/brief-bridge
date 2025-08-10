"""Given administrator has custom domain and SSL certificate - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: tunnel.custom_domain - setup custom domain configuration
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Configure custom domain and SSL certificate
    
    # GREEN Stage 1: Setup custom domain configuration
    ctx.custom_domain = "brief-bridge.example.com"
    ctx.ssl_certificate = "valid-ssl-cert"
    ctx.domain_configured = True
