"""FastAPI application for Azure OpenAI Sora video generation."""

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .models import VideoGenerationRequest, VideoStatus
from .services.azure_openai import AzureOpenAIService
from .routes import video
from .config import settings


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

# Setup paths
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Create directories if they don't exist
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API routes
app.include_router(video.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Azure OpenAI Sora Video Generator"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.app_host, 
        port=settings.app_port, 
        debug=settings.app_debug
    )