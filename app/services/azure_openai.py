"""Azure OpenAI service for video generation using Sora."""

import asyncio
import os
import time
import uuid
from typing import Any

import httpx
from openai import AzureOpenAI

from ..models import VideoGenerationRequest, VideoStatus


class AzureOpenAIService:
    """Service for interacting with Azure OpenAI Sora API."""

    def __init__(self):
        """Initialize the Azure OpenAI service."""
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        )
        self.video_jobs: dict[str, VideoStatus] = {}
        # Store API configuration for HTTP requests
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    async def generate_video(self, request: VideoGenerationRequest) -> str:
        """Generate a video asynchronously."""
        video_id = str(uuid.uuid4())

        # Create initial job status
        self.video_jobs[video_id] = VideoStatus(
            video_id=video_id, status="pending", progress=0
        )

        # Start async generation
        asyncio.create_task(self._generate_video_async(request, video_id))

        return video_id

    async def _generate_video_async(
        self, request: VideoGenerationRequest, video_id: str
    ) -> None:
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

    def _parse_resolution(self, resolution: str) -> tuple[int, int]:
        """Parse resolution string into width and height."""
        try:
            width, height = resolution.split("x")
            return int(width), int(height)
        except (ValueError, AttributeError):
            # Default to HD if parsing fails
            return 1920, 1080

    def _call_sora_api(self, request: VideoGenerationRequest) -> dict[str, Any]:
        """Call the Sora API for video generation using HTTP requests."""
        # Parse resolution
        width, height = self._parse_resolution(request.resolution.value)

        # Prepare the request payload
        payload = {
            "model": "sora",
            "prompt": request.prompt,
            "height": str(height),
            "width": str(width),
            "n_seconds": str(request.duration),
            "n_variants": "1",
        }

        # Construct the endpoint URL
        url = f"{self.azure_endpoint.rstrip('/')}/openai/v1/video/generations/jobs"

        headers = {"Content-Type": "application/json", "Api-key": self.api_key}

        params = {"api-version": self.api_version}

        # Submit the job
        with httpx.Client() as client:
            response = client.post(
                url, json=payload, headers=headers, params=params, timeout=30.0
            )
            response.raise_for_status()
            job_data = response.json()

        # Get the job ID
        job_id = job_data.get("id")
        if not job_id:
            raise Exception("No job ID returned from API")

        # Poll for completion
        return self._poll_job_completion(job_id)

    def _poll_job_completion(self, job_id: str) -> dict[str, Any]:
        """Poll the job until completion and return the result."""
        url = f"{self.azure_endpoint.rstrip('/')}/openai/v1/video/generations/jobs/{job_id}"

        headers = {"Api-key": self.api_key}

        params = {"api-version": self.api_version}

        max_attempts = 60  # 10 minutes with 10-second intervals
        attempt = 0

        with httpx.Client() as client:
            while attempt < max_attempts:
                response = client.get(url, headers=headers, params=params, timeout=30.0)
                response.raise_for_status()
                job_data = response.json()

                status = job_data.get("status")

                if status == "succeeded":
                    # Extract the video data
                    outputs = job_data.get("outputs", [])
                    if outputs and len(outputs) > 0:
                        video_data = outputs[0]
                        return {
                            "video_url": video_data.get("url"),
                            "revised_prompt": job_data.get(
                                "revised_prompt", job_data.get("prompt")
                            ),
                        }
                    else:
                        raise Exception("No outputs in completed job")

                elif status == "failed":
                    error_msg = job_data.get("error", {}).get("message", "Job failed")
                    raise Exception(f"Video generation failed: {error_msg}")

                elif status in ["pending", "running"]:
                    # Continue polling
                    time.sleep(10)
                    attempt += 1
                else:
                    raise Exception(f"Unknown job status: {status}")

        raise Exception("Job did not complete within timeout")

    def get_video_status(self, video_id: str) -> VideoStatus | None:
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
