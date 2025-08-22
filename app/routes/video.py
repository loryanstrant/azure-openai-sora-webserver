"""Video generation routes."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.models import VideoGenerationRequest, VideoGenerationResponse, VideoStatus
from app.services.azure_openai import azure_openai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video", tags=["video"])


@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest):
    """
    Generate a video using Azure OpenAI Sora.
    
    Args:
        request: Video generation parameters
        
    Returns:
        VideoGenerationResponse with job ID for tracking progress
    """
    try:
        logger.info(f"Received video generation request: {request.prompt[:50]}...")
        
        # Start video generation
        video_id = await azure_openai_service.generate_video(request)
        
        return VideoGenerationResponse(
            success=True,
            message="Video generation started successfully",
            video_id=video_id
        )
        
    except Exception as e:
        logger.error(f"Error starting video generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start video generation: {str(e)}"
        )


@router.get("/status/{video_id}", response_model=VideoStatus)
async def get_video_status(video_id: str):
    """
    Get the status of a video generation job.
    
    Args:
        video_id: Unique identifier for the video generation job
        
    Returns:
        VideoStatus with current progress and completion status
    """
    try:
        status = azure_openai_service.get_video_status(video_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Video job {video_id} not found"
            )
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get video status: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_old_jobs():
    """
    Clean up old video generation jobs.
    
    Returns:
        Success message
    """
    try:
        azure_openai_service.cleanup_old_jobs()
        return {"message": "Old jobs cleaned up successfully"}
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup old jobs: {str(e)}"
        )