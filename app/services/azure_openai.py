"""Azure OpenAI service for video generation using Sora."""

import asyncio
import os
import uuid
from typing import Dict, Optional, Any
from openai import AzureOpenAI

from ..models import VideoGenerationRequest, VideoStatus


class AzureOpenAIService:
    """Service for interacting with Azure OpenAI Sora API."""
    
    def __init__(self):
        """Initialize the Azure OpenAI service."""
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        )
        self.video_jobs: Dict[str, VideoStatus] = {}
    
    async def generate_video(self, request: VideoGenerationRequest) -> str:
        """Generate a video asynchronously."""
        video_id = str(uuid.uuid4())
        
        # Create initial job status
        self.video_jobs[video_id] = VideoStatus(
            video_id=video_id,
            status="pending",
            progress=0
        )
        
        # Start async generation
        asyncio.create_task(self._generate_video_async(request, video_id))
        
        return video_id
    
    async def _generate_video_async(self, request: VideoGenerationRequest, video_id: str) -> None:
        """Generate video asynchronously in background."""
        try:
            # Update status to processing
            self.video_jobs[video_id].status = "processing"
            self.video_jobs[video_id].progress = 25
            
            # Call Sora API
            result = self._call_sora_api(request)
            
            # Update with results
            self.video_jobs[video_id].status = "completed"
            self.video_jobs[video_id].progress = 100
            self.video_jobs[video_id].video_url = result.get("video_url")
            self.video_jobs[video_id].revised_prompt = result.get("revised_prompt")
            
        except Exception as e:
            self.video_jobs[video_id].status = "failed"
            self.video_jobs[video_id].progress = 0
            raise e
    
    def _call_sora_api(self, request: VideoGenerationRequest) -> Dict[str, Any]:
        """Call the Sora API for video generation."""
        response = self.client.videos.generate(
            model="sora",
            prompt=request.prompt,
            size=request.resolution.value,
            duration=request.duration
        )
        
        video_data = response.data[0]
        return {
            "video_url": video_data.url,
            "revised_prompt": video_data.revised_prompt
        }
    
    def get_video_status(self, video_id: str) -> Optional[VideoStatus]:
        """Get the status of a video generation job."""
        return self.video_jobs.get(video_id)
    
    def cleanup_old_jobs(self, max_jobs: int = 50) -> None:
        """Clean up old video jobs to prevent memory issues."""
        if len(self.video_jobs) > max_jobs:
            # Keep only the most recent jobs
            sorted_jobs = sorted(self.video_jobs.items(), key=lambda x: x[0])
            jobs_to_keep = dict(sorted_jobs[-max_jobs:])
            self.video_jobs.clear()
            self.video_jobs.update(jobs_to_keep)