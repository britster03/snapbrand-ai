from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.database import get_db
from ..models.user import User
from ..models.generated_image import GeneratedImage as DBGeneratedImage
from ..models.schemas import GeneratedImage
from ..core.auth import get_current_active_user
from ..services.s3 import s3_service

router = APIRouter(prefix="/v1/images", tags=["images"])


@router.get("/", response_model=List[GeneratedImage])
async def list_user_images(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    template_id: Optional[str] = Query(None),
    size: Optional[str] = Query(None)
) -> List[GeneratedImage]:
    """List user's generated images with pagination and filtering."""
    
    query = db.query(DBGeneratedImage).filter(
        DBGeneratedImage.user_id == current_user.id,
        DBGeneratedImage.is_deleted == False
    )
    
    # Apply filters
    if template_id:
        query = query.filter(DBGeneratedImage.template_id == template_id)
    if size:
        query = query.filter(DBGeneratedImage.size == size)
    
    # Order by creation date (newest first) and apply pagination
    images = query.order_by(DBGeneratedImage.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to response format
    result = []
    for img in images:
        # Generate fresh presigned URL
        presigned_url = s3_service.generate_presigned_url(img.s3_key)
        
        result.append(GeneratedImage(
            id=img.id,
            s3_url=img.s3_url,
            presigned_url=presigned_url,
            prompt=img.prompt,
            size=img.size,
            created_at=img.created_at,
            metadata={
                "template_id": img.template_id,
                "guidance_scale": img.guidance_scale,
                "seed": img.seed,
                "generation_cost": img.generation_cost,
                "processing_time": img.processing_time,
                "negative_prompt": img.negative_prompt,
                "batch_id": img.batch_id,
                "brand_style": img.brand_style
            }
        ))
    
    return result


@router.get("/{image_id}", response_model=GeneratedImage)
async def get_image(
    image_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> GeneratedImage:
    """Get a specific generated image by ID."""
    
    image = db.query(DBGeneratedImage).filter(
        DBGeneratedImage.id == image_id,
        DBGeneratedImage.user_id == current_user.id,
        DBGeneratedImage.is_deleted == False
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Generate fresh presigned URL
    presigned_url = s3_service.generate_presigned_url(image.s3_key)
    
    return GeneratedImage(
        id=image.id,
        s3_url=image.s3_url,
        presigned_url=presigned_url,
        prompt=image.prompt,
        size=image.size,
        created_at=image.created_at,
        metadata={
            "template_id": image.template_id,
            "guidance_scale": image.guidance_scale,
            "seed": image.seed,
            "generation_cost": image.generation_cost,
            "processing_time": image.processing_time,
            "negative_prompt": image.negative_prompt,
            "batch_id": image.batch_id,
            "brand_style": image.brand_style
        }
    )


@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Soft delete a generated image."""
    
    image = db.query(DBGeneratedImage).filter(
        DBGeneratedImage.id == image_id,
        DBGeneratedImage.user_id == current_user.id,
        DBGeneratedImage.is_deleted == False
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Soft delete
    image.is_deleted = True
    image.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Image deleted successfully"}


@router.get("/stats/summary")
async def get_image_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's image generation statistics."""
    
    total_images = db.query(DBGeneratedImage).filter(
        DBGeneratedImage.user_id == current_user.id,
        DBGeneratedImage.is_deleted == False
    ).count()
    
    # Get images by template
    template_stats = db.query(DBGeneratedImage.template_id, db.func.count(DBGeneratedImage.id))\
        .filter(
            DBGeneratedImage.user_id == current_user.id,
            DBGeneratedImage.is_deleted == False,
            DBGeneratedImage.template_id.isnot(None)
        )\
        .group_by(DBGeneratedImage.template_id)\
        .all()
    
    # Get images by size
    size_stats = db.query(DBGeneratedImage.size, db.func.count(DBGeneratedImage.id))\
        .filter(
            DBGeneratedImage.user_id == current_user.id,
            DBGeneratedImage.is_deleted == False
        )\
        .group_by(DBGeneratedImage.size)\
        .all()
    
    return {
        "total_images": total_images,
        "total_cost_spent": current_user.total_cost_spent,
        "template_usage": {template: count for template, count in template_stats},
        "size_usage": {size: count for size, count in size_stats}
    } 