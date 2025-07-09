# SnapBrand.ai Deployment Guide

This guide covers deploying the complete SnapBrand.ai application, including the FastAPI backend and Next.js frontend.

## Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed
- Node.js 18+ and npm/pnpm
- Python 3.11+
- AWS CDK v2 installed (`npm i -g aws-cdk`)

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI    │    │  FastAPI Backend│    │   AWS Services  │
│   (Vercel/Netlify) │◄──►│  (App Runner)   │◄──►│                 │
└─────────────────┘    └─────────────────┘    │ • Bedrock       │
                                              │ • S3            │
                                              │ • ECR           │
                                              │ • IAM           │
                                              └─────────────────┘
```

## Step 1: Backend Deployment

### 1.1 Local Development Setup

```bash
# Clone and setup backend
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your AWS credentials and settings

# Run locally
uvicorn app.main:app --reload
```

### 1.2 AWS Infrastructure Deployment

```bash
# Setup CDK infrastructure
cd infra
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy infrastructure
cdk deploy SnapBrandStack
```

This creates:
- S3 bucket for assets
- ECR repository for container images
- IAM roles with Bedrock + S3 permissions
- App Runner service (initially empty)

### 1.3 Build and Deploy Backend Container

```bash
# Get ECR repository URI from CDK output
export ECR_URI=$(aws cloudformation describe-stacks \
  --stack-name SnapBrandStack \
  --query 'Stacks[0].Outputs[?OutputKey==`BackendRepoUri`].OutputValue' \
  --output text)

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_URI

# Build and push image
docker build -t snapbrand-backend -f backend/Dockerfile .
docker tag snapbrand-backend:latest $ECR_URI:latest
docker push $ECR_URI:latest
```

### 1.4 Update App Runner Service

```bash
# Get App Runner service ARN
export SERVICE_ARN=$(aws cloudformation describe-stacks \
  --stack-name SnapBrandStack \
  --query 'Stacks[0].Outputs[?OutputKey==`AppRunnerServiceArn`].OutputValue' \
  --output text)

# Update service with new image
aws apprunner start-deployment --service-arn $SERVICE_ARN
```

### 1.5 Environment Configuration

Get the S3 bucket name from CDK output and update your backend environment:

```bash
export S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name SnapBrandStack \
  --query 'Stacks[0].Outputs[?OutputKey==`AssetsBucketName`].OutputValue' \
  --output text)

# Update App Runner environment variables
aws apprunner update-service \
  --service-arn $SERVICE_ARN \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR_URI':latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "S3_BUCKET_NAME": "'$S3_BUCKET'",
          "AWS_REGION": "us-east-1",
          "BEDROCK_MODEL_ID": "amazon.titan-image-generator-v2:0",
          "LOG_LEVEL": "INFO"
        }
      }
    }
  }'
```

## Step 2: Frontend Deployment

### 2.1 Environment Configuration

Create `.env.local` in the project root:

```env
NEXT_PUBLIC_API_URL=https://your-app-runner-url.amazonaws.com
```

### 2.2 Deploy to Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### 2.3 Alternative: Deploy to Netlify

```bash
# Build the project
npm run build

# Deploy to Netlify
netlify deploy --prod --dir=out
```

## Step 3: CI/CD Pipeline

### 3.1 GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy SnapBrand.ai

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: snapbrand-backend
          IMAGE_TAG: latest
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG -f backend/Dockerfile .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      
      - name: Deploy to App Runner
        run: |
          aws apprunner start-deployment \
            --service-arn ${{ secrets.APPRUNNER_SERVICE_ARN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### 3.2 Required Secrets

Add these secrets to your GitHub repository:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `APPRUNNER_SERVICE_ARN`
- `NEXT_PUBLIC_API_URL`
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

## Step 4: Production Configuration

### 4.1 Security Hardening

1. **API Keys**: Generate strong API keys and add them to backend environment
2. **CORS**: Update CORS origins to only include your production domain
3. **Rate Limiting**: Adjust rate limits based on your usage patterns
4. **Monitoring**: Set up CloudWatch alarms for errors and performance

### 4.2 Environment Variables

Production backend environment:

```env
# Production settings
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://yourdomain.com"]
API_KEYS=["prod-api-key-1", "prod-api-key-2"]
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500
```

### 4.3 SSL/TLS

App Runner automatically provides HTTPS. For custom domains:

```bash
# Add custom domain to App Runner
aws apprunner associate-custom-domain \
  --service-arn $SERVICE_ARN \
  --domain-name api.yourdomain.com
```

## Step 5: Monitoring and Maintenance

### 5.1 Health Checks

Monitor the health endpoint:
```bash
curl https://your-app-runner-url.amazonaws.com/health
```

### 5.2 Logs

View App Runner logs:
```bash
aws logs describe-log-groups --log-group-name-prefix /aws/apprunner
```

### 5.3 Scaling

App Runner automatically scales based on load. For manual scaling:

```bash
aws apprunner update-service \
  --service-arn $SERVICE_ARN \
  --auto-scaling-configuration-arn your-scaling-config-arn
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Check CORS_ORIGINS in backend environment
2. **Bedrock Access**: Ensure IAM role has `bedrock:InvokeModel` permission
3. **S3 Access**: Verify S3 bucket permissions and IAM role
4. **Image Generation Fails**: Check Bedrock model availability in your region

### Debug Commands

```bash
# Check App Runner service status
aws apprunner describe-service --service-arn $SERVICE_ARN

# View recent deployments
aws apprunner list-operations --service-arn $SERVICE_ARN

# Check S3 bucket contents
aws s3 ls s3://your-bucket-name/generated/

# Test API endpoints
curl -X POST https://your-api-url/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test image", "num_images": 1}'
```

## Cost Optimization

1. **App Runner**: Use minimal instance size for development
2. **Bedrock**: Monitor usage and set up billing alerts
3. **S3**: Implement lifecycle policies for old images
4. **CDN**: Consider CloudFront for image delivery

## Next Steps

1. **Authentication**: Implement user authentication with Cognito
2. **Database**: Add PostgreSQL for user data and image metadata
3. **Analytics**: Set up usage tracking and analytics
4. **Advanced Features**: Implement brand style learning and custom templates 