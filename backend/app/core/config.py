from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # AWS Configuration
    aws_region: str = Field("us-east-1", env="AWS_REGION")
    bedrock_model_id: str = Field(
        "stability.stable-diffusion-xl-v1", env="BEDROCK_MODEL_ID"
    )
    s3_bucket: str = Field("snapbrandassets", env="S3_BUCKET_NAME")

    # Optional explicit credentials (prefer IAM role when deployed on AWS)
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_session_token: Optional[str] = Field(None, env="AWS_SESSION_TOKEN")

    # Application Configuration
    app_name: str = Field("SnapBrand.ai Backend", env="APP_NAME")
    app_version: str = Field("0.1.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Security & CORS
    cors_origins: List[str] = Field(
        ["http://localhost:3000", "https://snapbrand.ai"], 
        env="CORS_ORIGINS"
    )
    api_key_header: str = Field("X-API-Key", env="API_KEY_HEADER")
    api_keys: List[str] = Field([], env="API_KEYS")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(1000, env="RATE_LIMIT_PER_HOUR")
    
    # S3 Configuration
    presign_expiration: int = Field(3600, env="PRESIGN_EXPIRATION")
    max_file_size_mb: int = Field(10, env="MAX_FILE_SIZE_MB")
    
    # Bedrock Configuration
    max_images_per_request: int = Field(10, env="MAX_IMAGES_PER_REQUEST")
    default_image_size: str = Field("1024x1024", env="DEFAULT_IMAGE_SIZE")
    
    # Database
    database_url: str = Field("sqlite:///./snapbrand.db", env="DATABASE_URL")
    
    # Authentication
    secret_key: str = Field("your-secret-key-change-in-production", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"


@lru_cache()
def get_settings() -> "Settings":
    """Cached accessor so imports don't create multiple settings instances."""
    return Settings() 