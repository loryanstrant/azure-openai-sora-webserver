"""Configuration settings for the Azure OpenAI Sora web server."""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    azure_openai_api_key: str
    azure_openai_api_version: str = "2024-02-01"
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = False
    
    # Video Generation Configuration
    max_video_length: int = 15  # Maximum video length in seconds
    default_video_length: int = 5  # Default video length in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()