# Azure OpenAI Sora Video Generation Web Server

A fully containerized web server that connects to Sora in Azure OpenAI to generate videos with a modern, responsive web interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-00a393.svg)
![Docker](https://img.shields.io/badge/docker-ready-2496ed.svg)

## Features

✨ **Modern Web Interface**: Clean, responsive design with real-time progress tracking  
🎬 **Video Generation**: Powered by Azure OpenAI's Sora model  
📐 **Multiple Resolutions**: Support for landscape, portrait, and square formats  
⏱️ **Adjustable Duration**: Configurable video length from 1-15 seconds  
🐳 **Docker Ready**: Fully containerized with Docker Compose support  
🔄 **CI/CD Pipeline**: Automated testing and deployment to GitHub Container Registry  
🧪 **Comprehensive Testing**: Unit, integration, and error handling tests  
📊 **Health Monitoring**: Built-in health checks and logging  

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Azure OpenAI account with Sora model access
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/loryanstrant/Azure-OpenAI-Sora-webserver.git
   cd Azure-OpenAI-Sora-webserver
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure OpenAI credentials
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the web interface**
   Open http://localhost:8000 in your browser

### Using Pre-built Docker Image

```bash
docker run -p 8000:8000 \
  -e AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/ \
  -e AZURE_OPENAI_DEPLOYMENT_NAME=your-sora-deployment \
  -e AZURE_OPENAI_API_KEY=your-api-key \
  ghcr.io/loryanstrant/azure-openai-sora-webserver:latest
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | ✅ | - |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Sora deployment name | ✅ | - |
| `AZURE_OPENAI_API_KEY` | API key for authentication | ✅ | - |
| `AZURE_OPENAI_API_VERSION` | API version to use | ❌ | `2024-02-01` |
| `APP_HOST` | Host to bind the server | ❌ | `0.0.0.0` |
| `APP_PORT` | Port to bind the server | ❌ | `8000` |
| `APP_DEBUG` | Enable debug mode | ❌ | `false` |
| `MAX_VIDEO_LENGTH` | Maximum video duration (seconds) | ❌ | `15` |
| `DEFAULT_VIDEO_LENGTH` | Default video duration (seconds) | ❌ | `5` |

### Supported Video Resolutions

- **1920x1080** - Full HD Landscape
- **1080x1920** - Full HD Portrait  
- **1280x720** - HD Landscape
- **720x1280** - HD Portrait
- **1024x1024** - Square Format

## Development

### Local Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

2. **Set environment variables**
   ```bash
   export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   export AZURE_OPENAI_DEPLOYMENT_NAME=your-sora-deployment
   export AZURE_OPENAI_API_KEY=your-api-key
   ```

3. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_main.py -v
```

### Linting

```bash
# Install linting tools
pip install flake8 black isort

# Run linting
flake8 app/
black app/
isort app/
```

### Building Docker Image

```bash
# Build the image
docker build -t azure-openai-sora-webserver .

# Run the container
docker run -p 8000:8000 \
  -e AZURE_OPENAI_ENDPOINT=your-endpoint \
  -e AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment \
  -e AZURE_OPENAI_API_KEY=your-key \
  azure-openai-sora-webserver
```

## API Documentation

The application provides both a web interface and REST API endpoints:

### REST Endpoints

- **POST** `/api/video/generate` - Start video generation
- **GET** `/api/video/status/{video_id}` - Check generation status  
- **POST** `/api/video/cleanup` - Clean up old jobs
- **GET** `/health` - Health check endpoint
- **GET** `/docs` - Interactive API documentation

### Example API Usage

```bash
# Generate a video
curl -X POST "http://localhost:8000/api/video/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A majestic eagle soaring through mountain peaks",
    "resolution": "1920x1080",
    "duration": 10
  }'

# Check status
curl "http://localhost:8000/api/video/status/{video_id}"
```

## Architecture

```
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic models
│   ├── routes/              # API routes
│   │   └── video.py         # Video generation endpoints
│   ├── services/            # Business logic
│   │   └── azure_openai.py  # Azure OpenAI integration
│   ├── static/              # Static assets (CSS, JS)
│   └── templates/           # HTML templates
├── tests/                   # Test suite
├── Dockerfile              # Container definition
├── docker-compose.yml      # Multi-container setup
└── .github/workflows/       # CI/CD pipeline
```

## Monitoring and Logging

The application includes:

- **Health checks** at `/health` endpoint
- **Structured logging** with configurable levels
- **Request/response logging** for debugging
- **Error tracking** with detailed error messages
- **Performance monitoring** capabilities

## Security Features

- **Environment-based configuration** (no hardcoded secrets)
- **Input validation** with Pydantic models
- **Error handling** without exposing internal details
- **Security scanning** in CI/CD pipeline
- **Non-root container** execution

## Troubleshooting

### Common Issues

1. **Connection to Azure OpenAI fails**
   - Verify your endpoint URL and API key
   - Check that your deployment has Sora model access
   - Ensure network connectivity to Azure

2. **Video generation takes too long**
   - Check Azure OpenAI service status
   - Monitor the job status via `/api/video/status/{id}`
   - Verify your quota and rate limits

3. **Docker container won't start**
   - Check that all required environment variables are set
   - Verify port 8000 is not already in use
   - Check Docker logs: `docker logs <container_id>`

### Debug Mode

Enable debug mode for detailed logging:

```bash
export APP_DEBUG=true
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- 📖 Check the [documentation](https://github.com/loryanstrant/Azure-OpenAI-Sora-webserver)
- 🐛 Report issues on [GitHub Issues](https://github.com/loryanstrant/Azure-OpenAI-Sora-webserver/issues)
- 💬 Join discussions in [GitHub Discussions](https://github.com/loryanstrant/Azure-OpenAI-Sora-webserver/discussions)

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- UI components inspired by modern design principles
