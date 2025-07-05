from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, List

from fastapi import HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from .config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""

    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests: Dict[str, List[float]] = defaultdict(list)
        self.hour_requests: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(client_ip, current_time)

        # Check rate limits
        if len(self.minute_requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        if len(self.hour_requests[client_ip]) >= self.requests_per_hour:
            logger.warning(f"Hourly rate limit exceeded for {client_ip}")
            raise HTTPException(status_code=429, detail="Hourly rate limit exceeded")

        # Add current request
        self.minute_requests[client_ip].append(current_time)
        self.hour_requests[client_ip].append(current_time)

        response = await call_next(request)
        return response

    def _clean_old_requests(self, client_ip: str, current_time: float):
        """Remove requests older than the time windows."""
        # Clean minute requests (older than 60 seconds)
        self.minute_requests[client_ip] = [
            req_time for req_time in self.minute_requests[client_ip]
            if current_time - req_time < 60
        ]

        # Clean hour requests (older than 3600 seconds)
        self.hour_requests[client_ip] = [
            req_time for req_time in self.hour_requests[client_ip]
            if current_time - req_time < 3600
        ]


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API keys for protected endpoints."""

    def __init__(self, app, protected_paths: List[str] = None):
        super().__init__(app)
        self.protected_paths = protected_paths or ["/v1/generate", "/v1/batch"]
        self.settings = get_settings()

    async def dispatch(self, request: Request, call_next):
        # Skip API key check for non-protected paths
        if not any(request.url.path.startswith(path) for path in self.protected_paths):
            return await call_next(request)

        # Skip API key check if no keys are configured
        if not self.settings.api_keys:
            return await call_next(request)

        api_key = request.headers.get(self.settings.api_key_header)
        if not api_key:
            raise HTTPException(
                status_code=401, 
                detail=f"API key required. Use {self.settings.api_key_header} header."
            )

        if api_key not in self.settings.api_keys:
            logger.warning(f"Invalid API key attempt from {request.client.host}")
            raise HTTPException(status_code=401, detail="Invalid API key")

        return await call_next(request)


def setup_cors_middleware(app):
    """Setup CORS middleware with configuration from settings."""
    settings = get_settings()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_rate_limit_middleware(app):
    """Setup rate limiting middleware."""
    settings = get_settings()
    
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.rate_limit_per_minute,
        requests_per_hour=settings.rate_limit_per_hour,
    )


def setup_api_key_middleware(app):
    """Setup API key authentication middleware."""
    app.add_middleware(APIKeyMiddleware) 