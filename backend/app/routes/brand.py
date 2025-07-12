from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from ..models import get_db, User, BrandProfile, BrandAsset, Campaign, Industry
from ..models.schemas import UserOut
from ..core.auth import get_current_user
from ..services.brand_manager import BrandManager

router = APIRouter(prefix="/brands", tags=["brands"])
brand_manager = BrandManager()


# Pydantic models for request/response
from pydantic import BaseModel, Field
from enum import Enum


class BrandProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Industry
    brand_values: List[str] = Field(default_factory=list)
    target_audience: Dict[str, Any] = Field(default_factory=dict)
    competitors: List[str] = Field(default_factory=list)
    unique_selling_points: List[str] = Field(default_factory=list)
    primary_colors: List[str] = Field(default_factory=list)
    secondary_colors: List[str] = Field(default_factory=list)
    font_families: Dict[str, str] = Field(default_factory=dict)
    logo_style: Optional[str] = None
    visual_style: Optional[str] = None
    preferred_image_styles: List[str] = Field(default_factory=list)
    avoided_elements: List[str] = Field(default_factory=list)
    brand_keywords: List[str] = Field(default_factory=list)


class BrandProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[Industry] = None
    brand_values: Optional[List[str]] = None
    target_audience: Optional[Dict[str, Any]] = None
    competitors: Optional[List[str]] = None
    unique_selling_points: Optional[List[str]] = None
    primary_colors: Optional[List[str]] = None
    secondary_colors: Optional[List[str]] = None
    font_families: Optional[Dict[str, str]] = None
    logo_style: Optional[str] = None
    visual_style: Optional[str] = None
    preferred_image_styles: Optional[List[str]] = None
    avoided_elements: Optional[List[str]] = None
    brand_keywords: Optional[List[str]] = None


class BrandProfileResponse(BaseModel):
    id: int
    user_id: str
    name: str
    description: Optional[str]
    industry: str
    brand_values: List[str]
    target_audience: Dict[str, Any]
    competitors: List[str]
    unique_selling_points: List[str]
    primary_colors: List[str]
    secondary_colors: List[str]
    font_families: Dict[str, str]
    logo_style: Optional[str]
    visual_style: Optional[str]
    preferred_image_styles: List[str]
    avoided_elements: List[str]
    brand_keywords: List[str]
    avg_engagement_rate: float
    total_generations: int
    successful_campaigns: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BrandAssetResponse(BaseModel):
    id: int
    brand_profile_id: int
    asset_type: str
    asset_name: str
    asset_url: str
    dominant_colors: Optional[List[Dict[str, Any]]]
    style_attributes: Optional[Dict[str, Any]]
    text_elements: Optional[List[Dict[str, Any]]]
    composition_data: Optional[Dict[str, Any]]
    file_size: Optional[int]
    dimensions: Optional[Dict[str, Any]]
    file_format: Optional[str]
    analysis_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_platforms: List[str] = Field(default_factory=list)
    target_metrics: Dict[str, Any] = Field(default_factory=dict)


class CampaignResponse(BaseModel):
    id: int
    brand_profile_id: int
    user_id: str
    name: str
    description: Optional[str]
    campaign_type: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    target_platforms: List[str]
    target_metrics: Dict[str, Any]
    status: str
    total_assets_generated: int
    actual_metrics: Optional[Dict[str, Any]]
    roi: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BrandConsistencyReport(BaseModel):
    overall_score: float
    color_consistency: Dict[str, Any]
    style_consistency: Dict[str, Any]
    guideline_compliance: Dict[str, Any]
    recommendations: List[str]


class BrandInsights(BaseModel):
    brand_profile: Dict[str, Any]
    color_insights: Dict[str, Any]
    style_insights: Dict[str, Any]
    asset_insights: Dict[str, Any]
    recommendations: List[str]


