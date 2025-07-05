from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from .core.config import Settings
from .core.middleware import setup_cors_middleware, setup_rate_limit_middleware, setup_api_key_middleware
from .core.pricing import get_model_pricing_info
from .routes.generate import router as generate_router
from .routes.assets import router as assets_router
from .routes.templates import router as templates_router
from .routes.batch import router as batch_router
from .routes.auth import router as auth_router
from .routes.images import router as images_router
from .models.database import init_db

settings = Settings()

# Configure logger globally
logger.remove()
logger.add(
    lambda msg: print(msg, flush=True), 
    level=settings.log_level.upper(),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=settings.debug,
)

# Setup middleware
setup_cors_middleware(app)
setup_rate_limit_middleware(app)
setup_api_key_middleware(app)

# Initialize database
init_db()

# Seed database with initial data
try:
    from .core.database_seed import seed_database
    seed_database()
except Exception as e:
    logger.warning(f"Database seeding failed: {e}")

# Include routers
app.include_router(auth_router)
app.include_router(generate_router)
app.include_router(assets_router)
app.include_router(templates_router)
app.include_router(batch_router)
app.include_router(images_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Production-ready health check endpoint with comprehensive service status."""
    logger.debug("Health check requested")
    
    services = {}
    overall_status = "healthy"
    
    # Check Bedrock service
    try:
        from .services.bedrock import bedrock_service
        
        # Test actual Bedrock connectivity
        try:
            models = bedrock_service.client.list_foundation_models()
            pricing_info = get_model_pricing_info(settings.bedrock_model_id)
            
            services["bedrock"] = {
                "status": "healthy",
                "details": {
                    "available_models": len(models.get("modelSummaries", [])),
                    "configured_model": settings.bedrock_model_id,
                    "pricing": pricing_info
                }
            }
        except Exception as e:
            services["bedrock"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            overall_status = "unhealthy"
            
    except Exception as e:
        services["bedrock"] = {
            "status": "unhealthy", 
            "error": f"Service initialization failed: {str(e)}"
        }
        overall_status = "unhealthy"
    
    # Check S3 service
    try:
        from .services.s3 import s3_service
        
        # Test actual S3 connectivity
        try:
            s3_service.client.head_bucket(Bucket=settings.s3_bucket)
            services["s3"] = {
                "status": "healthy",
                "details": {
                    "bucket": settings.s3_bucket,
                    "region": settings.aws_region
                }
            }
        except Exception as e:
            services["s3"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            overall_status = "unhealthy"
            
    except Exception as e:
        services["s3"] = {
            "status": "unhealthy",
            "error": f"Service initialization failed: {str(e)}"
        }
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "version": settings.app_version,
        "services": services,
        "timestamp": datetime.utcnow().isoformat(),
        "configuration": {
            "max_images_per_request": settings.max_images_per_request,
            "rate_limit_per_minute": settings.rate_limit_per_minute,
            "api_key_required": bool(settings.api_keys),
            "aws_region": settings.aws_region,
            "bedrock_model": settings.bedrock_model_id,
            "s3_bucket": settings.s3_bucket,
            "debug": settings.debug
        }
    }


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    logger.exception(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


# All routers have been included above 