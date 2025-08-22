"""Test configuration and fixtures."""

import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "test-sora",
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-01"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_video_request():
    """Sample video generation request for testing."""
    return {
        "prompt": "A beautiful sunset over the ocean",
        "resolution": "1920x1080",
        "duration": 5
    }