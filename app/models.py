"""Data models for the Azure OpenAI Sora service."""

from enum import Enum

from pydantic import BaseModel, Field


class VideoResolution(str, Enum):
    """Video resolution options."""

    RES_1920x1080 = "1920x1080"
    RES_1280x720 = "1280x720"
    RES_1080x1920 = "1080x1920"


class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""

    prompt: str = Field(
        ..., min_length=1, max_length=1000, description="Video description prompt"
    )
    resolution: VideoResolution = VideoResolution.RES_1920x1080
    duration: int = Field(
        default=5, ge=1, le=30, description="Video duration in seconds"
    )


class VideoStatus(BaseModel):
    """Status model for video generation jobs."""

    video_id: str
    status: str
    progress: int = Field(default=0, ge=0, le=100)
    video_url: str | None = None
    revised_prompt: str | None = None
