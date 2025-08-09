from conftest import ScenarioContext, BDDPhase


def invoke(ctx: ScenarioContext, client_id: str, delay_seconds: str) -> None:
    """Mark that client will execute commands successfully with specified delay"""
    # Parse delay as float - handle different formats
    delay_str = delay_seconds
    # Handle different possible formats
    if ' seconds' in delay_str:
        delay_str = delay_str.replace(' seconds', '')
    elif ' second' in delay_str:
        delay_str = delay_str.replace(' second', '')
    elif delay_str.endswith('s'):
        delay_str = delay_str[:-1]
    
    delay = float(delay_str.strip())
    
    # Store execution settings for this client
    if not hasattr(ctx, 'client_execution_settings'):
        ctx.client_execution_settings = {}
    
    ctx.client_execution_settings[client_id] = {
        'success': True,
        'delay': delay,
        'result': f'{client_id.split("-")[-1].upper()} result'  # Extract 'A' or 'B' from client-A/client-B
    }