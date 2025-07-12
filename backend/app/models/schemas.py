from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, HttpUrl, validator


class UserOut(BaseModel):
    """Schema for user output."""
    
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    is_active: bool = Field(True, description="Whether user is active")
    is_premium: bool = Field(False, description="Whether user has premium subscription")
    total_images_generated: int = Field(0, description="Total images generated")
    total_cost_spent: str = Field("0.00", description="Total cost spent")
    created_at: datetime = Field(..., description="Account creation date")
    
    class Config:
        from_attributes = True


class GenerateRequest(BaseModel):
    """Schema for image generation request."""

    prompt: str = Field(..., min_length=1, max_length=1000, description="Base prompt describing the image")
    negative_prompt: Optional[str] = Field(
        None, max_length=500, description="Concepts to avoid during generation"
    )
    num_images: int = Field(1, ge=1, le=10, description="Number of images to generate")
    size: str = Field("1024x1024", pattern=r"^\d{3,4}x\d{3,4}$")
    guidance_scale: float = Field(7.5, ge=1, le=20)
    seed: Optional[int] = Field(None, ge=0)
    template_id: Optional[str] = Field(None, description="Template ID to use for generation")
    brand_style: Optional[Dict[str, Any]] = Field(None, description="Brand style parameters")
    campaign_id: Optional[int] = Field(None, description="Campaign ID to associate with generated images")
    
    # Professional quality parameters
    quality: Optional[str] = Field(None, description="Image quality level (standard, high, ultra, professional)")
    style: Optional[str] = Field(None, description="Style category (photorealistic, artistic, technical, marketing, product)")
    composition: Optional[str] = Field(None, description="Composition rule (rule_of_thirds, center_composition, leading_lines, symmetry, golden_ratio)")
    lighting: Optional[str] = Field(None, description="Lighting preset (professional, studio, natural, dramatic, soft, golden_hour)")


class GeneratedImage(BaseModel):
    """Schema for a generated image response."""
    
    id: str = Field(..., description="Unique image ID")
    s3_url: HttpUrl = Field(..., description="Direct S3 URL")
    presigned_url: HttpUrl = Field(..., description="Pre-signed download URL")
    prompt: str = Field(..., description="Prompt used for generation")
    size: str = Field(..., description="Image dimensions")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class GenerateResponse(BaseModel):
    """Schema for image generation response."""
    
    images: List[GeneratedImage] = Field(..., description="Generated images")
    total_cost: Optional[float] = Field(None, description="Estimated cost in USD")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")


class Template(BaseModel):
    """Schema for image generation templates."""
    
    id: str = Field(..., description="Unique template ID")
    name: str = Field(..., description="Template name")
    category: str = Field(..., description="Template category")
    description: str = Field(..., description="Template description")
    prompt_template: str = Field(..., description="Prompt template with placeholders")
    negative_prompt: Optional[str] = Field(None, description="Default negative prompt")
    default_size: str = Field("1024x1024", description="Default image size")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Template parameters")
    is_active: bool = Field(True, description="Whether template is active")


class BatchGenerateRequest(BaseModel):
    """Schema for batch image generation."""
    
    requests: List[GenerateRequest] = Field(..., min_items=1, max_items=50)
    batch_id: Optional[str] = Field(None, description="Custom batch ID")
    priority: str = Field("normal", pattern="^(low|normal|high)$")


class BatchGenerateResponse(BaseModel):
    """Schema for batch generation response."""
    
    batch_id: str = Field(..., description="Batch ID")
    total_requests: int = Field(..., description="Total number of requests")
    status: str = Field(..., description="Batch status")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    results: Optional[List[GenerateResponse]] = Field(None, description="Generation results")


class BatchStatusResponse(BaseModel):
    """Schema for batch status response."""
    
    batch_id: str = Field(..., description="Batch ID")
    status: str = Field(..., description="Batch status")
    progress: float = Field(..., ge=0, le=100, description="Progress percentage")
    completed_requests: int = Field(..., description="Number of completed requests")
    total_requests: int = Field(..., description="Total number of requests")
    results: Optional[List[GenerateResponse]] = Field(None, description="Completed results")
    error_count: int = Field(0, description="Number of failed requests")
    created_at: datetime = Field(..., description="Batch creation time")
    updated_at: datetime = Field(..., description="Last update time")


class UploadUrlResponse(BaseModel):
    """Schema for S3 upload URL response."""
    
    upload_url: HttpUrl = Field(..., description="Pre-signed upload URL")
    object_key: str = Field(..., description="S3 object key")
    expires_at: datetime = Field(..., description="URL expiration time")


class BrandAsset(BaseModel):
    """Schema for brand assets."""
    
    id: str = Field(..., description="Asset ID")
    name: str = Field(..., description="Asset name")
    type: str = Field(..., description="Asset type (logo, color_palette, sample_image)")
    s3_url: HttpUrl = Field(..., description="Asset S3 URL")
    presigned_url: HttpUrl = Field(..., description="Pre-signed download URL")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Asset metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class VectorGenerateRequest(BaseModel):
    """Schema for vector image generation request."""

    prompt: str = Field(..., min_length=1, max_length=1000, description="Base prompt describing the vector image")
    negative_prompt: Optional[str] = Field(
        None, max_length=500, description="Concepts to avoid during generation"
    )
    num_images: int = Field(1, ge=1, le=10, description="Number of vector images to generate")
    size: str = Field("512x512", pattern=r"^\d{3,4}x\d{3,4}$")
    style: str = Field("modern", description="Vector style (modern, minimalist, artistic, geometric, organic)")
    seed: Optional[int] = Field(None, ge=0, description="Random seed for reproducibility")
    format: str = Field("svg", pattern="^(svg|base64)$", description="Output format")


class GeneratedVector(BaseModel):
    """Schema for a generated vector image response."""
    
    id: str = Field(..., description="Unique vector image ID")
    svg_content: Optional[str] = Field(None, description="Raw SVG content")
    svg_base64: Optional[str] = Field(None, description="Base64 encoded SVG")
    s3_url: Optional[HttpUrl] = Field(None, description="Direct S3 URL if stored")
    presigned_url: Optional[HttpUrl] = Field(None, description="Pre-signed download URL if stored")
    prompt: str = Field(..., description="Prompt used for generation")
    size: str = Field(..., description="Vector image dimensions")
    style: str = Field(..., description="Applied style")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class VectorGenerateResponse(BaseModel):
    """Schema for vector image generation response."""
    
    vectors: List[GeneratedVector] = Field(..., description="Generated vector images")
    total_cost: Optional[float] = Field(None, description="Estimated cost in USD")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")


class HealthResponse(BaseModel):
    """Schema for health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str] = Field(..., description="Dependent service statuses") 