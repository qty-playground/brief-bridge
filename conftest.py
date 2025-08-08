"""Root conftest.py for pytest configuration and shared fixtures"""

import pytest


class TestContext:
    """
    Test context for BDD step implementations following Command Pattern
    
    This is an empty shell - add attributes as needed for specific test scenarios.
    Each BDD scenario can dynamically add properties to store test data.
    
    Example usage in step modules:
        def invoke(ctx: TestContext):
            ctx.client_id = "test-client-123"
            ctx.response = some_api_response
            ctx.expected_status = 200
    """
    pass


@pytest.fixture
def context() -> TestContext:
    """Provide fresh TestContext instance for each test scenario"""
    return TestContext()