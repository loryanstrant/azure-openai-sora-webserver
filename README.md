# Azure OpenAI Sora Web Server 🎬

A comprehensive, production-ready web application for generating videos using Azure OpenAI's Sora model. This application provides both a modern web interface and a REST API for seamless video generation with real-time status tracking.

![Azure OpenAI Sora](https://img.shields.io/badge/Azure%20OpenAI-Sora-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## ✨ Features

### 🎨 Web Interface
- **Modern Responsive Design**: Beautiful, intuitive web interface that works on all devices
- **Real-time Progress Tracking**: Live updates on video generation status with progress bars
- **Interactive Controls**: Easy-to-use form controls for prompt, resolution, and duration
- **Error Handling**: User-friendly error messages with retry functionality
- **Video Preview**: Built-in video player with download capabilities

### 🚀 API Features
- **RESTful API**: Complete REST API with OpenAPI documentation
- **Async Processing**: Non-blocking video generation with background processing
- **Status Monitoring**: Real-time job status checking and progress updates
- **Health Checks**: Built-in health monitoring for production deployments
- **Input Validation**: Comprehensive request validation with Pydantic

### 🏗️ Production Ready
- **Docker Support**: Complete containerization with optimized Docker images
- **Configuration Management**: Environment-based configuration with validation
- **CI/CD Pipeline**: Automated testing, security scanning, and deployment
- **Security**: Input sanitization, non-root containers, dependency scanning
- **Monitoring**: Health checks, logging, and error tracking
- **Scalability**: Async operations and resource management

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.11 or higher
- Azure OpenAI account with Sora access
- Docker (optional, for containerized deployment)

### 1. Clone the Repository
```bash
git clone https://github.com/loryanstrant/Azure-OpenAI-Sora-webserver.git
cd Azure-OpenAI-Sora-webserver
```

### 2. Set Up Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Azure OpenAI credentials
nano .env
```

Required environment variables:
```bash
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application will be available at:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Using Docker directly
```bash
# Build the image
docker build -t sora-webserver .

# Run the container
docker run -d \
  --name sora-webserver \
  -p 8000:8000 \
  -e AZURE_OPENAI_API_KEY=your_key \
  -e AZURE_OPENAI_ENDPOINT=your_endpoint \
  sora-webserver
```

## 📖 API Documentation

### Generate Video
```http
POST /api/generate
Content-Type: application/json

{
  "prompt": "A beautiful sunset over the ocean with waves crashing on the shore",
  "resolution": "1920x1080",
  "duration": 5
}
```

**Response:**
```json
{
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending"
}
```

### Check Status
```http
GET /api/status/{video_id}
```

**Response:**
```json
{
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "progress": 100,
  "video_url": "https://...",
  "revised_prompt": "Enhanced prompt description"
}
```

### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "azure-openai-sora"
}
```

## 🎛️ Configuration

The application supports extensive configuration through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_OPENAI_API_KEY` | *Required* | Your Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | *Required* | Your Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_VERSION` | `2024-08-01-preview` | API version |
| `APP_HOST` | `0.0.0.0` | Host to bind the server |
| `APP_PORT` | `8000` | Port to run the server |
| `APP_DEBUG` | `false` | Enable debug mode |
| `MAX_CONCURRENT_JOBS` | `10` | Maximum concurrent video generations |
| `MAX_STORED_JOBS` | `50` | Maximum stored job histories |
| `JOB_CLEANUP_INTERVAL` | `3600` | Job cleanup interval (seconds) |

## 🧪 Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html
```

### Code Quality
```bash
# Install development tools
pip install black isort flake8 mypy bandit safety

# Format code
black app/ tests/
isort app/ tests/

# Lint code
flake8 app/ tests/ --max-line-length=88
mypy app/ --ignore-missing-imports

# Security checks
bandit -r app/
safety check
```

### Project Structure
```
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic models
│   ├── routes/
│   │   └── video.py         # API routes
│   ├── services/
│   │   └── azure_openai.py  # Azure OpenAI integration
│   ├── static/              # Frontend assets
│   │   ├── style.css
│   │   └── script.js
│   └── templates/           # HTML templates
│       └── index.html
├── tests/                   # Test suite
├── .github/workflows/       # CI/CD pipeline
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Docker Compose setup
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔒 Security

- **Input Validation**: All inputs are validated using Pydantic models
- **Environment Variables**: Sensitive data is managed through environment variables
- **Non-root Container**: Docker container runs as non-root user
- **Dependency Scanning**: Automated security scanning in CI/CD pipeline
- **HTTPS Ready**: Application is ready for reverse proxy with HTTPS termination

## 🚀 Deployment

### Azure Container Apps
```bash
# Create container app
az containerapp create \
  --name sora-webserver \
  --resource-group myResourceGroup \
  --environment myEnvironment \
  --image ghcr.io/loryanstrant/azure-openai-sora-webserver:latest \
  --env-vars AZURE_OPENAI_API_KEY=your_key AZURE_OPENAI_ENDPOINT=your_endpoint \
  --ingress external \
  --target-port 8000
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sora-webserver
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sora-webserver
  template:
    metadata:
      labels:
        app: sora-webserver
    spec:
      containers:
      - name: sora-webserver
        image: ghcr.io/loryanstrant/azure-openai-sora-webserver:latest
        ports:
        - containerPort: 8000
        env:
        - name: AZURE_OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: azure-openai-secret
              key: api-key
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/loryanstrant/Azure-OpenAI-Sora-webserver/issues)
- **Documentation**: [API Docs](http://localhost:8000/docs) (when running locally)
- **Azure OpenAI**: [Official Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)

## 🎉 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/)
- Containerized with [Docker](https://www.docker.com/)
- UI design inspired by modern web standards
