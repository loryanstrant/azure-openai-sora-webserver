# Azure OpenAI Sora Video Generator Web Server

A production-ready, containerized web server that connects to Azure OpenAI's Sora model to generate videos. This application provides both a modern web interface and RESTful API endpoints for video generation.

## 🚀 Features

- **Modern FastAPI Web Server**: Built with FastAPI using modern async patterns and lifespan handlers
- **Web Interface**: Intuitive HTML/CSS/JavaScript frontend for easy video generation
- **RESTful API**: Complete API with automatic documentation via FastAPI
- **Azure OpenAI Integration**: Seamless connection to Azure OpenAI Sora video generation
- **Containerized**: Multi-stage Docker build with security best practices
- **Comprehensive Testing**: Unit, integration, and API tests with mocking
- **Code Quality**: Linting, formatting, and type checking with Ruff and Black
- **CI/CD Pipeline**: GitHub Actions workflow with automated testing and deployment
- **Health Monitoring**: Built-in health checks and logging
- **Security**: Container runs as non-root user, vulnerability scanning with Trivy

## 📋 Requirements

- Python 3.11+
- Docker (for containerized deployment)
- Azure OpenAI account with Sora access
- Azure OpenAI API key and endpoint

## 🔧 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | Yes | - |
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint URL | Yes | - |
| `AZURE_OPENAI_API_VERSION` | API version | No | `2024-08-01-preview` |

## 🏗️ Installation & Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/loryanstrant/Azure-OpenAI-Sora-webserver.git
   cd Azure-OpenAI-Sora-webserver
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export AZURE_OPENAI_API_KEY="your-api-key"
   export AZURE_OPENAI_ENDPOINT="https://your-instance.openai.azure.com/"
   export AZURE_OPENAI_API_VERSION="2024-08-01-preview"
   ```

4. **Run the application**
   ```bash
   python -m app.main
   ```

5. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t azure-openai-sora-webserver .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name sora-webserver \
     -p 8000:8000 \
     -e AZURE_OPENAI_API_KEY="your-api-key" \
     -e AZURE_OPENAI_ENDPOINT="https://your-instance.openai.azure.com/" \
     azure-openai-sora-webserver
   ```

3. **Access the application**
   - Web Interface: http://localhost:8000
   - Health Check: http://localhost:8000/health

### Using GitHub Container Registry

The application is automatically built and published to GitHub Container Registry (GHCR):

```bash
docker pull ghcr.io/loryanstrant/azure-openai-sora-webserver:latest
docker run -d \
  --name sora-webserver \
  -p 8000:8000 \
  -e AZURE_OPENAI_API_KEY="your-api-key" \
  -e AZURE_OPENAI_ENDPOINT="https://your-instance.openai.azure.com/" \
  ghcr.io/loryanstrant/azure-openai-sora-webserver:latest
```

## 🎯 Usage

### Web Interface

1. Navigate to http://localhost:8000
2. Enter your video description in the prompt field
3. Select resolution (1920x1080, 1280x720, or 1080x1920)
4. Set duration (1-30 seconds)
5. Click "Generate Video"
6. Monitor progress and view the generated video

### API Endpoints

#### Generate Video
```bash
POST /generate
Content-Type: application/json

{
  "prompt": "A beautiful sunset over the ocean",
  "resolution": "1920x1080",
  "duration": 5
}
```

#### Check Video Status
```bash
GET /status/{video_id}
```

#### Health Check
```bash
GET /health
```

### API Response Examples

**Generate Video Response:**
```json
{
  "video_id": "uuid-string",
  "status": "pending"
}
```

**Status Response:**
```json
{
  "video_id": "uuid-string",
  "status": "completed",
  "progress": 100,
  "video_url": "https://example.com/video.mp4",
  "revised_prompt": "Enhanced prompt used for generation"
}
```

## 🧪 Testing

Run the complete test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_azure_openai.py -v     # Unit tests
pytest tests/test_fastapi.py -v          # FastAPI tests
pytest tests/test_integration.py -v      # Integration tests

# Run with coverage
coverage run -m pytest tests/
coverage report --show-missing
```

## 🔍 Code Quality

The project uses modern Python development tools:

```bash
# Linting with Ruff
ruff check app/ tests/

# Code formatting with Black
black app/ tests/

# Import sorting with isort
isort app/ tests/

# Type checking (if mypy is added)
mypy app/
```

## 🔧 Development

### Project Structure
```
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   └── services/
│       ├── __init__.py
│       └── azure_openai.py  # Azure OpenAI service
├── static/
│   └── index.html           # Web interface
├── tests/
│   ├── conftest.py          # Test configuration
│   ├── test_azure_openai.py # Unit tests
│   ├── test_fastapi.py      # FastAPI tests
│   └── test_integration.py  # Integration tests
├── .github/workflows/
│   └── ci-cd.yml           # CI/CD pipeline
├── Dockerfile              # Multi-stage container build
├── requirements.txt        # Python dependencies
└── pyproject.toml         # Tool configuration
```

### Adding New Features

1. Create feature branch from `main`
2. Add tests first (TDD approach)
3. Implement the feature
4. Ensure all tests pass
5. Run code quality checks
6. Submit pull request

## 🚀 CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **Code Quality**: Runs linting, formatting, and type checks
2. **Testing**: Executes all tests across Python 3.11 and 3.12
3. **Security**: Performs vulnerability scanning with Trivy
4. **Build**: Creates Docker image with multi-stage build
5. **Publish**: Pushes image to GitHub Container Registry
6. **Deploy**: Integration testing with built container

## 🔒 Security Features

- **Non-root container execution**: Application runs as dedicated user
- **Dependency scanning**: Automated vulnerability checks
- **Multi-stage builds**: Reduced attack surface in production image
- **Health checks**: Container health monitoring
- **Input validation**: Comprehensive request validation with Pydantic

## 📊 Monitoring & Logging

- **Health endpoint**: `/health` for service monitoring
- **Structured logging**: JSON logs for production environments
- **Progress tracking**: Real-time video generation progress
- **Error handling**: Comprehensive error messages and status codes

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: https://github.com/loryanstrant/Azure-OpenAI-Sora-webserver/issues
- **Discussions**: https://github.com/loryanstrant/Azure-OpenAI-Sora-webserver/discussions
- **Documentation**: See the `/docs` endpoint when running the application

## 🙏 Acknowledgments

- Azure OpenAI for providing Sora video generation capabilities
- FastAPI for the excellent web framework
- The Python community for outstanding tooling and libraries
