"""Video generation API routes."""

from fastapi import APIRouter, HTTPException, Depends
from ..models import VideoGenerationRequest, VideoStatus
from ..services.azure_openai import AzureOpenAIService

router = APIRouter(prefix="/api", tags=["video"])

# Dependency to get the Azure service
def get_azure_service() -> AzureOpenAIService:
    """Get the global Azure OpenAI service instance."""
    from ..main import azure_service
    if not azure_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return azure_service


@router.post("/generate", response_model=dict)
async def generate_video(
    request: VideoGenerationRequest, 
    service: AzureOpenAIService = Depends(get_azure_service)
):
    """Generate a video using Azure OpenAI Sora."""
    try:
        video_id = await service.generate_video(request)
        return {"video_id": video_id, "status": "pending"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{video_id}", response_model=VideoStatus)
async def get_video_status(
    video_id: str, 
    service: AzureOpenAIService = Depends(get_azure_service)
):
    """Get the status of a video generation job."""
    status = service.get_video_status(video_id)
    if not status:
        raise HTTPException(status_code=404, detail="Video job not found")
    return status


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "azure-openai-sora"}