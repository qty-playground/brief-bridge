"""Then response should show expected status - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json

def invoke(ctx: ScenarioContext, expected_response: str) -> None:
    """
    Verify response shows expected status information
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Assert response contains expected status data
    
    # GREEN Stage 1: Verify status response structure
    import json
    import re
    
    assert hasattr(ctx, "tunnel_status_response"), "Tunnel status response not found"
    actual = ctx.tunnel_status_response
    expected = json.loads(expected_response)
    
    # Verify each expected field with pattern matching
    for key, expected_value in expected.items():
        assert key in actual, f"Expected key '{key}' not found in status response"
        
        if isinstance(expected_value, str) and "[a-z0-9]" in expected_value:
            # Handle URL pattern matching
            pattern = expected_value.replace("[a-z0-9]+", "[a-z0-9]+").replace(".", "\\.")
            assert re.match(pattern, actual[key]), f"Status field {key} doesn't match pattern {expected_value}"
        elif isinstance(expected_value, dict):
            # Handle nested objects like install_commands
            for nested_key, nested_value in expected_value.items():
                assert nested_key in actual[key], f"Expected nested key '{nested_key}' not found in {key}"
                if isinstance(nested_value, str) and "[a-z0-9]" in nested_value:
                    # More sophisticated pattern matching for install commands
                    # Extract the base URL pattern and check the command structure
                    if "https://" in nested_value and "[a-z0-9]" in nested_value:
                        # Just check that the actual value contains a valid ngrok URL
                        assert "https://" in actual[key][nested_key], f"Install command should contain https URL"
                        assert ".ngrok.io" in actual[key][nested_key], f"Install command should contain ngrok.io domain"
                        assert "install." in actual[key][nested_key], f"Install command should reference install script"
                    else:
                        pattern = nested_value.replace("[a-z0-9]+", "[a-z0-9]+").replace(".", "\\.")
                        assert re.match(pattern, actual[key][nested_key]), f"Nested field doesn't match pattern"
        elif key in ["uptime", "connections"]:
            # For numeric fields, just check they exist and are reasonable
            assert isinstance(actual[key], (int, float)), f"Expected {key} to be numeric, got {type(actual[key])}"
            assert actual[key] >= 0, f"Expected {key} to be non-negative, got {actual[key]}"
        else:
            assert actual[key] == expected_value, f"Expected {key}='{expected_value}', got '{actual[key]}'"
