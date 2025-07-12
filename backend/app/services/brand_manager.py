import os
import uuid
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import boto3
from sqlalchemy.orm import Session
from fastapi import UploadFile
import json

from ..models import (
    BrandProfile, 
    BrandAsset, 
    BrandGuideline,
    Campaign,
    Industry,
    User
)
from ..core.config import get_settings
from .brand_asset_analyzer import BrandAssetAnalyzer

logger = logging.getLogger(__name__)


class BrandManager:
    """Service for managing brand profiles, assets, and guidelines."""
    
    def __init__(self):
        settings = get_settings()
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.asset_analyzer = BrandAssetAnalyzer(self.s3_client)
        self.bucket_name = settings.s3_bucket
    
    async def create_brand_profile(
        self,
        db: Session,
        user_id: str,
        name: str,
        description: Optional[str],
        industry: Industry,
        brand_data: Dict[str, Any]
    ) -> BrandProfile:
        """Create a new brand profile."""
        brand_profile = BrandProfile(
            user_id=user_id,
            name=name,
            description=description,
            industry=industry,
            brand_values=brand_data.get('brand_values', []),
            target_audience=brand_data.get('target_audience', {}),
            competitors=brand_data.get('competitors', []),
            unique_selling_points=brand_data.get('unique_selling_points', []),
            primary_colors=brand_data.get('primary_colors', []),
            secondary_colors=brand_data.get('secondary_colors', []),
            font_families=brand_data.get('font_families', {}),
            logo_style=brand_data.get('logo_style'),
            visual_style=brand_data.get('visual_style'),
            preferred_image_styles=brand_data.get('preferred_image_styles', []),
            avoided_elements=brand_data.get('avoided_elements', []),
            brand_keywords=brand_data.get('brand_keywords', [])
        )
        
        db.add(brand_profile)
        db.commit()
        db.refresh(brand_profile)
        
        # Create default guidelines
        await self._create_default_guidelines(db, brand_profile.id)
        
        return brand_profile
    
    async def upload_brand_asset(
        self,
        db: Session,
        brand_profile_id: int,
        file: UploadFile,
        asset_type: str,
        asset_name: str
    ) -> BrandAsset:
        """Upload and analyze a brand asset."""
        try:
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml', 'image/webp']
            if file.content_type not in allowed_types:
                raise ValueError(f"Unsupported file type: {file.content_type}")
            
            # Generate unique key for S3
            file_extension = file.filename.split('.')[-1]
            s3_key = f"brand-assets/{brand_profile_id}/{uuid.uuid4()}.{file_extension}"
            
            # Upload to S3
            file_content = await file.read()
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'brand_profile_id': str(brand_profile_id),
                    'asset_type': asset_type,
                    'asset_name': asset_name
                }
            )
            
            # Generate presigned URL
            asset_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=86400 * 7  # 7 days
            )
            
            # Create asset record
            brand_asset = BrandAsset(
                brand_profile_id=brand_profile_id,
                asset_type=asset_type,
                asset_name=asset_name,
                asset_url=asset_url,
                file_size=len(file_content),
                file_format=file_extension,
                dimensions={}  # Will be updated during analysis
            )
            
            db.add(brand_asset)
            db.commit()
            db.refresh(brand_asset)
            
            # Analyze asset asynchronously
            try:
                analysis_result = self.asset_analyzer.analyze_image(f"s3://{self.bucket_name}/{s3_key}")
                
                # Update asset with analysis results
                brand_asset.dominant_colors = analysis_result.get('dominant_colors', [])
                brand_asset.style_attributes = analysis_result.get('style_attributes', {})
                brand_asset.text_elements = analysis_result.get('text_elements', [])
                brand_asset.composition_data = analysis_result.get('composition_data', {})
                brand_asset.analysis_completed = True
                brand_asset.analysis_data = self._ensure_json_serializable(analysis_result)
                
                # Update dimensions
                if 'composition_data' in analysis_result and 'dimensions' in analysis_result['composition_data']:
                    brand_asset.dimensions = analysis_result['composition_data']['dimensions']
                
                db.commit()
                
                # Update brand profile with extracted colors if it's a logo
                if asset_type == 'logo' and not db.query(BrandProfile).filter_by(
                    id=brand_profile_id
                ).first().primary_colors:
                    await self._update_brand_colors_from_asset(db, brand_profile_id, analysis_result)
                
            except Exception as e:
                logger.error(f"Error analyzing asset: {str(e)}")
                # Continue even if analysis fails
            
            return brand_asset
            
        except Exception as e:
            logger.error(f"Error uploading brand asset: {str(e)}")
            raise
    
    def _ensure_json_serializable(self, obj: Any) -> Any:
        """Ensure all values in object are JSON serializable."""
        if isinstance(obj, dict):
            return {k: self._ensure_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._ensure_json_serializable(item) for item in obj]
        elif isinstance(obj, (bool, int, float, str, type(None))):
            return obj
        elif hasattr(obj, 'item'):  # numpy scalars
            return obj.item()
        else:
            return str(obj)
    
    async def _update_brand_colors_from_asset(
        self,
        db: Session,
        brand_profile_id: int,
        analysis_result: Dict[str, Any]
    ):
        """Update brand colors based on asset analysis."""
        brand_profile = db.query(BrandProfile).filter_by(id=brand_profile_id).first()
        if not brand_profile:
            return
        
        dominant_colors = analysis_result.get('dominant_colors', [])
        if dominant_colors:
            # Take top 3 colors as primary colors
            primary_colors = [color['hex'] for color in dominant_colors[:3]]
            # Next 3 as secondary colors
            secondary_colors = [color['hex'] for color in dominant_colors[3:6]]
            
            brand_profile.primary_colors = primary_colors
            brand_profile.secondary_colors = secondary_colors
            db.commit()
    
    async def _create_default_guidelines(self, db: Session, brand_profile_id: int):
        """Create default brand guidelines."""
        default_guidelines = [
            {
                "guideline_type": "color",
                "rule_name": "Primary Color Usage",
                "rule_description": "Primary colors should be used for main brand elements",
                "rule_data": {"usage_percentage": 60},
                "priority": 8,
                "is_mandatory": True
            },
            {
                "guideline_type": "typography",
                "rule_name": "Font Consistency",
                "rule_description": "Use specified font families for all text elements",
                "rule_data": {"allowed_variations": ["regular", "bold", "italic"]},
                "priority": 7,
                "is_mandatory": True
            },
            {
                "guideline_type": "imagery",
                "rule_name": "Image Style Consistency",
                "rule_description": "All images should match the brand's visual style",
                "rule_data": {"check_style_match": True},
                "priority": 6,
                "is_mandatory": False
            },
            {
                "guideline_type": "layout",
                "rule_name": "Logo Clear Space",
                "rule_description": "Maintain minimum clear space around logo",
                "rule_data": {"min_clear_space": "2x logo height"},
                "priority": 9,
                "is_mandatory": True
            }
        ]
        
        for guideline in default_guidelines:
            brand_guideline = BrandGuideline(
                brand_profile_id=brand_profile_id,
                **guideline
            )
            db.add(brand_guideline)
        
        db.commit()
    
    async def analyze_brand_consistency(
        self,
        db: Session,
        brand_profile_id: int,
        image_url: str
    ) -> Dict[str, Any]:
        """Analyze how well an image matches brand guidelines."""
        # Get brand profile and guidelines
        brand_profile = db.query(BrandProfile).filter_by(id=brand_profile_id).first()
        if not brand_profile:
            raise ValueError("Brand profile not found")
        
        guidelines = db.query(BrandGuideline).filter_by(
            brand_profile_id=brand_profile_id
        ).all()
        
        # Analyze the image
        image_analysis = self.asset_analyzer.analyze_image(image_url)
        
        # Check consistency
        consistency_report = {
            "overall_score": 0,
            "color_consistency": self._check_color_consistency(
                brand_profile, image_analysis
            ),
            "style_consistency": self._check_style_consistency(
                brand_profile, image_analysis
            ),
            "guideline_compliance": self._check_guideline_compliance(
                guidelines, image_analysis
            ),
            "recommendations": []
        }
        
        # Calculate overall score
        scores = [
            consistency_report["color_consistency"]["score"],
            consistency_report["style_consistency"]["score"],
            consistency_report["guideline_compliance"]["score"]
        ]
        consistency_report["overall_score"] = sum(scores) / len(scores)
        
        # Generate recommendations
        if consistency_report["color_consistency"]["score"] < 0.7:
            consistency_report["recommendations"].append(
                "Consider using more brand colors in the image"
            )
        if consistency_report["style_consistency"]["score"] < 0.7:
            consistency_report["recommendations"].append(
                f"Adjust image style to be more {brand_profile.visual_style}"
            )
        
        return consistency_report
    
    def _check_color_consistency(
        self,
        brand_profile: BrandProfile,
        image_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check color consistency with brand palette."""
        brand_colors = (brand_profile.primary_colors or []) + (brand_profile.secondary_colors or [])
        if not brand_colors:
            return {"score": 1.0, "details": "No brand colors defined"}
        
        image_colors = image_analysis.get('dominant_colors', [])
        matches = 0
        total_percentage = 0
        
        for image_color in image_colors:
            for brand_color in brand_colors:
                # Check if colors are similar (simple RGB distance)
                if self._colors_similar(image_color['hex'], brand_color):
                    matches += 1
                    total_percentage += image_color['percentage']
                    break
        
        score = min(total_percentage / 50, 1.0)  # 50% coverage is perfect score
        
        return {
            "score": score,
            "matching_colors": matches,
            "coverage_percentage": total_percentage,
            "details": f"{matches} brand colors found covering {total_percentage:.1f}% of image"
        }
    
    def _colors_similar(self, hex1: str, hex2: str, threshold: int = 30) -> bool:
        """Check if two hex colors are similar."""
        # Convert hex to RGB
        rgb1 = tuple(int(hex1.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        rgb2 = tuple(int(hex2.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate Euclidean distance
        distance = sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5
        
        return distance < threshold
    
    def _check_style_consistency(
        self,
        brand_profile: BrandProfile,
        image_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check style consistency with brand preferences."""
        style_attrs = image_analysis.get('style_attributes', {})
        style_descriptors = style_attrs.get('style_descriptors', [])
        
        score = 1.0
        issues = []
        
        # Check visual style match
        if brand_profile.visual_style:
            style_map = {
                'modern': ['minimalist', 'clean', 'bright'],
                'classic': ['balanced', 'traditional', 'detailed'],
                'bold': ['high-contrast', 'vibrant', 'dramatic'],
                'playful': ['vibrant', 'colorful', 'dynamic'],
                'professional': ['balanced', 'clean', 'structured']
            }
            
            expected_descriptors = style_map.get(brand_profile.visual_style, [])
            matching_descriptors = [d for d in style_descriptors if d in expected_descriptors]
            
            if expected_descriptors:
                match_ratio = len(matching_descriptors) / len(expected_descriptors)
                score *= match_ratio
                
                if match_ratio < 0.5:
                    issues.append(f"Image style doesn't match brand's {brand_profile.visual_style} style")
        
        return {
            "score": score,
            "detected_style": style_descriptors,
            "expected_style": brand_profile.visual_style,
            "issues": issues
        }
    
    def _check_guideline_compliance(
        self,
        guidelines: List[BrandGuideline],
        image_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check compliance with brand guidelines."""
        if not guidelines:
            return {"score": 1.0, "details": "No guidelines defined"}
        
        total_score = 0
        checked_guidelines = 0
        violations = []
        
        for guideline in guidelines:
            if guideline.is_mandatory:
                # Simple compliance check based on guideline type
                compliance = 1.0
                
                if guideline.guideline_type == "color" and guideline.rule_data:
                    # Check color usage percentage
                    required_percentage = guideline.rule_data.get('usage_percentage', 50)
                    # This is simplified - in production, would check actual usage
                    compliance = 0.8
                
                elif guideline.guideline_type == "layout" and "composition_data" in image_analysis:
                    # Check layout rules
                    composition = image_analysis['composition_data']
                    if guideline.rule_name == "Logo Clear Space":
                        # Check if logo has clear space (simplified)
                        compliance = 0.9 if composition.get('whitespace_ratio', 0) > 0.1 else 0.5
                
                total_score += compliance * guideline.priority
                checked_guidelines += guideline.priority
                
                if compliance < 0.8:
                    violations.append({
                        "guideline": guideline.rule_name,
                        "compliance": compliance,
                        "severity": "high" if guideline.is_mandatory else "medium"
                    })
        
        final_score = total_score / checked_guidelines if checked_guidelines > 0 else 1.0
        
        return {
            "score": final_score,
            "checked_guidelines": len(guidelines),
            "violations": violations,
            "details": f"{len(violations)} guideline violations found"
        }
    
    async def create_campaign(
        self,
        db: Session,
        brand_profile_id: int,
        user_id: int,
        campaign_data: Dict[str, Any]
    ) -> Campaign:
        """Create a new marketing campaign."""
        campaign = Campaign(
            brand_profile_id=brand_profile_id,
            user_id=user_id,
            name=campaign_data['name'],
            description=campaign_data.get('description'),
            campaign_type=campaign_data.get('campaign_type', 'general'),
            start_date=campaign_data.get('start_date'),
            end_date=campaign_data.get('end_date'),
            target_platforms=campaign_data.get('target_platforms', []),
            target_metrics=campaign_data.get('target_metrics', {}),
            status='draft'
        )
        
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        return campaign
    
    async def get_brand_insights(
        self,
        db: Session,
        brand_profile_id: int
    ) -> Dict[str, Any]:
        """Get insights and analytics for a brand profile."""
        brand_profile = db.query(BrandProfile).filter_by(id=brand_profile_id).first()
        if not brand_profile:
            raise ValueError("Brand profile not found")
        
        # Get brand assets
        assets = db.query(BrandAsset).filter_by(brand_profile_id=brand_profile_id).all()
        
        # Aggregate color data
        all_colors = []
        for asset in assets:
            if asset.dominant_colors:
                all_colors.extend(asset.dominant_colors)
        
        # Get most common colors
        color_frequency = {}
        for color in all_colors:
            hex_color = color['hex']
            if hex_color not in color_frequency:
                color_frequency[hex_color] = 0
            color_frequency[hex_color] += color['percentage']
        
        # Sort by frequency
        top_colors = sorted(
            color_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Style analysis
        style_descriptors = []
        for asset in assets:
            if asset.style_attributes and 'style_descriptors' in asset.style_attributes:
                style_descriptors.extend(asset.style_attributes['style_descriptors'])
        
        # Count style descriptors
        style_counts = {}
        for descriptor in style_descriptors:
            style_counts[descriptor] = style_counts.get(descriptor, 0) + 1
        
        insights = {
            "brand_profile": {
                "name": brand_profile.name,
                "industry": brand_profile.industry.value,
                "total_assets": len(assets),
                "total_generations": brand_profile.total_generations
            },
            "color_insights": {
                "defined_primary_colors": brand_profile.primary_colors or [],
                "defined_secondary_colors": brand_profile.secondary_colors or [],
                "detected_top_colors": [{"hex": c[0], "frequency": c[1]} for c in top_colors],
                "color_consistency_score": self._calculate_color_consistency_score(
                    brand_profile, top_colors
                )
            },
            "style_insights": {
                "defined_style": brand_profile.visual_style,
                "detected_styles": dict(sorted(
                    style_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]),
                "style_consistency": self._calculate_style_consistency_score(
                    brand_profile, style_counts
                )
            },
            "asset_insights": {
                "total_assets": len(assets),
                "asset_types": self._count_asset_types(assets),
                "analyzed_assets": sum(1 for a in assets if a.analysis_completed),
                "average_asset_size": sum(a.file_size or 0 for a in assets) / len(assets) if assets else 0
            },
            "recommendations": self._generate_brand_recommendations(
                brand_profile, assets, top_colors, style_counts
            )
        }
        
        return insights
    
    def _calculate_color_consistency_score(
        self,
        brand_profile: BrandProfile,
        top_colors: List[Tuple[str, float]]
    ) -> float:
        """Calculate how consistent detected colors are with brand colors."""
        brand_colors = (brand_profile.primary_colors or []) + (brand_profile.secondary_colors or [])
        if not brand_colors or not top_colors:
            return 0.0
        
        # Check how many of top detected colors match brand colors
        matches = 0
        for detected_color, _ in top_colors[:5]:
            for brand_color in brand_colors:
                if self._colors_similar(detected_color, brand_color):
                    matches += 1
                    break
        
        return matches / min(5, len(brand_colors))
    
    def _calculate_style_consistency_score(
        self,
        brand_profile: BrandProfile,
        style_counts: Dict[str, int]
    ) -> float:
        """Calculate style consistency score."""
        if not brand_profile.visual_style or not style_counts:
            return 0.0
        
        # Map brand styles to expected descriptors
        style_expectations = {
            'modern': ['minimalist', 'clean', 'bright', 'simple'],
            'classic': ['balanced', 'traditional', 'detailed', 'elegant'],
            'bold': ['high-contrast', 'vibrant', 'dramatic', 'strong'],
            'playful': ['vibrant', 'colorful', 'dynamic', 'fun'],
            'professional': ['balanced', 'clean', 'structured', 'formal']
        }
        
        expected = style_expectations.get(brand_profile.visual_style, [])
        if not expected:
            return 0.5
        
        # Calculate what percentage of detected styles match expectations
        total_count = sum(style_counts.values())
        matching_count = sum(
            style_counts.get(descriptor, 0)
            for descriptor in expected
        )
        
        return matching_count / total_count if total_count > 0 else 0.0
    
    def _count_asset_types(self, assets: List[BrandAsset]) -> Dict[str, int]:
        """Count assets by type."""
        type_counts = {}
        for asset in assets:
            type_counts[asset.asset_type] = type_counts.get(asset.asset_type, 0) + 1
        return type_counts
    
    def _generate_brand_recommendations(
        self,
        brand_profile: BrandProfile,
        assets: List[BrandAsset],
        top_colors: List[Tuple[str, float]],
        style_counts: Dict[str, int]
    ) -> List[str]:
        """Generate recommendations for brand improvement."""
        recommendations = []
        
        # Color recommendations
        if not brand_profile.primary_colors:
            recommendations.append(
                "Define primary brand colors based on your logo and existing assets"
            )
        elif top_colors and brand_profile.primary_colors:
            color_score = self._calculate_color_consistency_score(brand_profile, top_colors)
            if color_score < 0.5:
                recommendations.append(
                    "Your assets are using colors that don't match your brand palette. "
                    "Consider updating assets or refining your color palette."
                )
        
        # Style recommendations
        if not brand_profile.visual_style:
            recommendations.append(
                "Define your brand's visual style to ensure consistency"
            )
        elif style_counts:
            style_score = self._calculate_style_consistency_score(brand_profile, style_counts)
            if style_score < 0.3:
                recommendations.append(
                    f"Your assets don't consistently reflect your {brand_profile.visual_style} style. "
                    "Consider creating style guidelines for content creators."
                )
        
        # Asset recommendations
        if len(assets) < 5:
            recommendations.append(
                "Upload more brand assets to get better insights and consistency analysis"
            )
        
        asset_types = self._count_asset_types(assets)
        if 'logo' not in asset_types:
            recommendations.append(
                "Upload your brand logo to automatically extract brand colors"
            )
        
        # Industry-specific recommendations
        industry_recommendations = {
            Industry.ECOMMERCE: "Consider adding product photography guidelines",
            Industry.SAAS: "Define UI/UX consistency rules for software screenshots",
            Industry.HEALTHCARE: "Ensure imagery conveys trust and professionalism",
            Industry.FINANCE: "Maintain conservative, professional visual standards"
        }
        
        if brand_profile.industry in industry_recommendations:
            recommendations.append(industry_recommendations[brand_profile.industry])
        
        return recommendations[:5]  # Return top 5 recommendations