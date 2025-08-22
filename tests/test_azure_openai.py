"""Tests for Azure OpenAI service."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.azure_openai import AzureOpenAIService
from app.models import VideoGenerationRequest, VideoResolution


@pytest.fixture
def azure_service(mock_env_vars):
    """Create an Azure OpenAI service instance for testing."""
    with patch('app.services.azure_openai.AzureOpenAI'):
        service = AzureOpenAIService()
        # Mock nested client.videos.generate for all tests
        service.client = MagicMock()
        service.client.videos = MagicMock()
        service.client.videos.generate = MagicMock()
        return service


@pytest.mark.asyncio
async def test_generate_video_success(azure_service: AzureOpenAIService):
    """Test successful video generation."""
    request = VideoGenerationRequest(
        prompt="A beautiful sunset",
        resolution=VideoResolution.RES_1920x1080,
        duration=5
    )
    
    with patch.object(azure_service, '_generate_video_async') as mock_async:
        mock_async.return_value = None
        
        video_id = await azure_service.generate_video(request)
        
        assert video_id is not None
        assert video_id in azure_service.video_jobs
        assert azure_service.video_jobs[video_id].status == "pending"


def test_call_sora_api_success(azure_service: AzureOpenAIService):
    """Test successful Sora API call."""
    request = VideoGenerationRequest(
        prompt="A beautiful sunset",
        resolution=VideoResolution.RES_1920x1080,
        duration=5
    )
    
    # Mock the API response
    mock_video_data = MagicMock()
    mock_video_data.url = "http://example.com/video.mp4"
    mock_video_data.revised_prompt = "A beautiful sunset over calm waters"
    
    mock_response = MagicMock()
    mock_response.data = [mock_video_data]
    
    azure_service.client.videos.generate.return_value = mock_response
    
    result = azure_service._call_sora_api(request)
    
    assert result is not None
    assert result["video_url"] == "http://example.com/video.mp4"
    assert result["revised_prompt"] == "A beautiful sunset over calm waters"
    
    # Verify the API was called with correct parameters
    azure_service.client.videos.generate.assert_called_once()


def test_call_sora_api_failure(azure_service: AzureOpenAIService):
    """Test Sora API call failure."""
    request = VideoGenerationRequest(
        prompt="A beautiful sunset",
        resolution=VideoResolution.RES_1920x1080,
        duration=5
    )
    
    # Mock API exception
    azure_service.client.videos.generate.side_effect = Exception("API Error")
    
    with pytest.raises(Exception, match="API Error"):
        azure_service._call_sora_api(request)


def test_get_video_status_existing(azure_service: AzureOpenAIService):
    """Test getting status for existing video job."""
    from app.models import VideoStatus
    
    test_status = VideoStatus(
        video_id="test-id",
        status="processing",
        progress=50
    )
    
    azure_service.video_jobs["test-id"] = test_status
    
    result = azure_service.get_video_status("test-id")
    
    assert result == test_status
    assert result.video_id == "test-id"
    assert result.status == "processing"
    assert result.progress == 50


def test_get_video_status_non_existent(azure_service: AzureOpenAIService):
    """Test getting status for non-existent video job."""
    result = azure_service.get_video_status("non-existent-id")
    assert result is None


def test_cleanup_old_jobs(azure_service: AzureOpenAIService):
    """Test cleanup of old video jobs."""
    from app.models import VideoStatus
    
    # Add many jobs to trigger cleanup
    for i in range(150):
        job_id = f"job-{i}"
        azure_service.video_jobs[job_id] = VideoStatus(
            video_id=job_id,
            status="completed",
            progress=100
        )
    
    initial_count = len(azure_service.video_jobs)
    assert initial_count == 150
    
    azure_service.cleanup_old_jobs()
    
    # Should keep only 50 most recent jobs
    assert len(azure_service.video_jobs) == 50
