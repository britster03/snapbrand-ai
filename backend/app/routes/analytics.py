from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from pydantic import BaseModel, Field
import json

from ..models import (
    get_db, User, BrandProfile, GeneratedImage, Campaign,
    PerformanceMetric, TeamMember
)
from ..core.auth import get_current_user
from ..models.brand import Industry

router = APIRouter(prefix="/analytics", tags=["analytics"])


# Pydantic models
class PerformanceMetricCreate(BaseModel):
    brand_profile_id: int
    generated_image_id: Optional[str] = None
    campaign_id: Optional[int] = None
    metric_type: str = Field(..., pattern="^(engagement|conversion|reach|click_through|impression|share|save)$")
    metric_value: float = Field(..., ge=0)
    metric_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    platform: Optional[str] = None
    variant_id: Optional[str] = None
    is_control: bool = False


class PerformanceMetricResponse(BaseModel):
    id: int
    brand_profile_id: int
    generated_image_id: Optional[str]
    campaign_id: Optional[int]
    metric_type: str
    metric_value: float
    metric_data: Dict[str, Any]
    platform: Optional[str]
    recorded_at: datetime
    variant_id: Optional[str]
    is_control: bool

    class Config:
        from_attributes = True


class BrandAnalytics(BaseModel):
    brand_profile_id: int
    brand_name: str
    time_period: str
    summary: Dict[str, Any]
    performance_by_metric: Dict[str, Any]
    performance_by_platform: Dict[str, Any]
    top_performing_content: List[Dict[str, Any]]
    conversion_funnel: Dict[str, Any]
    recommendations: List[str]


class CampaignAnalytics(BaseModel):
    campaign_id: int
    campaign_name: str
    status: str
    duration: Dict[str, Any]
    performance_summary: Dict[str, Any]
    platform_breakdown: Dict[str, Any]
    content_performance: List[Dict[str, Any]]
    roi_analysis: Dict[str, Any]
    ab_test_results: Optional[Dict[str, Any]]


class ContentPerformance(BaseModel):
    image_id: str
    image_url: str
    prompt: str
    created_at: datetime
    metrics: Dict[str, float]
    engagement_rate: float
    conversion_rate: float
    performance_score: float
    platform_performance: Dict[str, Dict[str, float]]


