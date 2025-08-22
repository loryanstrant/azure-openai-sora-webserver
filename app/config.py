"""Configuration management using Pydantic settings."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: str = "2024-08-01-preview"
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = False
    
    # Job Management
    max_concurrent_jobs: int = 10
    max_stored_jobs: int = 50
    job_cleanup_interval: int = 3600  # seconds


# Global settings instance
settings = Settings()