from __future__ import annotations

import json
from base64 import b64decode
from typing import Any, Dict, List, Optional

import boto3
from botocore.config import Config as BotoConfig
from loguru import logger

from ..core.config import get_settings


class EnhancedBedrockService:
    """Enhanced wrapper around Amazon Bedrock Runtime for image generation."""

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

    def _build_stable_diffusion_payload(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        size: str = "1024x1024",
        style_preset: str = "photographic",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Build payload for Stable Diffusion XL model."""
        payload: Dict[str, Any] = {
            "text_prompts": [{"text": prompt, "weight": 1.0}],
            "cfg_scale": guidance_scale,
            "steps": 50,
            "samples": num_images,
            "style_preset": style_preset,
            "width": int(size.split("x")[0]),
            "height": int(size.split("x")[1]),
        }
        if negative_prompt:
            payload["text_prompts"].append({"text": negative_prompt, "weight": -1.0})
        if seed:
            payload["seed"] = seed
        return payload

    def _build_titan_payload(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Build payload for Titan Image Generator V2 model."""
        width, height = map(int, size.split("x"))
        
        # Titan V2 supported sizes - must match exactly
        supported_sizes = {
            (1024, 1024), (768, 768), (512, 512),  # 1:1
            (768, 1152), (384, 576),  # 2:3
            (1152, 768), (576, 384),  # 3:2
            (768, 1280), (384, 640),  # 3:5
            (1280, 768), (640, 384),  # 5:3
            (896, 1152), (448, 576),  # 7:9
            (1152, 896), (576, 448),  # 9:7
            (768, 1408), (384, 704),  # 6:11
            (1408, 768), (704, 384),  # 11:6
            (640, 1408), (320, 704),  # 5:11
            (1408, 640), (704, 320),  # 11:5
            (1152, 640),  # 9:5
            (1173, 640),  # 16:9
        }
        
        if (width, height) not in supported_sizes:
            # Find closest supported size
            closest_size = min(supported_sizes, 
                             key=lambda s: abs(s[0] - width) + abs(s[1] - height))
            logger.warning(f"Size {size} not supported by Titan V2, using closest: {closest_size[0]}x{closest_size[1]}")
            width, height = closest_size
        
        # Titan V2 supports quality levels: standard, premium
        # and better prompt adherence
        payload: Dict[str, Any] = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
            },
            "imageGenerationConfig": {
                "numberOfImages": num_images,
                "quality": quality,
                "cfgScale": guidance_scale,
                "height": height,
                "width": width,
                "seed": seed or 0,
            }
        }
        
        # Add negative prompt if provided
        if negative_prompt:
            payload["textToImageParams"]["negativeText"] = negative_prompt
            
        return payload

    def _parse_stable_diffusion_response(self, response_body) -> List[bytes]:
        """Parse Stable Diffusion XL response."""
        response_json = response_body.read()
        if not response_json:
            raise RuntimeError("Empty response from Bedrock model")

        data: Dict[str, Any] = json.loads(response_json)
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

    def _parse_titan_response(self, response_body) -> List[bytes]:
        """Parse Titan Image Generator V2 response."""
        response_json = response_body.read()
        if not response_json:
            raise RuntimeError("Empty response from Bedrock model")

        data: Dict[str, Any] = json.loads(response_json)
        
        # Titan V2 response format: {"images": ["base64string1", "base64string2"]}
        results = data.get("images", [])
        if not results:
            raise RuntimeError("No images in Bedrock response")

        images: List[bytes] = []
        for image_data in results:
            # In Titan V2, each image is a direct base64 string
            if isinstance(image_data, str):
                images.append(b64decode(image_data))
            elif isinstance(image_data, dict) and "base64" in image_data:
                # Fallback for older format
                images.append(b64decode(image_data["base64"]))
        
        return images

    def generate_images(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        **kwargs: Any,
    ) -> List[bytes]:
        """Generate images and return them as raw PNG bytes."""

        # Determine which model we're using and build appropriate payload
        if "stability" in self._model_id:
            body = self._build_stable_diffusion_payload(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_images=num_images,
                **kwargs,
            )
            parse_response = self._parse_stable_diffusion_response
        elif "titan" in self._model_id:
            body = self._build_titan_payload(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_images=num_images,
                **kwargs,
            )
            parse_response = self._parse_titan_response
        else:
            raise ValueError(f"Unsupported model: {self._model_id}")

        logger.info(f"Invoking Bedrock model {self._model_id} with payload: {body}")
        
        try:
            response = self._client.invoke_model(
                modelId=self._model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body),
            )

            response_body = response.get("body")
            if response_body is None:
                raise RuntimeError("No response body from Bedrock model")

            return parse_response(response_body)

        except Exception as e:
            logger.error(f"Error invoking Bedrock model {self._model_id}: {e}")
            raise


# Create service instance
enhanced_bedrock_service = EnhancedBedrockService() 