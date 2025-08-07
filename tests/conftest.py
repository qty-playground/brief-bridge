import pytest
from fastapi.testclient import TestClient

from brief_bridge.main import app


@pytest.fixture
def test_client():
    """Provide a test client for FastAPI."""
    return TestClient(app)

pytest_plugins = [
    "tests.register_client_use_case.given_steps",
    "tests.register_client_use_case.when_steps",
    "tests.register_client_use_case.then_steps",
]
