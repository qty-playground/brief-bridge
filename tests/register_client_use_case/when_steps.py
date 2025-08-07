"""
When Steps for Register Client
Action steps that trigger system behavior.
Each when step is independent and represents a single system interaction.
"""
from pytest_bdd import when


@when('I POST to "{endpoint}" with: {json_payload}')
def when_i_post_to_endpoint_with_payload(endpoint, json_payload):
    """
    Execute HTTP POST request with JSON payload.
    Independent action step - captures response for then steps.
    """
    raise NotImplementedError("Step not implemented - when_i_post_to_endpoint_with_payload")


@when('I POST to "{endpoint}" with empty body')
def when_i_post_to_endpoint_with_empty_body(endpoint):
    """
    Execute HTTP POST request with empty body.
    Independent action step for testing edge cases.
    """
    raise NotImplementedError("Step not implemented - when_i_post_to_endpoint_with_empty_body")
