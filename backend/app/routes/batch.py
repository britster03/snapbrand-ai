from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from loguru import logger

from ..models.schemas import (
    BatchGenerateRequest, 
    BatchGenerateResponse, 
    BatchStatusResponse,
    GenerateRequest,
    GenerateResponse,
    GeneratedImage
)
from ..models.database import get_db
from ..models.user import User
from ..models.batch_job import BatchJob as DBBatchJob
from ..models.generated_image import GeneratedImage as DBGeneratedImage
from ..services.bedrock import bedrock_service
from ..services.s3 import s3_service
from ..core.config import get_settings
from ..core.pricing import calculate_generation_cost
from ..core.auth import get_current_active_user

router = APIRouter(prefix="/v1/batch", tags=["batch"])

settings = get_settings()


async def process_batch_job(batch_id: str, requests: List[GenerateRequest]):
    """Background task to process batch image generation."""
    
    # Create a new database session for the background task
    from ..models.database import SessionLocal
    db = SessionLocal()
    
    try:
        # Get batch job and user
        batch_job = db.query(DBBatchJob).filter(DBBatchJob.id == batch_id).first()
        if not batch_job:
            logger.error(f"Batch job {batch_id} not found")
            return
        
        user = db.query(User).filter(User.id == batch_job.user_id).first()
        if not user:
            logger.error(f"User {batch_job.user_id} not found")
            return
        
        batch_job.status = "processing"
        batch_job.started_at = datetime.utcnow()
        db.commit()
        
        results = []
        completed_requests = 0
        error_count = 0
        total_images_generated = 0
        total_cost = 0.0
        
        for i, request in enumerate(requests):
            logger.info(f"Processing request {i+1}/{len(requests)} in batch {batch_id}")
            
            try:
                # Generate images using Bedrock
                images = bedrock_service.generate_images(
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt,
                    num_images=request.num_images,
                    guidance_scale=request.guidance_scale,
                    seed=request.seed,
                    size=request.size,
                )
                
                # Upload to S3 and save to database
                generated_images = []
                for idx, img_bytes in enumerate(images):
                    image_id = f"{batch_id}_{i}_{idx}"
                    key = f"batch/{batch_id}/{image_id}.png"
                    s3_url = s3_service.upload_bytes(img_bytes, key)
                    presigned_url = s3_service.generate_presigned_url(key)
                    
                    # Calculate cost for this image
                    image_cost = calculate_generation_cost(
                        model_id=settings.bedrock_model_id,
                        num_images=1,
                        size=request.size
                    )
                    
                    # Save image to database
                    db_image = DBGeneratedImage(
                        id=image_id,
                        user_id=user.id,
                        prompt=request.prompt,
                        negative_prompt=request.negative_prompt,
                        size=request.size,
                        s3_url=s3_url,
                        s3_key=key,
                        guidance_scale=request.guidance_scale,
                        seed=request.seed,
                        template_id=request.template_id,
                        batch_id=batch_id,
                        batch_index=i,
                        generation_cost=str(image_cost),
                        brand_style=str(request.brand_style) if request.brand_style else None,
                        processing_time=0.0  # Per-image processing time not tracked for batch
                    )
                    db.add(db_image)
                    
                    # Create response object
                    generated_image = GeneratedImage(
                        id=image_id,
                        s3_url=s3_url,
                        presigned_url=presigned_url,
                        prompt=request.prompt,
                        size=request.size,
                        metadata={
                            "batch_id": batch_id,
                            "request_index": i,
                            "image_index": idx,
                            "template_id": request.template_id,
                            "brand_style": request.brand_style,
                            "generation_cost": image_cost
                        }
                    )
                    generated_images.append(generated_image)
                    
                    total_images_generated += 1
                    total_cost += image_cost
                
                # Create response for this request
                actual_cost = calculate_generation_cost(
                    model_id=settings.bedrock_model_id,
                    num_images=len(generated_images),
                    size=request.size
                )
                response = GenerateResponse(
                    images=generated_images,
                    processing_time=0.0,  # Processing time tracked per batch, not per request
                    total_cost=actual_cost
                )
                results.append(response)
                completed_requests += 1
                
            except Exception as e:
                logger.error(f"Error processing request {i+1} in batch {batch_id}: {e}")
                error_count += 1
                # Add empty response for failed request
                results.append(GenerateResponse(images=[]))
            
            # Update progress and save to database
            batch_job.completed_requests = completed_requests
            batch_job.error_count = error_count
            batch_job.progress = (completed_requests / len(requests)) * 100
            batch_job.updated_at = datetime.utcnow()
            db.commit()
            
            # Small delay to prevent overwhelming the service
            await asyncio.sleep(0.1)
        
        # Update user statistics
        user.total_images_generated += total_images_generated
        user.total_cost_spent = str(float(user.total_cost_spent) + total_cost)
        
        # Finalize batch job and save to database
        batch_job.status = "completed" if error_count == 0 else "completed_with_errors"
        batch_job.results_data = json.dumps([r.dict() for r in results], default=str)
        batch_job.completed_at = datetime.utcnow()
        batch_job.updated_at = datetime.utcnow()
        batch_job.actual_cost = str(total_cost)
        db.commit()
        
        logger.info(f"Completed batch job {batch_id}: {completed_requests} successful, {error_count} errors, {total_images_generated} images generated")
        
    finally:
        db.close()


