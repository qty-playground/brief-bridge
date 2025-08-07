import pytest
from fastapi.testclient import TestClient

from brief_bridge.main import app


@pytest.fixture
def test_client():
    """Provide a test client for FastAPI."""
    return TestClient(app)

# pytest_plugins will be populated during walking skeleton phase
