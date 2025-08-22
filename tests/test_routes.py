"""Tests for video generation routes."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.models import VideoStatus


def test_generate_video_success(test_client: TestClient, mock_env_vars, sample_video_request):
    """Test successful video generation request."""
    with patch('app.services.azure_openai.azure_openai_service.generate_video') as mock_generate:
        mock_generate.return_value = "test-video-id-123"
        
        response = test_client.post("/api/video/generate", json=sample_video_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["video_id"] == "test-video-id-123"
        assert "started successfully" in data["message"]


def test_generate_video_validation_error(test_client: TestClient, mock_env_vars):
    """Test video generation with invalid request data."""
    invalid_request = {
        "prompt": "",  # Empty prompt should fail validation
        "resolution": "1920x1080",
        "duration": 5
    }
    
    response = test_client.post("/api/video/generate", json=invalid_request)
    assert response.status_code == 422  # Validation error


def test_generate_video_duration_validation(test_client: TestClient, mock_env_vars):
    """Test video generation with invalid duration."""
    invalid_request = {
        "prompt": "Test prompt",
        "resolution": "1920x1080",
        "duration": 20  # Too long, max is 15
    }
    
    response = test_client.post("/api/video/generate", json=invalid_request)
    assert response.status_code == 422  # Validation error


def test_get_video_status_success(test_client: TestClient, mock_env_vars):
    """Test successful video status retrieval."""
    test_status = VideoStatus(
        video_id="test-id",
        status="completed",
        progress=100,
        video_url="http://example.com/video.mp4"
    )
    
    with patch('app.services.azure_openai.azure_openai_service.get_video_status') as mock_status:
        mock_status.return_value = test_status
        
        response = test_client.get("/api/video/status/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["video_id"] == "test-id"
        assert data["status"] == "completed"
        assert data["progress"] == 100
        assert data["video_url"] == "http://example.com/video.mp4"


def test_get_video_status_not_found(test_client: TestClient, mock_env_vars):
    """Test video status retrieval for non-existent job."""
    with patch('app.services.azure_openai.azure_openai_service.get_video_status') as mock_status:
        mock_status.return_value = None
        
        response = test_client.get("/api/video/status/non-existent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


def test_cleanup_old_jobs(test_client: TestClient, mock_env_vars):
    """Test cleanup endpoint."""
    with patch('app.services.azure_openai.azure_openai_service.cleanup_old_jobs') as mock_cleanup:
        mock_cleanup.return_value = None
        
        response = test_client.post("/api/video/cleanup")
        
        assert response.status_code == 200
        assert "cleaned up successfully" in response.json()["message"]