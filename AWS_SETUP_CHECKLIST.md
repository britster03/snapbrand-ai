# AWS S3 & Bedrock Integration Setup Checklist

## ✅ Prerequisites
- [ ] AWS Account created and billing set up
- [ ] AWS CLI installed (optional, for testing)
- [ ] Python 3.9+ installed
- [ ] Backend virtual environment activated

## 🔐 AWS Account Setup

### 1. Create IAM User
- [ ] Go to AWS IAM Console
- [ ] Create new user with programmatic access
- [ ] Attach required policies (see below)
- [ ] Download access keys (CSV file)

### 2. Required IAM Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels",
        "bedrock:GetFoundationModel"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME"
    }
  ]
}
```

## 🪣 S3 Bucket Setup

### 1. Create S3 Bucket
- [ ] Go to AWS S3 Console
- [ ] Click "Create bucket"
- [ ] Choose unique bucket name (e.g., `snapbrand-assets-2024`)
- [ ] Select region (match with `AWS_REGION`)
- [ ] Keep default settings
- [ ] Create bucket

### 2. Configure CORS
- [ ] Go to bucket properties
- [ ] Find CORS configuration
- [ ] Add this CORS policy:
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedOrigins": ["http://localhost:3000", "https://your-domain.com"],
    "ExposeHeaders": ["ETag"]
  }
]
```

## 🤖 Bedrock Setup

### 1. Enable Bedrock Access
- [ ] Go to AWS Bedrock Console
- [ ] Click "Get started"
- [ ] Accept terms of service
- [ ] Enable Stable Diffusion XL model

### 2. Verify Model Access
- [ ] Run: `aws bedrock list-foundation-models --region us-east-1`
- [ ] Confirm `amazon.titan-image-generator-v2:0` is available

## ⚙️ Environment Configuration

### 1. Create .env File
- [ ] Create `backend/.env` file
- [ ] Add all required environment variables (see template below)

### 2. Environment Variables Template
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_SESSION_TOKEN=your_session_token_here  # Optional

# Bedrock Configuration
BEDROCK_MODEL_ID=amazon.titan-image-generator-v2:0

# S3 Configuration
S3_BUCKET_NAME=your-bucket-name-here
PRESIGN_EXPIRATION=3600
MAX_FILE_SIZE_MB=10

# Application Configuration
APP_NAME=imagifyy.ai Backend
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# Security & CORS
CORS_ORIGINS=["http://localhost:3000", "https://imagifyy.ai"]
API_KEY_HEADER=X-API-Key
API_KEYS=["your-api-key-1", "your-api-key-2"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Bedrock Configuration
MAX_IMAGES_PER_REQUEST=10
DEFAULT_IMAGE_SIZE=1024x1024

# Database
DATABASE_URL=sqlite:///./snapbrand.db

# Authentication
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🧪 Testing Integration

### 1. Run Integration Test
```bash
cd backend
python test_aws_integration.py
```
- [ ] All tests pass ✅

### 2. Run Image Generation Test
```bash
cd backend
python test_image_generation.py
```
- [ ] Image generation works ✅
- [ ] S3 upload works ✅
- [ ] Presigned URLs work ✅

## 🚀 Start Backend Server

### 1. Install Dependencies
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Test API Endpoints
- [ ] Health check: `GET http://localhost:8000/health`
- [ ] Generation status: `GET http://localhost:8000/v1/generate/status`

## 🔍 Troubleshooting

### Common Issues:

1. **S3 Access Denied**
   - Check IAM permissions
   - Verify bucket name in .env
   - Ensure bucket exists in correct region

2. **Bedrock Access Denied**
   - Enable Bedrock in AWS Console
   - Check IAM permissions
   - Verify model ID is correct

3. **Invalid Credentials**
   - Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   - Ensure credentials are not expired
   - Verify region matches credentials

4. **CORS Errors**
   - Update S3 bucket CORS policy
   - Check CORS_ORIGINS in .env
   - Ensure frontend URL is included

## 📊 Monitoring

### 1. AWS CloudWatch
- [ ] Set up CloudWatch logging
- [ ] Monitor Bedrock API calls
- [ ] Track S3 usage

### 2. Application Logs
- [ ] Check `backend.log` for errors
- [ ] Monitor generation times
- [ ] Track API usage

## 🔒 Security Best Practices

- [ ] Use IAM roles instead of access keys in production
- [ ] Enable S3 bucket encryption
- [ ] Set up CloudTrail for audit logging
- [ ] Use VPC endpoints for private access
- [ ] Regularly rotate access keys
- [ ] Enable MFA for AWS account

## 💰 Cost Optimization

- [ ] Monitor Bedrock API usage
- [ ] Set up billing alerts
- [ ] Use appropriate image sizes
- [ ] Implement rate limiting
- [ ] Consider S3 lifecycle policies

---

**Next Steps:**
1. Complete all checklist items above
2. Test the full application
3. Deploy to production environment
4. Set up monitoring and alerting 