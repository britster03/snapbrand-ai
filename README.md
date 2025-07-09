# SnapBrand.ai - Professional AI Image Generation Platform

🚀 **Production-ready AI image generation system** built for hackathons and professional use cases. Generate high-quality, brand-consistent images using state-of-the-art diffusion models with professional standards and industry guidelines.

## 🌟 Key Features

### 🎨 Professional Image Generation
- **Amazon Titan V2**: Latest generation AI model with superior prompt adherence and quality
- **Advanced Prompt Engineering**: Industry-standard prompt enhancement with professional guidelines
- **Quality Controls**: 4 quality levels (Standard, High, Ultra, Professional) with automated validation
- **Style Categories**: Photorealistic, Artistic, Technical, Marketing, Product Photography
- **Composition Rules**: Rule of thirds, Golden ratio, Leading lines, Symmetry, Center composition
- **Lighting Presets**: Professional, Studio, Natural, Dramatic, Soft, Golden hour

### 🖼️ Vector Image Generation
- **SVG Generation**: Create scalable vector graphics from text prompts
- **Vector Styles**: Modern, Minimalist, Artistic, Geometric, Organic
- **Multiple Formats**: Raw SVG or Base64 encoded output
- **Intelligent Design**: Automatic color and shape extraction from prompts
- **Professional Quality**: Clean, scalable graphics perfect for branding

### 🏢 Brand Consistency
- **Brand Asset Management**: Upload and manage logos, color palettes, sample images
- **Style Presets**: Professional, Vibrant, Minimal, Luxury brand styles
- **Color Integration**: Automatic color palette application to generations
- **Template System**: Professional templates for various use cases

### 📊 Production Features
- **Real-time Cost Tracking**: AWS Bedrock pricing integration ($0.04/image)
- **Credits System**: 1 credit = $0.01 USD for transparent billing
- **Batch Processing**: Generate multiple images efficiently
- **Quality Validation**: Automated image quality assessment
- **Usage Analytics**: Track generation statistics and costs

### 🔧 Technical Excellence
- **AWS Integration**: Bedrock for generation, S3 for storage
- **FastAPI Backend**: High-performance Python API
- **Next.js Frontend**: Modern React-based UI
- **Professional UI**: shadcn/ui components with responsive design
- **Authentication**: JWT-based secure authentication

## 🏗️ Architecture

```
Frontend (Next.js)     Backend (FastAPI)       AWS Services
├── Dashboard          ├── Generation API      ├── Bedrock (AI Models)
├── Generate Page      ├── Template System     ├── S3 (Storage)
├── Vector Generate    ├── Vector Engine       └── IAM (Security)
├── Brand Assets       ├── Prompt Engineering
├── Batch Processing   ├── Quality Validation
└── Analytics          └── Cost Tracking
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- AWS Account with Bedrock access
- Docker (optional)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/snapbrand-ai.git
cd snapbrand-ai
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials and settings

# Initialize database
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend  # or root directory
npm install
npm run dev
```

### 4. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🎯 Professional Templates

### Product Photography
- **Product Hero**: Studio lighting, center composition, professional grade
- **Luxury Brand**: Dramatic lighting, symmetrical composition, premium quality

### Marketing Content
- **Social Media**: Rule of thirds, natural lighting, high quality
- **Website Hero**: Golden ratio, professional lighting, ultra quality
- **Email Headers**: Leading lines, professional lighting, marketing style

### Technical Content
- **Technical Illustrations**: Precise documentation style, soft lighting
- **Corporate Headshots**: Studio lighting, professional composition

## 📈 Quality Standards

### Quality Levels
1. **Standard**: Good for basic use cases (512px+, basic quality checks)
2. **High**: Suitable for most professional needs (768px+, enhanced quality)
3. **Ultra**: Premium quality for important content (1024px+, strict validation)
4. **Professional**: Industry-grade for critical applications (1024px+, comprehensive validation)

### Validation Metrics
- **Resolution**: Minimum dimensions based on quality level
- **Sharpness**: Laplacian variance for edge detection
- **Contrast**: Standard deviation analysis
- **Noise Level**: High-pass filter estimation
- **Professional Standards**: Aspect ratio, color consistency checks