@router.post("/profiles", response_model=BrandProfileResponse)
async def create_brand_profile(
    brand_data: BrandProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new brand profile."""
    try:
        brand_profile = await brand_manager.create_brand_profile(
            db=db,
            user_id=current_user.id,
            name=brand_data.name,
            description=brand_data.description,
            industry=brand_data.industry,
            brand_data=brand_data.model_dump()
        )
        
        return BrandProfileResponse(
            id=brand_profile.id,
            user_id=brand_profile.user_id,
            name=brand_profile.name,
            description=brand_profile.description,
            industry=brand_profile.industry.value,
            brand_values=brand_profile.brand_values or [],
            target_audience=brand_profile.target_audience or {},
            competitors=brand_profile.competitors or [],
            unique_selling_points=brand_profile.unique_selling_points or [],
            primary_colors=brand_profile.primary_colors or [],
            secondary_colors=brand_profile.secondary_colors or [],
            font_families=brand_profile.font_families or {},
            logo_style=brand_profile.logo_style,
            visual_style=brand_profile.visual_style,
            preferred_image_styles=brand_profile.preferred_image_styles or [],
            avoided_elements=brand_profile.avoided_elements or [],
            brand_keywords=brand_profile.brand_keywords or [],
            avg_engagement_rate=brand_profile.avg_engagement_rate,
            total_generations=brand_profile.total_generations,
            successful_campaigns=brand_profile.successful_campaigns,
            created_at=brand_profile.created_at,
            updated_at=brand_profile.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles", response_model=List[BrandProfileResponse])
async def list_brand_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all brand profiles for the current user."""
    profiles = db.query(BrandProfile).filter_by(user_id=current_user.id).all()
    
    return [
        BrandProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            description=profile.description,
            industry=profile.industry.value,
            brand_values=profile.brand_values or [],
            target_audience=profile.target_audience or {},
            competitors=profile.competitors or [],
            unique_selling_points=profile.unique_selling_points or [],
            primary_colors=profile.primary_colors or [],
            secondary_colors=profile.secondary_colors or [],
            font_families=profile.font_families or {},
            logo_style=profile.logo_style,
            visual_style=profile.visual_style,
            preferred_image_styles=profile.preferred_image_styles or [],
            avoided_elements=profile.avoided_elements or [],
            brand_keywords=profile.brand_keywords or [],
            avg_engagement_rate=profile.avg_engagement_rate,
            total_generations=profile.total_generations,
            successful_campaigns=profile.successful_campaigns,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        for profile in profiles
    ]


@router.get("/profiles/{profile_id}", response_model=BrandProfileResponse)
async def get_brand_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific brand profile."""
    profile = db.query(BrandProfile).filter_by(
        id=profile_id,
        user_id=current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    return BrandProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        name=profile.name,
        description=profile.description,
        industry=profile.industry.value,
        brand_values=profile.brand_values or [],
        target_audience=profile.target_audience or {},
        competitors=profile.competitors or [],
        unique_selling_points=profile.unique_selling_points or [],
        primary_colors=profile.primary_colors or [],
        secondary_colors=profile.secondary_colors or [],
        font_families=profile.font_families or {},
        logo_style=profile.logo_style,
        visual_style=profile.visual_style,
        preferred_image_styles=profile.preferred_image_styles or [],
        avoided_elements=profile.avoided_elements or [],
        brand_keywords=profile.brand_keywords or [],
        avg_engagement_rate=profile.avg_engagement_rate,
        total_generations=profile.total_generations,
        successful_campaigns=profile.successful_campaigns,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )


@router.put("/profiles/{profile_id}", response_model=BrandProfileResponse)
async def update_brand_profile(
    profile_id: int,
    update_data: BrandProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a brand profile."""
    profile = db.query(BrandProfile).filter_by(
        id=profile_id,
        user_id=current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return BrandProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        name=profile.name,
        description=profile.description,
        industry=profile.industry.value,
        brand_values=profile.brand_values or [],
        target_audience=profile.target_audience or {},
        competitors=profile.competitors or [],
        unique_selling_points=profile.unique_selling_points or [],
        primary_colors=profile.primary_colors or [],
        secondary_colors=profile.secondary_colors or [],
        font_families=profile.font_families or {},
        logo_style=profile.logo_style,
        visual_style=profile.visual_style,
        preferred_image_styles=profile.preferred_image_styles or [],
        avoided_elements=profile.avoided_elements or [],
        brand_keywords=profile.brand_keywords or [],
        avg_engagement_rate=profile.avg_engagement_rate,
        total_generations=profile.total_generations,
        successful_campaigns=profile.successful_campaigns,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )


@router.delete("/profiles/{profile_id}")
async def delete_brand_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a brand profile."""
    profile = db.query(BrandProfile).filter_by(
        id=profile_id,
        user_id=current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    db.delete(profile)
    db.commit()
    
    return {"message": "Brand profile deleted successfully"}


@router.post("/profiles/{profile_id}/assets", response_model=BrandAssetResponse)
async def upload_brand_asset(
    profile_id: int,
    file: UploadFile = File(...),
    asset_type: str = Form(...),
    asset_name: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a brand asset."""
    # Verify profile ownership
    profile = db.query(BrandProfile).filter_by(
        id=profile_id,
        user_id=current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    try:
        asset = await brand_manager.upload_brand_asset(
            db=db,
            brand_profile_id=profile_id,
            file=file,
            asset_type=asset_type,
            asset_name=asset_name
        )
        
        return BrandAssetResponse(
            id=asset.id,
            brand_profile_id=asset.brand_profile_id,
            asset_type=asset.asset_type,
            asset_name=asset.asset_name,
            asset_url=asset.asset_url,
            dominant_colors=asset.dominant_colors,
            style_attributes=asset.style_attributes,
            text_elements=asset.text_elements,
            composition_data=asset.composition_data,
            file_size=asset.file_size,
            dimensions=asset.dimensions,
            file_format=asset.file_format,
            analysis_completed=asset.analysis_completed,
            created_at=asset.created_at,
            updated_at=asset.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{profile_id}/assets", response_model=List[BrandAssetResponse])
async def list_brand_assets(
    profile_id: int,
    asset_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List brand assets."""
    # Verify profile ownership
    profile = db.query(BrandProfile).filter_by(
        id=profile_id,
        user_id=current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    query = db.query(BrandAsset).filter_by(brand_profile_id=profile_id)
    if asset_type:
        query = query.filter_by(asset_type=asset_type)
    
    assets = query.all()
    
    return [
        BrandAssetResponse(
            id=asset.id,
            brand_profile_id=asset.brand_profile_id,
            asset_type=asset.asset_type,
            asset_name=asset.asset_name,
            asset_url=asset.asset_url,
            dominant_colors=asset.dominant_colors,
            style_attributes=asset.style_attributes,
            text_elements=asset.text_elements,
            composition_data=asset.composition_data,
            file_size=asset.file_size,
            dimensions=asset.dimensions,
            file_format=asset.file_format,
            analysis_completed=asset.analysis_completed,
            created_at=asset.created_at,
            updated_at=asset.updated_at
        )
        for asset in assets
    ]


@router.delete("/profiles/{profile_id}/assets/{asset_id}")
async def delete_brand_asset(
    profile_id: int,
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a brand asset."""
    # Verify profile ownership
    profile = db.query(BrandProfile).filter_by(
        id=profile_id,
        user_id=current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    asset = db.query(BrandAsset).filter_by(
        id=asset_id,
        brand_profile_id=profile_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Brand asset not found")
    
    # Delete from S3
    try:
        s3_key = asset.asset_url.split('/')[-1]
        brand_manager.s3_client.delete_object(
            Bucket=brand_manager.bucket_name,
            Key=f"brand-assets/{profile_id}/{s3_key}"
        )
    except Exception as e:
        # Log error but continue with database deletion
        pass
    
    db.delete(asset)
    db.commit()
    
    return {"message": "Brand asset deleted successfully"}


@router.post("/profiles/{profile_id}/analyze-consistency", response_model=BrandConsistencyReport)
async def analyze_brand_consistency(
    profile_id: int,
    image_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze how well an image matches brand guidelines."""
    # Verify profile ownership
    profile = db.query(BrandProfile).filter_by(
        id=profile_id,
        user_id=current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    try:
        consistency_report = await brand_manager.analyze_brand_consistency(
            db=db,
            brand_profile_id=profile_id,
            image_url=image_url
        )
        
        return BrandConsistencyReport(**consistency_report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profiles/{profile_id}/campaigns", response_model=CampaignResponse)
async def create_campaign(
    profile_id: int,
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new campaign for a brand profile."""
    # Verify profile ownership
    profile = db.query(BrandProfile).filter_by(
        id=profile_id,
        user_id=current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    try:
        campaign = await brand_manager.create_campaign(
            db=db,
            brand_profile_id=profile_id,
            user_id=current_user.id,
            campaign_data=campaign_data.model_dump()
        )
        
        return CampaignResponse(
            id=campaign.id,
            brand_profile_id=campaign.brand_profile_id,
            user_id=campaign.user_id,
            name=campaign.name,
            description=campaign.description,
            campaign_type=campaign.campaign_type,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            target_platforms=campaign.target_platforms or [],
            target_metrics=campaign.target_metrics or {},
            status=campaign.status,
            total_assets_generated=campaign.total_assets_generated,
            actual_metrics=campaign.actual_metrics,
            roi=campaign.roi,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{profile_id}/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List campaigns for a brand profile."""
    # Verify profile ownership
    profile = db.query(BrandProfile).filter_by(
        id=profile_id,
        user_id=current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    campaigns = db.query(Campaign).filter_by(brand_profile_id=profile_id).all()
    
    return [
        CampaignResponse(
            id=campaign.id,
            brand_profile_id=campaign.brand_profile_id,
            user_id=campaign.user_id,
            name=campaign.name,
            description=campaign.description,
            campaign_type=campaign.campaign_type,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            target_platforms=campaign.target_platforms or [],
            target_metrics=campaign.target_metrics or {},
            status=campaign.status,
            total_assets_generated=campaign.total_assets_generated,
            actual_metrics=campaign.actual_metrics,
            roi=campaign.roi,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at
        )
        for campaign in campaigns
    ]


@router.get("/profiles/{profile_id}/insights", response_model=BrandInsights)
async def get_brand_insights(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get insights and analytics for a brand profile."""
    # Verify profile ownership
    profile = db.query(BrandProfile).filter_by(
        id=profile_id,
        user_id=current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    try:
        insights = await brand_manager.get_brand_insights(
            db=db,
            brand_profile_id=profile_id
        )
        
        return BrandInsights(**insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))