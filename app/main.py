"""FastAPI application for Azure OpenAI Sora video generation."""

import asyncio
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .models import VideoGenerationRequest, VideoStatus
from .services.azure_openai import AzureOpenAIService


# Global service instance
azure_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    global azure_service
    azure_service = AzureOpenAIService()
    print("Starting Azure OpenAI Sora Web Server...")
    
    yield
    
    # Shutdown
    print("Shutting down Azure OpenAI Sora Web Server...")
    # Clean up any pending tasks
    if azure_service:
        azure_service.cleanup_old_jobs()
    print("Cleanup completed.")


# Create FastAPI app with lifespan handler
app = FastAPI(
    title="Azure OpenAI Sora Video Generator",
    description="A web server for generating videos using Azure OpenAI Sora",
    version="1.0.0",
    lifespan=lifespan
)


@app.post("/generate", response_model=dict)
async def generate_video(request: VideoGenerationRequest):
    """Generate a video using Azure OpenAI Sora."""
    try:
        video_id = await azure_service.generate_video(request)
        return {"video_id": video_id, "status": "pending"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{video_id}", response_model=VideoStatus)
async def get_video_status(video_id: str):
    """Get the status of a video generation job."""
    status = azure_service.get_video_status(video_id)
    if not status:
        raise HTTPException(status_code=404, detail="Video job not found")
    return status


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "azure-openai-sora"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)