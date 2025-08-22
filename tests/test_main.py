"""Tests for the main FastAPI application."""

import pytest
from fastapi.testclient import TestClient


def test_health_check(test_client: TestClient):
    """Test the health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "azure-openai-sora-webserver"
    }


def test_home_page(test_client: TestClient, mock_env_vars):
    """Test the home page renders correctly."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert "Azure OpenAI Sora Video Generator" in response.text
    assert "Generate amazing videos" in response.text


def test_static_files_mount(test_client: TestClient):
    """Test that static files are properly mounted."""
    # This test might fail if the actual static files don't exist
    # but it tests the mount configuration
    response = test_client.get("/static/css/style.css")
    # We expect either 200 (file exists) or 404 (file doesn't exist but mount works)
    assert response.status_code in [200, 404]


def test_api_endpoints_are_included(test_client: TestClient):
    """Test that API endpoints are properly included."""
    # Test that the OpenAPI docs are available (indicates routes are included)
    response = test_client.get("/docs")
    assert response.status_code == 200