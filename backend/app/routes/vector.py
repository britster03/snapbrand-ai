from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from ..core.auth import get_current_user
from ..models.schemas import (
    VectorGenerateRequest,
    VectorGenerateResponse,
    GeneratedVector,
    ErrorResponse,
)
from ..models.user import User
from ..services.vector_engine import vector_engine

router = APIRouter(prefix="/v1/vector", tags=["vector"])


@router.post(
    "/generate",
    response_model=VectorGenerateResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Generate vector images",
    description="Generate vector images from text prompts using AI models",
)
async def generate_vector_images(
    request: VectorGenerateRequest,
    current_user: User = Depends(get_current_user),
) -> VectorGenerateResponse:
    """
    Generate vector images from text prompts.
    
    This endpoint accepts a text prompt and generates vector images (SVG format)
    based on the description. The generated vectors can be returned as raw SVG
    content or base64-encoded strings.
    """
    
    try:
        logger.info(f"Vector generation request from user {current_user.id}: {request.prompt}")
        
        # Record start time for processing time calculation
        start_time = datetime.utcnow()
        
        # Validate request parameters
        if not request.prompt.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt cannot be empty"
            )
        
        # Generate vector images using the vector engine
        if request.format == "base64":
            svg_results = vector_engine.generate_vectors_base64(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                num_images=request.num_images,
                size=request.size,
                style=request.style,
                seed=request.seed,
            )
        else:
            svg_results = vector_engine.generate_vectors(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                num_images=request.num_images,
                size=request.size,
                style=request.style,
                seed=request.seed,
            )
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Create response objects
        generated_vectors: List[GeneratedVector] = []
        
        for i, svg_data in enumerate(svg_results):
            vector_id = str(uuid.uuid4())
            
            # Create GeneratedVector object based on format
            if request.format == "base64":
                vector = GeneratedVector(
                    id=vector_id,
                    svg_content=None,
                    svg_base64=svg_data,
                    s3_url=None,
                    presigned_url=None,
                    prompt=request.prompt,
                    size=request.size,
                    style=request.style,
                    created_at=datetime.utcnow(),
                    metadata={
                        "user_id": current_user.id,
                        "negative_prompt": request.negative_prompt,
                        "seed": request.seed,
                        "format": request.format,
                        "generation_index": i,
                    }
                )
            else:
                vector = GeneratedVector(
                    id=vector_id,
                    svg_content=svg_data,
                    svg_base64=None,
                    s3_url=None,
                    presigned_url=None,
                    prompt=request.prompt,
                    size=request.size,
                    style=request.style,
                    created_at=datetime.utcnow(),
                    metadata={
                        "user_id": current_user.id,
                        "negative_prompt": request.negative_prompt,
                        "seed": request.seed,
                        "format": request.format,
                        "generation_index": i,
                    }
                )
            
            generated_vectors.append(vector)
        
        # For now, we'll use a simple cost calculation
        # In production, this would be based on actual service costs
        estimated_cost = len(generated_vectors) * 0.02  # $0.02 per vector image
        
        logger.info(f"Successfully generated {len(generated_vectors)} vector images for user {current_user.id}")
        
        return VectorGenerateResponse(
            vectors=generated_vectors,
            total_cost=estimated_cost,
            processing_time=processing_time,
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating vector images: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate vector images: {str(e)}"
        )


@router.get(
    "/health",
    summary="Vector service health check",
    description="Check if the vector generation service is healthy",
)
async def vector_health_check():
    """Check the health of the vector generation service."""
    try:
        # Test the vector engine with a simple prompt
        test_vectors = vector_engine.generate_vectors(
            prompt="test circle",
            num_images=1,
            size="256x256"
        )
        
        if test_vectors and len(test_vectors) > 0:
            return {
                "status": "healthy",
                "service": "vector_engine",
                "timestamp": datetime.utcnow(),
                "test_generation": "success"
            }
        else:
            return {
                "status": "unhealthy",
                "service": "vector_engine",
                "timestamp": datetime.utcnow(),
                "test_generation": "failed"
            }
            
    except Exception as e:
        logger.error(f"Vector service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "vector_engine",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        } 