@router.post("/metrics", response_model=PerformanceMetricResponse)
async def record_performance_metric(
    metric: PerformanceMetricCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a performance metric for an image or campaign."""
    
    # Verify brand access
    brand = db.query(BrandProfile).filter_by(id=metric.brand_profile_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    is_owner = brand.user_id == current_user.id
    is_member = db.query(TeamMember).filter_by(
        brand_profile_id=metric.brand_profile_id,
        user_id=current_user.id
    ).first()
    
    if not is_owner and not is_member:
        raise HTTPException(status_code=403, detail="Not authorized to record metrics")
    
    # Verify image if provided
    if metric.generated_image_id:
        image = db.query(GeneratedImage).filter_by(id=metric.generated_image_id).first()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
    
    # Verify campaign if provided
    if metric.campaign_id:
        campaign = db.query(Campaign).filter_by(id=metric.campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Create metric
    db_metric = PerformanceMetric(
        brand_profile_id=metric.brand_profile_id,
        generated_image_id=metric.generated_image_id,
        campaign_id=metric.campaign_id,
        metric_type=metric.metric_type,
        metric_value=metric.metric_value,
        metric_data=metric.metric_data,
        platform=metric.platform,
        variant_id=metric.variant_id,
        is_control=metric.is_control
    )
    
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    
    return PerformanceMetricResponse(
        id=db_metric.id,
        brand_profile_id=db_metric.brand_profile_id,
        generated_image_id=db_metric.generated_image_id,
        campaign_id=db_metric.campaign_id,
        metric_type=db_metric.metric_type,
        metric_value=db_metric.metric_value,
        metric_data=db_metric.metric_data or {},
        platform=db_metric.platform,
        recorded_at=db_metric.recorded_at,
        variant_id=db_metric.variant_id,
        is_control=db_metric.is_control
    )


@router.get("/brand/{brand_profile_id}", response_model=BrandAnalytics)
async def get_brand_analytics(
    brand_profile_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for a brand profile."""
    
    # Verify access
    brand = db.query(BrandProfile).filter_by(id=brand_profile_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    is_owner = brand.user_id == current_user.id
    is_member = db.query(TeamMember).filter_by(
        brand_profile_id=brand_profile_id,
        user_id=current_user.id
    ).first()
    
    if not is_owner and not is_member:
        raise HTTPException(status_code=403, detail="Not authorized to view analytics")
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get all metrics for the period
    metrics = db.query(PerformanceMetric).filter(
        and_(
            PerformanceMetric.brand_profile_id == brand_profile_id,
            PerformanceMetric.recorded_at >= start_date
        )
    ).all()
    
    # Calculate summary statistics
    summary = _calculate_summary_stats(metrics)
    
    # Performance by metric type
    performance_by_metric = _calculate_performance_by_metric(metrics)
    
    # Performance by platform
    performance_by_platform = _calculate_performance_by_platform(metrics)
    
    # Top performing content
    top_content = _get_top_performing_content(db, brand_profile_id, start_date, limit=10)
    
    # Conversion funnel
    conversion_funnel = _calculate_conversion_funnel(metrics)
    
    # Generate recommendations
    recommendations = _generate_analytics_recommendations(
        brand, summary, performance_by_metric, performance_by_platform
    )
    
    return BrandAnalytics(
        brand_profile_id=brand_profile_id,
        brand_name=brand.name,
        time_period=f"Last {days} days",
        summary=summary,
        performance_by_metric=performance_by_metric,
        performance_by_platform=performance_by_platform,
        top_performing_content=top_content,
        conversion_funnel=conversion_funnel,
        recommendations=recommendations
    )


@router.get("/campaign/{campaign_id}", response_model=CampaignAnalytics)
async def get_campaign_analytics(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific campaign."""
    
    # Get campaign
    campaign = db.query(Campaign).filter_by(id=campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Verify access
    brand = db.query(BrandProfile).filter_by(id=campaign.brand_profile_id).first()
    is_owner = brand.user_id == current_user.id
    is_member = db.query(TeamMember).filter_by(
        brand_profile_id=campaign.brand_profile_id,
        user_id=current_user.id
    ).first()
    
    if not is_owner and not is_member:
        raise HTTPException(status_code=403, detail="Not authorized to view campaign analytics")
    
    # Get campaign metrics
    metrics = db.query(PerformanceMetric).filter_by(campaign_id=campaign_id).all()
    
    # Calculate duration
    duration = _calculate_campaign_duration(campaign)
    
    # Performance summary
    performance_summary = _calculate_campaign_performance(metrics, campaign)
    
    # Platform breakdown
    platform_breakdown = _calculate_performance_by_platform(metrics)
    
    # Content performance
    content_performance = _get_campaign_content_performance(db, campaign_id)
    
    # ROI analysis
    roi_analysis = _calculate_roi(campaign, metrics)
    
    # A/B test results if applicable
    ab_test_results = _analyze_ab_tests(metrics) if _has_ab_tests(metrics) else None
    
    return CampaignAnalytics(
        campaign_id=campaign_id,
        campaign_name=campaign.name,
        status=campaign.status,
        duration=duration,
        performance_summary=performance_summary,
        platform_breakdown=platform_breakdown,
        content_performance=content_performance,
        roi_analysis=roi_analysis,
        ab_test_results=ab_test_results
    )


@router.get("/content/{image_id}", response_model=ContentPerformance)
async def get_content_performance(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance analytics for a specific image."""
    
    # Get image
    image = db.query(GeneratedImage).filter_by(id=image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Verify access
    if image.user_id != current_user.id:
        # Check if user has access through brand profile
        if image.brand_profile_id:
            is_member = db.query(TeamMember).filter_by(
                brand_profile_id=image.brand_profile_id,
                user_id=current_user.id
            ).first()
            if not is_member:
                raise HTTPException(status_code=403, detail="Not authorized to view content analytics")
        else:
            raise HTTPException(status_code=403, detail="Not authorized to view content analytics")
    
    # Get metrics
    metrics = db.query(PerformanceMetric).filter_by(generated_image_id=image_id).all()
    
    # Calculate aggregated metrics
    metric_summary = {}
    platform_performance = {}
    
    for metric in metrics:
        # Aggregate by type
        if metric.metric_type not in metric_summary:
            metric_summary[metric.metric_type] = 0
        metric_summary[metric.metric_type] += metric.metric_value
        
        # Aggregate by platform
        if metric.platform:
            if metric.platform not in platform_performance:
                platform_performance[metric.platform] = {}
            if metric.metric_type not in platform_performance[metric.platform]:
                platform_performance[metric.platform][metric.metric_type] = 0
            platform_performance[metric.platform][metric.metric_type] += metric.metric_value
    
    # Calculate rates
    impressions = metric_summary.get("impression", 1)
    engagement_rate = (
        (metric_summary.get("engagement", 0) + 
         metric_summary.get("click_through", 0) +
         metric_summary.get("share", 0) +
         metric_summary.get("save", 0)) / impressions * 100
    )
    conversion_rate = metric_summary.get("conversion", 0) / impressions * 100
    
    # Calculate performance score (weighted average)
    performance_score = (
        engagement_rate * 0.4 +
        conversion_rate * 0.6
    )
    
    return ContentPerformance(
        image_id=image_id,
        image_url=image.s3_url,
        prompt=image.prompt,
        created_at=image.created_at,
        metrics=metric_summary,
        engagement_rate=round(engagement_rate, 2),
        conversion_rate=round(conversion_rate, 2),
        performance_score=round(performance_score, 2),
        platform_performance=platform_performance
    )


@router.get("/comparison")
async def compare_performance(
    brand_profile_id: int,
    entity_type: str = Query(..., pattern="^(campaign|content|platform)$"),
    entity_ids: List[str] = Query(...),
    metric_types: List[str] = Query(["engagement", "conversion"]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare performance between multiple entities."""
    
    # Verify access
    brand = db.query(BrandProfile).filter_by(id=brand_profile_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    is_owner = brand.user_id == current_user.id
    is_member = db.query(TeamMember).filter_by(
        brand_profile_id=brand_profile_id,
        user_id=current_user.id
    ).first()
    
    if not is_owner and not is_member:
        raise HTTPException(status_code=403, detail="Not authorized to view analytics")
    
    comparison_data = []
    
    if entity_type == "campaign":
        for campaign_id in entity_ids:
            campaign = db.query(Campaign).filter_by(
                id=int(campaign_id),
                brand_profile_id=brand_profile_id
            ).first()
            
            if campaign:
                metrics = db.query(PerformanceMetric).filter_by(
                    campaign_id=campaign.id
                ).all()
                
                data = {
                    "entity_id": campaign_id,
                    "entity_name": campaign.name,
                    "metrics": _aggregate_metrics_by_type(metrics, metric_types)
                }
                comparison_data.append(data)
    
    elif entity_type == "content":
        for image_id in entity_ids:
            image = db.query(GeneratedImage).filter_by(
                id=image_id,
                brand_profile_id=brand_profile_id
            ).first()
            
            if image:
                metrics = db.query(PerformanceMetric).filter_by(
                    generated_image_id=image_id
                ).all()
                
                data = {
                    "entity_id": image_id,
                    "entity_name": image.prompt[:50] + "...",
                    "metrics": _aggregate_metrics_by_type(metrics, metric_types)
                }
                comparison_data.append(data)
    
    elif entity_type == "platform":
        for platform in entity_ids:
            metrics = db.query(PerformanceMetric).filter(
                and_(
                    PerformanceMetric.brand_profile_id == brand_profile_id,
                    PerformanceMetric.platform == platform
                )
            ).all()
            
            data = {
                "entity_id": platform,
                "entity_name": platform.title(),
                "metrics": _aggregate_metrics_by_type(metrics, metric_types)
            }
            comparison_data.append(data)
    
    return {
        "entity_type": entity_type,
        "comparison": comparison_data,
        "best_performer": _identify_best_performer(comparison_data, metric_types[0])
    }


# Helper functions
def _calculate_summary_stats(metrics: List[PerformanceMetric]) -> Dict[str, Any]:
    """Calculate summary statistics from metrics."""
    total_impressions = sum(m.metric_value for m in metrics if m.metric_type == "impression")
    total_engagements = sum(m.metric_value for m in metrics if m.metric_type == "engagement")
    total_conversions = sum(m.metric_value for m in metrics if m.metric_type == "conversion")
    
    return {
        "total_metrics": len(metrics),
        "total_impressions": int(total_impressions),
        "total_engagements": int(total_engagements),
        "total_conversions": int(total_conversions),
        "avg_engagement_rate": round(total_engagements / max(total_impressions, 1) * 100, 2),
        "avg_conversion_rate": round(total_conversions / max(total_impressions, 1) * 100, 2)
    }


def _calculate_performance_by_metric(metrics: List[PerformanceMetric]) -> Dict[str, Any]:
    """Calculate performance grouped by metric type."""
    performance = {}
    
    for metric in metrics:
        if metric.metric_type not in performance:
            performance[metric.metric_type] = {
                "total": 0,
                "count": 0,
                "average": 0
            }
        
        performance[metric.metric_type]["total"] += metric.metric_value
        performance[metric.metric_type]["count"] += 1
    
    # Calculate averages
    for metric_type in performance:
        performance[metric_type]["average"] = round(
            performance[metric_type]["total"] / performance[metric_type]["count"], 2
        )
    
    return performance


def _calculate_performance_by_platform(metrics: List[PerformanceMetric]) -> Dict[str, Any]:
    """Calculate performance grouped by platform."""
    platform_data = {}
    
    for metric in metrics:
        platform = metric.platform or "unknown"
        
        if platform not in platform_data:
            platform_data[platform] = {}
        
        if metric.metric_type not in platform_data[platform]:
            platform_data[platform][metric.metric_type] = 0
        
        platform_data[platform][metric.metric_type] += metric.metric_value
    
    return platform_data


def _get_top_performing_content(
    db: Session,
    brand_profile_id: int,
    start_date: datetime,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get top performing content based on engagement and conversion."""
    
    # Query to get images with their metrics
    images = db.query(GeneratedImage).filter(
        and_(
            GeneratedImage.brand_profile_id == brand_profile_id,
            GeneratedImage.created_at >= start_date
        )
    ).all()
    
    content_performance = []
    
    for image in images:
        metrics = db.query(PerformanceMetric).filter_by(
            generated_image_id=image.id
        ).all()
        
        if metrics:
            # Calculate performance score
            impressions = sum(m.metric_value for m in metrics if m.metric_type == "impression")
            engagements = sum(m.metric_value for m in metrics if m.metric_type == "engagement")
            conversions = sum(m.metric_value for m in metrics if m.metric_type == "conversion")
            
            if impressions > 0:
                engagement_rate = engagements / impressions
                conversion_rate = conversions / impressions
                performance_score = engagement_rate * 0.4 + conversion_rate * 0.6
                
                content_performance.append({
                    "image_id": image.id,
                    "image_url": image.s3_url,
                    "prompt": image.prompt[:100] + "...",
                    "created_at": image.created_at.isoformat(),
                    "impressions": int(impressions),
                    "engagements": int(engagements),
                    "conversions": int(conversions),
                    "engagement_rate": round(engagement_rate * 100, 2),
                    "conversion_rate": round(conversion_rate * 100, 2),
                    "performance_score": round(performance_score * 100, 2)
                })
    
    # Sort by performance score
    content_performance.sort(key=lambda x: x["performance_score"], reverse=True)
    
    return content_performance[:limit]


def _calculate_conversion_funnel(metrics: List[PerformanceMetric]) -> Dict[str, Any]:
    """Calculate conversion funnel stages."""
    
    funnel = {
        "impression": sum(m.metric_value for m in metrics if m.metric_type == "impression"),
        "engagement": sum(m.metric_value for m in metrics if m.metric_type == "engagement"),
        "click_through": sum(m.metric_value for m in metrics if m.metric_type == "click_through"),
        "conversion": sum(m.metric_value for m in metrics if m.metric_type == "conversion")
    }
    
    # Calculate drop-off rates
    if funnel["impression"] > 0:
        funnel["engagement_rate"] = round(funnel["engagement"] / funnel["impression"] * 100, 2)
        funnel["ctr"] = round(funnel["click_through"] / funnel["impression"] * 100, 2)
        funnel["conversion_rate"] = round(funnel["conversion"] / funnel["impression"] * 100, 2)
    else:
        funnel["engagement_rate"] = 0
        funnel["ctr"] = 0
        funnel["conversion_rate"] = 0
    
    return funnel


def _generate_analytics_recommendations(
    brand: BrandProfile,
    summary: Dict[str, Any],
    performance_by_metric: Dict[str, Any],
    performance_by_platform: Dict[str, Any]
) -> List[str]:
    """Generate actionable recommendations based on analytics."""
    
    recommendations = []
    
    # Engagement rate recommendations
    if summary["avg_engagement_rate"] < 2:
        recommendations.append(
            "Your engagement rate is below industry average. Consider A/B testing different visual styles and CTAs."
        )
    
    # Conversion rate recommendations
    if summary["avg_conversion_rate"] < 1:
        recommendations.append(
            "Conversion rate is low. Focus on clearer value propositions and stronger calls-to-action."
        )
    
    # Platform-specific recommendations
    if performance_by_platform:
        best_platform = max(
            performance_by_platform.items(),
            key=lambda x: x[1].get("conversion", 0)
        )[0]
        recommendations.append(
            f"{best_platform.title()} is your best performing platform. Consider allocating more resources there."
        )
    
    # Industry-specific recommendations
    industry_tips = {
        Industry.ECOMMERCE: "Show products in lifestyle contexts to improve engagement",
        Industry.SAAS: "Include UI screenshots and feature highlights in your visuals",
        Industry.HEALTHCARE: "Focus on trust-building elements and professional imagery"
    }
    
    if brand.industry in industry_tips:
        recommendations.append(industry_tips[brand.industry])
    
    return recommendations[:5]  # Return top 5 recommendations


def _calculate_campaign_duration(campaign: Campaign) -> Dict[str, Any]:
    """Calculate campaign duration and status."""
    
    now = datetime.utcnow()
    
    if campaign.start_date and campaign.end_date:
        total_days = (campaign.end_date - campaign.start_date).days
        
        if now < campaign.start_date:
            status = "not_started"
            days_active = 0
        elif now > campaign.end_date:
            status = "completed"
            days_active = total_days
        else:
            status = "active"
            days_active = (now - campaign.start_date).days
    else:
        total_days = None
        days_active = (now - campaign.created_at).days
        status = "ongoing"
    
    return {
        "total_days": total_days,
        "days_active": days_active,
        "status": status,
        "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
        "end_date": campaign.end_date.isoformat() if campaign.end_date else None
    }


def _calculate_campaign_performance(
    metrics: List[PerformanceMetric],
    campaign: Campaign
) -> Dict[str, Any]:
    """Calculate campaign performance summary."""
    
    summary = _calculate_summary_stats(metrics)
    
    # Compare to targets if available
    if campaign.target_metrics:
        target_achievement = {}
        for target_key, target_value in campaign.target_metrics.items():
            actual = summary.get(f"total_{target_key}s", 0)
            achievement = (actual / target_value * 100) if target_value > 0 else 0
            target_achievement[target_key] = {
                "target": target_value,
                "actual": actual,
                "achievement_rate": round(achievement, 2)
            }
        summary["target_achievement"] = target_achievement
    
    return summary


def _get_campaign_content_performance(
    db: Session,
    campaign_id: int
) -> List[Dict[str, Any]]:
    """Get performance of individual content pieces in a campaign."""
    
    # Get all images in campaign
    images = db.query(GeneratedImage).filter_by(campaign_id=campaign_id).all()
    
    content_data = []
    
    for image in images:
        metrics = db.query(PerformanceMetric).filter_by(
            generated_image_id=image.id
        ).all()
        
        if metrics:
            metric_summary = _calculate_summary_stats(metrics)
            content_data.append({
                "image_id": image.id,
                "image_url": image.s3_url,
                "created_at": image.created_at.isoformat(),
                "metrics": metric_summary
            })
    
    return content_data


def _calculate_roi(campaign: Campaign, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
    """Calculate ROI for a campaign."""
    
    # Get total conversions
    total_conversions = sum(m.metric_value for m in metrics if m.metric_type == "conversion")
    
    # Calculate costs (images generated * average cost)
    total_images = campaign.total_assets_generated
    avg_cost_per_image = 0.20  # Default cost, should come from pricing
    total_cost = total_images * avg_cost_per_image
    
    # Estimate revenue (would need actual revenue data)
    estimated_revenue_per_conversion = 50  # Placeholder
    total_revenue = total_conversions * estimated_revenue_per_conversion
    
    roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
    
    return {
        "total_cost": round(total_cost, 2),
        "total_conversions": int(total_conversions),
        "estimated_revenue": round(total_revenue, 2),
        "roi_percentage": round(roi, 2),
        "cost_per_conversion": round(total_cost / max(total_conversions, 1), 2)
    }


def _has_ab_tests(metrics: List[PerformanceMetric]) -> bool:
    """Check if metrics contain A/B test data."""
    variants = set(m.variant_id for m in metrics if m.variant_id)
    return len(variants) > 1


def _analyze_ab_tests(metrics: List[PerformanceMetric]) -> Dict[str, Any]:
    """Analyze A/B test results."""
    
    # Group by variant
    variant_data = {}
    
    for metric in metrics:
        variant = metric.variant_id or "control" if metric.is_control else "default"
        
        if variant not in variant_data:
            variant_data[variant] = []
        
        variant_data[variant].append(metric)
    
    # Calculate performance for each variant
    results = {}
    
    for variant, variant_metrics in variant_data.items():
        summary = _calculate_summary_stats(variant_metrics)
        results[variant] = summary
    
    # Determine winner
    if len(results) > 1:
        winner = max(
            results.items(),
            key=lambda x: x[1].get("avg_conversion_rate", 0)
        )[0]
        
        control_rate = results.get("control", {}).get("avg_conversion_rate", 0)
        winner_rate = results[winner].get("avg_conversion_rate", 0)
        
        improvement = ((winner_rate - control_rate) / control_rate * 100) if control_rate > 0 else 0
        
        return {
            "variants": results,
            "winner": winner,
            "improvement_percentage": round(improvement, 2),
            "confidence": "high" if len(metrics) > 100 else "low"  # Simplified
        }
    
    return {"message": "Not enough data for A/B test analysis"}


def _aggregate_metrics_by_type(
    metrics: List[PerformanceMetric],
    metric_types: List[str]
) -> Dict[str, float]:
    """Aggregate metrics by type."""
    
    aggregated = {}
    
    for metric_type in metric_types:
        total = sum(m.metric_value for m in metrics if m.metric_type == metric_type)
        aggregated[metric_type] = total
    
    return aggregated


def _identify_best_performer(
    comparison_data: List[Dict[str, Any]],
    primary_metric: str
) -> Dict[str, Any]:
    """Identify the best performer based on primary metric."""
    
    if not comparison_data:
        return {}
    
    best = max(
        comparison_data,
        key=lambda x: x["metrics"].get(primary_metric, 0)
    )
    
    return {
        "entity_id": best["entity_id"],
        "entity_name": best["entity_name"],
        "metric_value": best["metrics"].get(primary_metric, 0)
    }