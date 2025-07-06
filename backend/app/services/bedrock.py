from __future__ import annotations

import json
from base64 import b64decode
from typing import Any, Dict, List, Optional

import boto3
from botocore.config import Config as BotoConfig
from loguru import logger

from ..core.config import get_settings


class BedrockService:
    """Wrapper around Amazon Bedrock Runtime for image generation."""

    def __init__(self) -> None:
        settings = get_settings()

        session_params: Dict[str, Any] = {
            "region_name": settings.aws_region,
        }
        # Allow local testing with explicit credentials
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            session_params.update(
                {
                    "aws_access_key_id": settings.aws_access_key_id,
                    "aws_secret_access_key": settings.aws_secret_access_key,
                    "aws_session_token": settings.aws_session_token,
                }
            )

        logger.debug(f"Initializing boto3 session with params: {session_params}")
        session = boto3.Session(**session_params)  # type: ignore[arg-type]
        self._client = session.client(
            "bedrock-runtime",
            config=BotoConfig(retries={"max_attempts": 5, "mode": "adaptive"}),
        )
        self._model_id = settings.bedrock_model_id
        
        # Also create a regular bedrock client for health checks
        self._bedrock_client = session.client("bedrock")
    
    @property
    def client(self):
        """Public access to the bedrock client for health checks."""
        return self._bedrock_client

    def _build_payload(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        size: str = "1024x1024",
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "text_prompts": [{"text": prompt, "weight": 1.0}],
            "cfg_scale": guidance_scale,
            "steps": 50,
            "samples": num_images,
            "style_preset": "photographic",
            "width": int(size.split("x")[0]),
            "height": int(size.split("x")[1]),
        }
        if negative_prompt:
            payload["text_prompts"].append({"text": negative_prompt, "weight": -1.0})
        if seed:
            payload["seed"] = seed
        return payload

    def generate_images(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        **kwargs: Any,
    ) -> List[bytes]:
        """Generate images and return them as raw PNG bytes."""

        body = self._build_payload(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_images=num_images,
            **kwargs,
        )
        logger.info(f"Invoking Bedrock model {self._model_id} with payload: {body}")
        response = self._client.invoke_model(
            modelId=self._model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body).encode("utf-8"),
        )

        response_body = response.get("body")
        if response_body is None:
            raise RuntimeError("No response body from Bedrock model")

        response_json = response_body.read()
        if not response_json:
            raise RuntimeError("Empty response from Bedrock model")

        data: Dict[str, Any] = __import__("json").loads(response_json)
        results = data.get("artifacts", [])
        if not results:
            raise RuntimeError("No artifacts in Bedrock response")

        images: List[bytes] = []
        for artifact in results:
            if artifact.get("finishReason") == "SUCCESS":
                b64_image = artifact.get("base64")
                if not b64_image:
                    continue
                images.append(b64decode(b64_image))
            else:
                logger.warning(
                    f"Artifact not successful: finishReason={artifact.get('finishReason')}"
                )
        return images


bedrock_service = BedrockService() 