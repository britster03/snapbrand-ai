# SnapBrand.ai

SnapBrand.ai is an AI-powered brand asset studio that combines Amazon Bedrock diffusion models, FastAPI, and AWS App Runner to generate on-brand product imagery at scale.

---

## Architecture

```
┌──────────────┐    HTTP     ┌────────────────────────────────┐
│  Next.js UI  │ ──────────► │  FastAPI backend (App Runner)  │
└──────────────┘              │  ‑  /v1/generate              │
                              │  ‑  /v1/assets/upload-url     │
                              └─────────────┬──────────────────┘
                                            │
                                            │ InvokeModel + S3 put
                                            ▼
                                   ┌────────────────┐
                                   │ Amazon Bedrock │
                                   │  Diffusion XL  │
                                   └────────────────┘
                                            ▲
                                            │ S3 bucket read/write
                                            ▼
                                      ┌────────────┐
                                      │   S3       │
                                      └────────────┘
```

* **UI** – Existing Next.js project under `app/`.
* **Backend** – FastAPI application in `backend/app` exposed via AWS App Runner.
* **Storage** – Versioned S3 bucket for generated and uploaded brand assets.
* **AI** – Amazon Bedrock Stable Diffusion XL (configurable).

---

## Local Development

1. **Install backend dependencies**

   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create `.env`**

   ```env
   AWS_REGION=us-east-1
   BEDROCK_MODEL_ID=stability.stable-diffusion-xl-v1
   S3_BUCKET_NAME=your-dev-snapbrand-bucket
   LOG_LEVEL=DEBUG
   # Optional credentials for local use (omit when using AWS roles)
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   ```

3. **Run FastAPI**

   ```bash
   uvicorn app.main:app --reload
   ```

   The OpenAPI docs will be available at http://localhost:8000/docs .

---

## Docker Image

Build and test the container locally:

```bash
# From repo root
docker build -t snapbrand-backend -f backend/Dockerfile .
docker run -p 8000:8000 --env-file backend/.env snapbrand-backend
```

---

## Deployment (AWS CDK)

The `infra/` directory contains an AWS CDK stack that provisions:

* **S3 Bucket** – `AssetsBucket` (private, versioned)
* **ECR Repository** – `BackendRepo`
* **IAM Role** – App Runner task role with Bedrock + S3 permissions
* **App Runner Service** – pulls the latest `:latest` image from the ECR repo

### Prerequisites

* AWS CLI configured with an account that has CDK + Bedrock access.
* [AWS CDK v2](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) installed (`npm i -g aws-cdk`).

### Bootstrapping & Deploy

```bash
cd infra
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Bootstrap environment (only once per account/region)
cdk bootstrap

# Deploy stack
cdk deploy SnapBrandStack
```

The output will include:

* `AssetsBucketName` – the S3 bucket to set in prod `.env` files
* `AppRunnerServiceUrl` – public URL of the REST API

---

## CI / CD

Pushes to `main` can build & push the backend Docker image to ECR and trigger an automatic App Runner deployment. Configure GitHub Actions or any CI tool with:

1. **Build & push image:**
   `docker build -t $ECR_URI:latest -f backend/Dockerfile .`
2. **Login & push:**
   `aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI`
3. **Trigger deployment:**
   `aws apprunner start-deployment --service-arn $APPRUNNER_SERVICE_ARN`

---

## Notes & Next Steps

* **Security** – Add Amazon Cognito or JWT auth for user endpoints.
* **Brand Style Enforcement** – Integrate CLIP embeddings & custom vector DB to refine prompts.
* **Observability** – Attach CloudWatch Logs Insights & X-Ray tracing.
* **Cost Controls** – Add concurrency limits and Bedrock guardrails. 