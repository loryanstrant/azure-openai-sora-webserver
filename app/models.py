"""Data models for the Azure OpenAI Sora service."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class VideoResolution(str, Enum):
    """Video resolution options."""
    RES_1920x1080 = "1920x1080"
    RES_1280x720 = "1280x720"
    RES_1080x1920 = "1080x1920"


class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""
    prompt: str
    resolution: VideoResolution = VideoResolution.RES_1920x1080
    duration: int = 5


class VideoStatus(BaseModel):
    """Status model for video generation jobs."""
    video_id: str
    status: str
    progress: int = 0
    video_url: Optional[str] = None
    revised_prompt: Optional[str] = None