@router.post("/generate", response_model=BatchGenerateResponse)
async def create_batch_job(
    request: BatchGenerateRequest, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> BatchGenerateResponse:
    """Create a new batch generation job."""
    
    # Validate batch size
    if len(request.requests) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 requests per batch")
    
    # Generate batch ID
    batch_id = request.batch_id or f"batch_{uuid.uuid4().hex[:8]}"
    
    # Check if batch ID already exists
    existing_job = db.query(DBBatchJob).filter(DBBatchJob.id == batch_id).first()
    if existing_job:
        raise HTTPException(status_code=409, detail=f"Batch ID '{batch_id}' already exists")
    
    # Calculate estimated cost
    total_estimated_cost = sum(
        calculate_generation_cost(settings.bedrock_model_id, req.num_images, req.size)
        for req in request.requests
    )
    
    # Create batch job in database
    batch_job = DBBatchJob(
        id=batch_id,
        user_id=current_user.id,
        status="queued",
        priority=request.priority,
        total_requests=len(request.requests),
        completed_requests=0,
        progress=0.0,
        estimated_cost=str(total_estimated_cost),
        requests_data=json.dumps([req.dict() for req in request.requests], default=str)
    )
    
    db.add(batch_job)
    db.commit()
    db.refresh(batch_job)
    
    # Start background processing
    background_tasks.add_task(process_batch_job, batch_id, request.requests)
    
    logger.info(f"Created batch job {batch_id} with {len(request.requests)} requests")
    
    return BatchGenerateResponse(
        batch_id=batch_id,
        total_requests=len(request.requests),
        status="queued",
        estimated_completion=datetime.utcnow() + timedelta(minutes=len(request.requests) * 2)
    )


@router.get("/{batch_id}/status", response_model=BatchStatusResponse)
async def get_batch_status(
    batch_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> BatchStatusResponse:
    """Get the status of a batch job."""
    batch_job = db.query(DBBatchJob).filter(
        DBBatchJob.id == batch_id,
        DBBatchJob.user_id == current_user.id
    ).first()
    
    if not batch_job:
        raise HTTPException(status_code=404, detail=f"Batch job '{batch_id}' not found")
    
    # Convert results from JSON string if available
    results = None
    if batch_job.results_data:
        try:
            results_data = json.loads(batch_job.results_data)
            results = [GenerateResponse(**r) for r in results_data]
        except:
            pass
    
    return BatchStatusResponse(
        batch_id=batch_job.id,
        status=batch_job.status,
        progress=batch_job.progress,
        completed_requests=batch_job.completed_requests,
        total_requests=batch_job.total_requests,
        results=results,
        error_count=batch_job.error_count,
        created_at=batch_job.created_at,
        updated_at=batch_job.updated_at
    )


@router.get("/", response_model=List[BatchStatusResponse])
async def list_batch_jobs(
    limit: int = 20,
    status: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[BatchStatusResponse]:
    """List recent batch jobs, optionally filtered by status."""
    query = db.query(DBBatchJob).filter(DBBatchJob.user_id == current_user.id)
    
    # Filter by status if provided
    if status:
        query = query.filter(DBBatchJob.status == status)
    
    # Sort by creation time (newest first) and limit
    jobs = query.order_by(DBBatchJob.created_at.desc()).limit(limit).all()
    
    return [
        BatchStatusResponse(
            batch_id=job.id,
            status=job.status,
            progress=job.progress,
            completed_requests=job.completed_requests,
            total_requests=job.total_requests,
            results=None,  # Don't include results in list view
            error_count=job.error_count,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        for job in jobs
    ]


@router.delete("/{batch_id}")
async def cancel_batch_job(
    batch_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a batch job (if it's still queued)."""
    batch_job = db.query(DBBatchJob).filter(
        DBBatchJob.id == batch_id,
        DBBatchJob.user_id == current_user.id
    ).first()
    
    if not batch_job:
        raise HTTPException(status_code=404, detail=f"Batch job '{batch_id}' not found")
    if batch_job.status not in ["queued", "processing"]:
        raise HTTPException(status_code=400, detail="Can only cancel queued or processing jobs")
    
    batch_job.status = "cancelled"
    batch_job.updated_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Cancelled batch job {batch_id}")
    return {"message": f"Batch job '{batch_id}' cancelled successfully"}


# Cleanup old completed jobs (could be a scheduled task)
def cleanup_old_jobs():
    """Remove batch jobs older than 24 hours."""
    from ..models.database import SessionLocal
    
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    db = SessionLocal()
    
    try:
        old_jobs = db.query(DBBatchJob).filter(
            DBBatchJob.status.in_(["completed", "completed_with_errors", "cancelled"]),
            DBBatchJob.updated_at < cutoff_time
        ).all()
        
        for job in old_jobs:
            logger.info(f"Cleaning up old batch job {job.id}")
            db.delete(job)
        
        db.commit()
        logger.info(f"Cleaned up {len(old_jobs)} old batch jobs")
        
    finally:
        db.close() 