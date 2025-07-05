# SnapBrand.ai - AI-Powered Brand Asset Studio

A production-ready AI-powered brand asset studio that generates on-brand images using Amazon Bedrock's Stable Diffusion models. Built with Next.js frontend and FastAPI backend.

## 🚀 Features

- **AI Image Generation**: Powered by Amazon Bedrock Stable Diffusion XL
- **Template System**: 8 pre-built templates for various use cases
- **Batch Processing**: Generate multiple images with real-time progress tracking
- **Brand Asset Management**: Upload and manage brand assets with S3 integration
- **Rate Limiting**: Production-ready rate limiting and API key authentication
- **Real-time Updates**: Live progress tracking for batch operations
- **Responsive UI**: Modern, mobile-friendly interface built with Tailwind CSS

## 📋 Prerequisites

- **Node.js** 18+ and pnpm/npm
- **Python** 3.11+
- **AWS Account** with Bedrock and S3 access
- **Docker** (optional, for containerized deployment)

## 🛠 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd snapbrand-ai

# Run the automated setup script
./start.sh setup

# Start the application
./start.sh start
```

### Option 2: Docker Compose

```bash
# Set up environment variables
cp backend/.env.example .env
# Edit .env with your AWS credentials

# Start with Docker
./start.sh docker
```

### Option 3: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup

```bash
# Install dependencies
pnpm install

# Start the frontend
pnpm dev
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
BEDROCK_MODEL_ID=stability.stable-diffusion-xl-v1
S3_BUCKET_NAME=your-bucket-name

# Application Configuration
APP_NAME=SnapBrand.ai Backend
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# Security & CORS
CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]
API_KEYS=["your-api-key-1", "your-api-key-2"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# S3 Configuration
PRESIGN_EXPIRATION=3600
MAX_FILE_SIZE_MB=10

# Bedrock Configuration
MAX_IMAGES_PER_REQUEST=10
DEFAULT_IMAGE_SIZE=1024x1024
```

### Frontend Configuration

Set environment variables for the frontend:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI   │───▶│  FastAPI Backend │───▶│  Amazon Bedrock │
│  (Port 3000)   │    │   (Port 8000)    │    │  (Image Gen)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │   Amazon S3     │              │
         └──────────────│ (Asset Storage) │◀─────────────┘
                        └─────────────────┘
```

## 📚 API Documentation

### Core Endpoints

- `GET /health` - Health check with service status
- `POST /v1/generate` - Generate single image
- `POST /v1/batch/generate` - Create batch generation job
- `GET /v1/batch/{id}/status` - Get batch job status
- `GET /v1/templates` - List available templates
- `GET /v1/assets/upload-url` - Get presigned upload URL

### Authentication

All generation endpoints require API key authentication:

```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A professional product photo",
    "template_id": "product-hero",
    "num_images": 1
  }'
```

### Templates

Built-in templates include:
- `product-hero` - Product photography
- `instagram-post` - Social media content
- `lifestyle-scene` - Lifestyle photography
- `email-header` - Email marketing headers
- `website-banner` - Website hero banners
- `linkedin-post` - Professional content
- `product-catalog` - Catalog layouts
- `seasonal-campaign` - Seasonal marketing

## 🚀 Deployment

### AWS App Runner (Recommended)

1. **Set up AWS CDK infrastructure**:
   ```bash
   cd infrastructure
   npm install
   cdk deploy
   ```

2. **Build and push Docker image**:
   ```bash
   # Build image
   docker build -f backend/Dockerfile -t snapbrand-backend .
   
   # Tag and push to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag snapbrand-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/snapbrand-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/snapbrand-backend:latest
   ```

3. **Deploy frontend to Vercel**:
   ```bash
   # Set environment variables in Vercel
   NEXT_PUBLIC_API_URL=https://your-app-runner-url.amazonaws.com
   
   # Deploy
   vercel --prod
   ```

### Docker Compose (Development)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔍 Monitoring & Logging

### Health Checks

- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000`

### Logs

- Backend logs: `backend.log`
- Frontend logs: `frontend.log`
- Docker logs: `docker-compose logs`

### Service Status

```bash
# Check service status
./start.sh status

# View recent logs
tail -f backend.log
tail -f frontend.log
```

## 🛡 Security Features

- **API Key Authentication**: Secure endpoint access
- **Rate Limiting**: 60 requests/minute, 1000/hour per IP
- **CORS Protection**: Configurable allowed origins
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error responses without sensitive data
- **Presigned URLs**: Secure S3 access without exposing credentials

## 🧪 Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/
```

### Frontend Tests

```bash
pnpm test
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test generation (requires API key)
curl -X POST http://localhost:8000/v1/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test image", "num_images": 1}'
```

## 🔧 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Check what's using the port
   lsof -i :8000
   lsof -i :3000
   
   # Kill the process
   kill -9 <PID>
   ```

2. **AWS credentials not found**:
   ```bash
   # Configure AWS CLI
   aws configure
   
   # Or set environment variables
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   ```

3. **Python dependencies issues**:
   ```bash
   # Recreate virtual environment
   rm -rf backend/venv
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Docker issues**:
   ```bash
   # Clean up Docker
   docker-compose down
   docker system prune -f
   docker-compose up --build
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Backend
export DEBUG=true
export LOG_LEVEL=DEBUG

# Frontend
export NODE_ENV=development
```

## 📈 Performance Optimization

### Production Settings

- Set `DEBUG=false` in production
- Use `LOG_LEVEL=WARNING` or `ERROR` in production
- Enable CDN for static assets
- Use Redis for session storage (optional)
- Configure proper rate limits based on usage

### Scaling

- Use AWS App Runner auto-scaling
- Implement database for persistent storage
- Add Redis for caching and session management
- Use CloudFront for global distribution

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at `http://localhost:8000/docs`

## 🎯 Roadmap

- [ ] Database integration for persistent storage
- [ ] User authentication and management
- [ ] Advanced image editing features
- [ ] Custom model fine-tuning
- [ ] Analytics and usage tracking
- [ ] Multi-tenant support
- [ ] Advanced template editor
- [ ] Integration with design tools 