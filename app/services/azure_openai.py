"""Azure OpenAI service for Sora video generation."""

import logging
from typing import Optional, Dict, Any
from openai import AzureOpenAI
from app.config import settings
from app.models import VideoGenerationRequest, VideoStatus
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """Service for interacting with Azure OpenAI Sora."""
    
    def __init__(self):
        """Initialize the Azure OpenAI service (client will be created lazily)."""
        self._client = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Simple in-memory storage for video generation status
        # In production, this should be replaced with a proper database
        self.video_jobs: Dict[str, VideoStatus] = {}
    
    @property
    def client(self):
        """Lazy initialization of Azure OpenAI client."""
        if self._client is None:
            self._client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint
            )
        return self._client
    
    async def generate_video(self, request: VideoGenerationRequest) -> str:
        """
        Start video generation and return job ID.
        
        Args:
            request: Video generation request parameters
            
        Returns:
            Job ID for tracking the video generation progress
        """
        video_id = str(uuid.uuid4())
        
        # Initialize job status
        self.video_jobs[video_id] = VideoStatus(
            video_id=video_id,
            status="pending",
            progress=0
        )
        
        # Start video generation in background
        asyncio.create_task(self._generate_video_async(video_id, request))
        
        return video_id
    
    async def _generate_video_async(self, video_id: str, request: VideoGenerationRequest):
        """
        Async wrapper for video generation.
        
        Args:
            video_id: Unique identifier for the video generation job
            request: Video generation request parameters
        """
        try:
            # Update status to processing
            self.video_jobs[video_id].status = "processing"
            self.video_jobs[video_id].progress = 10
            
            logger.info(f"Starting video generation for job {video_id}")
            
            # Run the actual video generation in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._call_sora_api, 
                request
            )
            
            if result:
                self.video_jobs[video_id].status = "completed"
                self.video_jobs[video_id].progress = 100
                self.video_jobs[video_id].video_url = result.get("video_url")
                logger.info(f"Video generation completed for job {video_id}")
            else:
                self.video_jobs[video_id].status = "failed"
                self.video_jobs[video_id].error_message = "Failed to generate video"
                logger.error(f"Video generation failed for job {video_id}")
                
        except Exception as e:
            logger.error(f"Error in video generation for job {video_id}: {str(e)}")
            self.video_jobs[video_id].status = "failed"
            self.video_jobs[video_id].error_message = str(e)
    
    def _call_sora_api(self, request: VideoGenerationRequest) -> Optional[Dict[str, Any]]:
        """
        Call Azure OpenAI Sora API for video generation.
        
        Args:
            request: Video generation request parameters
            
        Returns:
            Dictionary containing video URL and metadata, or None if failed
        """
        try:
            # Prepare the video generation request
            video_request = {
                "prompt": request.prompt,
                "size": request.resolution.value,
                "duration": request.duration
            }
            
            logger.info(f"Calling Sora API with parameters: {video_request}")
            
            # Call Azure OpenAI Sora API
            response = self.client.videos.generate(
                model=settings.azure_openai_deployment_name,
                **video_request
            )
            
            # Extract video URL from response
            if response and hasattr(response, 'data') and response.data:
                video_data = response.data[0]
                return {
                    "video_url": getattr(video_data, 'url', None),
                    "revised_prompt": getattr(video_data, 'revised_prompt', None)
                }
                
        except Exception as e:
            logger.error(f"Error calling Sora API: {str(e)}")
            raise e
        
        return None
    
    def get_video_status(self, video_id: str) -> Optional[VideoStatus]:
        """
        Get the status of a video generation job.
        
        Args:
            video_id: Unique identifier for the video generation job
            
        Returns:
            VideoStatus object or None if job not found
        """
        return self.video_jobs.get(video_id)
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """
        Clean up old video generation jobs.
        
        Args:
            max_age_hours: Maximum age of jobs to keep in hours
        """
        # This is a simple cleanup - in production, you'd want to track creation time
        if len(self.video_jobs) > 100:  # Simple limit-based cleanup
            # Keep only the most recent 50 jobs
            job_ids = list(self.video_jobs.keys())
            for job_id in job_ids[:-50]:
                del self.video_jobs[job_id]


# Global service instance
azure_openai_service = AzureOpenAIService()