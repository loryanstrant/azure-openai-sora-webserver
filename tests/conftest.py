"""Test configuration and fixtures."""

import pytest
from unittest.mock import patch


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict('os.environ', {
        'AZURE_OPENAI_API_KEY': 'test-api-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-08-01-preview'
    }):
        yield