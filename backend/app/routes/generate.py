from __future__ import annotations

import time
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from loguru import logger

from ..models.schemas import GenerateRequest, GenerateResponse, GeneratedImage
from ..models.database import get_db
from ..models.user import User
from ..models.generated_image import GeneratedImage as DBGeneratedImage
from ..services.bedrock import bedrock_service
from ..services.s3 import s3_service
from ..services.prompt_engineering import prompt_engineering_service, ImageQuality, ImageStyle, CompositionRule
from ..services.llm_prompt_generator import llm_prompt_generator
from ..core.config import get_settings
from ..core.pricing import calculate_generation_cost
from ..core.auth import get_current_active_user
from .templates import get_template

router = APIRouter(prefix="/v1", tags=["generation"])
settings = get_settings()


async def validate_generation_request(request: GenerateRequest) -> GenerateRequest:
    """Validate and enhance generation request with LLM-generated prompts for dynamic templates."""
    # Check image count limit
    if request.num_images > settings.max_images_per_request:
        raise HTTPException(
            status_code=400, 
            detail=f"Maximum {settings.max_images_per_request} images per request"
        )
    
    # Handle dynamic LLM-generated templates
    if request.template_id:
        try:
            template = await get_template(request.template_id)
            
            # Check if this is a dynamic LLM template
            if (template.prompt_template == "DYNAMIC_LLM_GENERATED" and 
                template.negative_prompt == "DYNAMIC_LLM_GENERATED"):
                
                # Use LLM prompt generator
                template_type = template.parameters.get("template_type", "email_header")
                generated_prompts = llm_prompt_generator.generate_prompt(
                    template_type=template_type,
                    subject=request.prompt,  # User's input becomes the subject
                    style="modern"  # Default style, could be made configurable
                )
                
                # Replace with LLM-generated prompts
                request.prompt = generated_prompts["prompt"]
                request.negative_prompt = generated_prompts["negative_prompt"]
                
                # Set template size
                if request.size == "1024x1024" and template.default_size != "1024x1024":
                    request.size = template.default_size
                
                logger.info(f"LLM Generated prompt: {request.prompt[:100]}...")
                logger.info(f"LLM Generated negative: {request.negative_prompt[:100]}...")
                
                return request
            
            # Handle legacy static templates (if any remain)
            else:
                # Use template defaults if not specified
                if not request.negative_prompt and template.negative_prompt:
                    request.negative_prompt = template.negative_prompt
                if request.size == "1024x1024" and template.default_size != "1024x1024":
                    request.size = template.default_size
                
                # Get professional enhancement parameters for this template
                template_enhancement = prompt_engineering_service.get_template_enhancement(request.template_id)
                
                # Use old prompt engineering system for legacy templates
                quality = ImageQuality.HIGH
                style = ImageStyle.MARKETING
                
                enhanced_prompt = prompt_engineering_service.enhance_prompt(
                    base_prompt=request.prompt,
                    quality=quality,
                    style=style,
                    brand_style=request.brand_style,
                    template_context=template_enhancement.get("context")
                )
                
                enhanced_negative = prompt_engineering_service.generate_negative_prompt(
                    base_negative=request.negative_prompt,
                    style=style,
                    additional_exclusions=[]
                )
                
                request.prompt = enhanced_prompt
                request.negative_prompt = enhanced_negative
                
        except HTTPException:
            logger.warning(f"Template {request.template_id} not found, proceeding without template")
    
    # For requests without templates, use minimal enhancement
    else:
        request.prompt = request.prompt + ", high quality"
    
    logger.info(f"Final prompt: {request.prompt[:100]}...")
    logger.info(f"Final negative: {request.negative_prompt[:100]}...")
    
    return request


@router.post("/generate", response_model=GenerateResponse, status_code=201)
async def generate_images(
    payload: GenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> GenerateResponse:
    """Generate images using Bedrock and store them in S3."""
    
    # Validate the request
    validated_request = await validate_generation_request(payload)
    
    start_time = time.time()
    
    try:
        logger.info(f"Starting image generation: {payload.prompt[:50]}...")
        
        images = bedrock_service.generate_images(
            prompt=validated_request.prompt,
            negative_prompt=validated_request.negative_prompt,
            num_images=validated_request.num_images,
            guidance_scale=validated_request.guidance_scale,
            seed=validated_request.seed,
            size=validated_request.size,
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Generated {len(images)} images in {processing_time:.2f}s")
        
    except Exception as e:
        logger.exception("Bedrock generation failed")
        raise HTTPException(status_code=500, detail="Image generation failed") from e

    results: list[GeneratedImage] = []
    for idx, img_bytes in enumerate(images):
        try:
            # Generate unique ID and S3 key
            image_id = f"img_{uuid.uuid4().hex[:8]}"
            key = f"generated/{datetime.utcnow().strftime('%Y/%m/%d')}/{image_id}.png"
            
            # Upload to S3
            s3_url = s3_service.upload_bytes(img_bytes, key)
            presigned_url = s3_service.generate_presigned_url(key)
            
            # Calculate cost for this image
            image_cost = calculate_generation_cost(
                model_id=settings.bedrock_model_id,
                num_images=1,
                size=validated_request.size
            )
            
            # Save to database
            db_image = DBGeneratedImage(
                id=image_id,
                user_id=current_user.id,
                prompt=validated_request.prompt,
                negative_prompt=validated_request.negative_prompt,
                size=validated_request.size,
                s3_url=s3_url,
                s3_key=key,
                guidance_scale=validated_request.guidance_scale,
                seed=validated_request.seed,
                template_id=validated_request.template_id,
                generation_cost=str(image_cost),
                brand_style=str(validated_request.brand_style) if validated_request.brand_style else None,
                processing_time=processing_time
            )
            db.add(db_image)
            
            # Create response object
            generated_image = GeneratedImage(
                id=image_id,
                s3_url=s3_url,
                presigned_url=presigned_url,
                prompt=validated_request.prompt,
                size=validated_request.size,
                metadata={
                    "template_id": validated_request.template_id,
                    "brand_style": validated_request.brand_style,
                    "guidance_scale": validated_request.guidance_scale,
                    "seed": validated_request.seed,
                    "generation_time": processing_time
                }
            )
            results.append(generated_image)
            
        except Exception as e:
            logger.error(f"Failed to process image {idx}: {e}")
            # Continue with other images even if one fails
    
    if not results:
        raise HTTPException(status_code=500, detail="Failed to process any images")
    
    # Calculate actual cost based on AWS Bedrock pricing
    estimated_cost = calculate_generation_cost(
        model_id=settings.bedrock_model_id,
        num_images=len(results),
        size=validated_request.size
    )
    
    # Update user statistics
    current_user.total_images_generated += len(results)
    current_user.total_cost_spent = str(float(current_user.total_cost_spent) + estimated_cost)
    
    # Commit database changes
    db.commit()
    
    return GenerateResponse(
        images=results,
        processing_time=processing_time,
        total_cost=estimated_cost
    )


@router.get("/generate/status", response_model=dict)
async def get_generation_status() -> dict:
    """Get current generation service status."""
    return {
        "status": "operational",
        "model": settings.bedrock_model_id,
        "max_images_per_request": settings.max_images_per_request,
        "default_size": settings.default_image_size,
        "rate_limit_per_minute": settings.rate_limit_per_minute
    } 