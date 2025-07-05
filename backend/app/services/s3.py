from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError
from loguru import logger

from ..core.config import get_settings


class S3Service:
    """Wrapper for S3 operations used by the backend."""

    def __init__(self) -> None:
        settings = get_settings()
        session_params: Dict[str, Any] = {
            "region_name": settings.aws_region,
        }
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            session_params.update(
                {
                    "aws_access_key_id": settings.aws_access_key_id,
                    "aws_secret_access_key": settings.aws_secret_access_key,
                    "aws_session_token": settings.aws_session_token,
                }
            )

        session = boto3.Session(**session_params)  # type: ignore[arg-type]
        self._client = session.client(
            "s3", config=BotoConfig(retries={"max_attempts": 5, "mode": "adaptive"})
        )
        self._bucket = settings.s3_bucket
    
    @property
    def client(self):
        """Public access to the S3 client for health checks."""
        return self._client

    # Utility functions -----------------------------------------------------

    def _object_key(self, prefix: str, filename: str) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{prefix.rstrip('/')}/{timestamp}_{filename}"

    # Public API ------------------------------------------------------------

    def upload_bytes(self, data: bytes, key: str, content_type: str = "image/png") -> str:
        """Upload raw bytes to S3 and return the object URL."""
        self._client.put_object(
            Bucket=self._bucket, Key=key, Body=data, ContentType=content_type
        )
        url = f"https://{self._bucket}.s3.amazonaws.com/{key}"
        logger.debug(f"Uploaded {key} to {url}")
        return url

    def generate_presigned_url(self, key: str, expires_in: Optional[int] = None) -> str:
        settings = get_settings()
        expiration = expires_in or settings.presign_expiration
        try:
            response = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=expiration,
            )
            logger.debug(f"Generated presigned URL for {key}: {response}")
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise

    def generate_presigned_upload_url(self, key: str, expires_in: Optional[int] = None, content_type: str = "image/png") -> str:
        settings = get_settings()
        expiration = expires_in or settings.presign_expiration
        response = self._client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self._bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=expiration,
        )
        logger.debug(f"Generated presigned upload URL for {key}: {response}")
        return response


s3_service = S3Service() 