## 💰 Pricing & Credits

- **1 Credit = $0.01 USD** (transparent pricing)
- **Generation Cost**: 4 credits per image ($0.04)
- **Real-time Tracking**: See exact costs before generation
- **AWS Integration**: Based on actual Bedrock pricing

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Protected Routes**: Frontend route protection
- **API Key Management**: Secure API access
- **AWS IAM**: Proper cloud security setup

## 📊 API Endpoints

### Generation
- `POST /v1/generate` - Generate images with professional enhancement
- `GET /v1/generate/status` - Check generation service status

### Vector Generation
- `POST /v1/vector/generate` - Generate vector images (SVG format)
- `GET /v1/vector/health` - Check vector generation service status

### Templates
- `GET /v1/templates` - List available templates
- `GET /v1/templates/{id}` - Get specific template
- `GET /v1/templates/categories` - List template categories

### Images
- `GET /v1/images` - List user images
- `GET /v1/images/{id}` - Get specific image
- `DELETE /v1/images/{id}` - Delete image
- `GET /v1/images/stats/summary` - Get usage statistics

### Batch Processing
- `POST /v1/batch` - Create batch generation job
- `GET /v1/batch/{id}` - Get batch status
- `GET /v1/batch` - List user batch jobs

## 🎨 Brand Style Integration

### Available Styles
- **Professional**: Clean, corporate, minimal (Blue, Gray, White)
- **Vibrant**: Bold, energetic, colorful (Purple, Green, Orange)
- **Minimal**: Simple, clean, modern (White, Gray, Dark Gray)
- **Luxury**: Premium, elegant, sophisticated (Dark Gray, Gold, White)

### Style Application
- Automatic keyword integration
- Color palette application
- Style-specific prompt enhancement
- Brand consistency validation

## 🔧 Development

### Backend Structure
```
backend/
├── app/
│   ├── core/           # Configuration, auth, pricing
│   ├── models/         # Database models and schemas
│   ├── routes/         # API endpoints
│   ├── services/       # Business logic
│   └── main.py         # FastAPI application
├── requirements.txt    # Python dependencies
└── Dockerfile         # Container configuration
```

### Frontend Structure
```
frontend/
├── app/               # Next.js app directory
│   ├── dashboard/     # Dashboard pages
│   ├── globals.css    # Global styles
│   └── layout.tsx     # Root layout
├── components/        # Reusable components
├── lib/              # Utilities and API client
└── public/           # Static assets
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individually
docker build -t snapbrand-backend ./backend
docker build -t snapbrand-frontend ./frontend
```

### AWS Deployment
- Use provided CDK infrastructure in `/infra`
- Configure proper IAM roles for Bedrock access
- Set up S3 bucket for image storage
- Deploy using AWS CDK

## 📝 Environment Variables

### Backend (.env)
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
BEDROCK_MODEL_ID=amazon.titan-image-generator-v2:0

# Database
DATABASE_URL=sqlite:///./snapbrand.db

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
MAX_IMAGES_PER_REQUEST=10
RATE_LIMIT_PER_MINUTE=60
DEFAULT_IMAGE_SIZE=1024x1024
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Hackathon Ready

This project is specifically designed for hackathons with:
- **Quick Setup**: Get running in minutes
- **Professional Quality**: Industry-standard features
- **Scalable Architecture**: Ready for production
- **Comprehensive Documentation**: Easy to understand and extend
- **Modern Tech Stack**: Latest technologies and best practices

## 🌟 Why SnapBrand.ai?

- **🎯 Purpose-Built**: Designed specifically for professional image generation
- **🚀 Production-Ready**: Not just a demo, but a complete system
- **🎨 Brand-Focused**: Built-in brand consistency and style management
- **💰 Cost-Aware**: Transparent pricing and real-time cost tracking
- **🔧 Developer-Friendly**: Well-documented, modular, and extensible
- **🏆 Hackathon-Optimized**: Quick to deploy, impressive to demo

---

**Built with ❤️ for hackathons and professional use cases**

*Generate images that follow proper real-world guidelines and deliver exceptional quality to your users.* 