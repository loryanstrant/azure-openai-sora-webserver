"""Tests for Azure OpenAI service."""

from unittest.mock import MagicMock, patch
import httpx

import pytest

from app.models import VideoGenerationRequest, VideoResolution
from app.services.azure_openai import AzureOpenAIService


@pytest.fixture
def azure_service(mock_env_vars):
    """Create an Azure OpenAI service instance for testing."""
    with patch("app.services.azure_openai.AzureOpenAI"):
        service = AzureOpenAIService()
        return service


@pytest.mark.asyncio
async def test_generate_video_success(azure_service: AzureOpenAIService):
    """Test successful video generation."""
    request = VideoGenerationRequest(
        prompt="A beautiful sunset",
        resolution=VideoResolution.RES_1920x1080,
        duration=5,
    )

    with patch.object(azure_service, "_generate_video_async") as mock_async:
        mock_async.return_value = None

        video_id = await azure_service.generate_video(request)

        assert video_id is not None
        assert video_id in azure_service.video_jobs
        assert azure_service.video_jobs[video_id].status == "pending"


def test_parse_resolution(azure_service: AzureOpenAIService):
    """Test resolution parsing."""
    # Test valid resolutions
    assert azure_service._parse_resolution("1920x1080") == (1920, 1080)
    assert azure_service._parse_resolution("1280x720") == (1280, 720)
    assert azure_service._parse_resolution("1080x1920") == (1080, 1920)
    
    # Test invalid resolution - should default to HD
    assert azure_service._parse_resolution("invalid") == (1920, 1080)
    assert azure_service._parse_resolution("") == (1920, 1080)
    assert azure_service._parse_resolution("1920") == (1920, 1080)


@patch('httpx.Client')
def test_call_sora_api_success(mock_client_class, azure_service: AzureOpenAIService):
    """Test successful Sora API call."""
    request = VideoGenerationRequest(
        prompt="A beautiful sunset",
        resolution=VideoResolution.RES_1920x1080,
        duration=5,
    )

    # Mock the HTTP client and responses
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    # Mock job submission response
    mock_submit_response = MagicMock()
    mock_submit_response.json.return_value = {"id": "job-123"}
    mock_client.post.return_value = mock_submit_response
    
    # Mock job polling response (completed)
    mock_poll_response = MagicMock()
    mock_poll_response.json.return_value = {
        "status": "succeeded",
        "outputs": [{
            "url": "http://example.com/video.mp4"
        }],
        "revised_prompt": "A beautiful sunset over calm waters"
    }
    mock_client.get.return_value = mock_poll_response

    result = azure_service._call_sora_api(request)

    assert result is not None
    assert result["video_url"] == "http://example.com/video.mp4"
    assert result["revised_prompt"] == "A beautiful sunset over calm waters"

    # Verify the HTTP calls were made
    mock_client.post.assert_called_once()
    mock_client.get.assert_called_once()


@patch('httpx.Client')
def test_call_sora_api_failure(mock_client_class, azure_service: AzureOpenAIService):
    """Test Sora API call failure."""
    request = VideoGenerationRequest(
        prompt="A beautiful sunset",
        resolution=VideoResolution.RES_1920x1080,
        duration=5,
    )

    # Mock the HTTP client to raise an exception
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    mock_client.post.side_effect = httpx.HTTPStatusError(
        "API Error", request=MagicMock(), response=MagicMock()
    )

    with pytest.raises(httpx.HTTPStatusError):
        azure_service._call_sora_api(request)


@patch('httpx.Client')
def test_call_sora_api_job_failed(mock_client_class, azure_service: AzureOpenAIService):
    """Test Sora API call when job fails."""
    request = VideoGenerationRequest(
        prompt="A beautiful sunset",
        resolution=VideoResolution.RES_1920x1080,
        duration=5,
    )

    # Mock the HTTP client and responses
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    # Mock job submission response
    mock_submit_response = MagicMock()
    mock_submit_response.json.return_value = {"id": "job-123"}
    mock_client.post.return_value = mock_submit_response
    
    # Mock job polling response (failed)
    mock_poll_response = MagicMock()
    mock_poll_response.json.return_value = {
        "status": "failed",
        "error": {
            "message": "Video generation failed due to content policy"
        }
    }
    mock_client.get.return_value = mock_poll_response

    with pytest.raises(
    Exception,
    match="Video generation failed: Video generation failed due to content policy",
):
    azure_service._call_sora_api(request)


def test_get_video_status_existing(azure_service: AzureOpenAIService):
    """Test getting status for existing video job."""
    from app.models import VideoStatus

    test_status = VideoStatus(video_id="test-id", status="processing", progress=50)

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
            video_id=job_id, status="completed", progress=100
        )

    initial_count = len(azure_service.video_jobs)
    assert initial_count == 150

    azure_service.cleanup_old_jobs()

    # Should keep only 50 most recent jobs
    assert len(azure_service.video_jobs) == 50
