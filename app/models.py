"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class VideoResolution(str, Enum):
    """Supported video resolutions for Sora."""
    RES_1920x1080 = "1920x1080"
    RES_1080x1920 = "1080x1920"
    RES_1280x720 = "1280x720"
    RES_720x1280 = "720x1280"
    RES_1024x1024 = "1024x1024"


class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Video generation prompt")
    resolution: VideoResolution = Field(default=VideoResolution.RES_1920x1080, description="Video resolution")
    duration: int = Field(default=5, ge=1, le=15, description="Video duration in seconds")


class VideoGenerationResponse(BaseModel):
    """Response model for video generation."""
    success: bool
    message: str
    video_url: Optional[str] = None
    video_id: Optional[str] = None
    error_details: Optional[str] = None


class VideoStatus(BaseModel):
    """Model for video generation status."""
    video_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    progress: Optional[int] = None  # Percentage (0-100)
    video_url: Optional[str] = None
    error_message: Optional[str] = None