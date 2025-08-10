"""Then response should contain expected data - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json

def invoke(ctx: ScenarioContext, expected_response: str) -> None:
    """
    Verify response contains expected JSON structure
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Assert response matches expected JSON
    
    # GREEN Stage 1: Verify response structure
    import json
    import re
    
    assert hasattr(ctx, "tunnel_setup_response"), "Tunnel setup response not found"
    actual = ctx.tunnel_setup_response
    expected = json.loads(expected_response)
    
    # Verify each expected field
    for key, expected_value in expected.items():
        assert key in actual, f"Expected key '{key}' not found in response"
        
        # Handle pattern matching for URLs
        if isinstance(expected_value, str) and expected_value.startswith("https://") and "[a-z0-9]" in expected_value:
            # Convert pattern to regex and test
            pattern = expected_value.replace("[a-z0-9]+", "[a-z0-9]+")
            pattern = pattern.replace(".", "\\.")
            assert re.match(pattern, actual[key]), f"URL {actual[key]} doesn't match pattern {expected_value}"
        elif isinstance(expected_value, dict):
            # Recursive check for nested objects
            for nested_key, nested_value in expected_value.items():
                assert nested_key in actual[key], f"Expected nested key '{nested_key}' not found"
                if isinstance(nested_value, str) and "[a-z0-9]" in nested_value:
                    pattern = nested_value.replace("[a-z0-9]+", "[a-z0-9]+").replace(".", "\\.")
                    assert re.match(pattern, actual[key][nested_key]), f"URL doesn't match pattern"
        else:
            assert actual[key] == expected_value, f"Expected {key}='{expected_value}', got '{actual[key]}'"
