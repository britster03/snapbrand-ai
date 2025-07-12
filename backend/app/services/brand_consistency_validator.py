import logging
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
import json

from ..models import BrandProfile, BrandGuideline, GeneratedImage
from .brand_asset_analyzer import BrandAssetAnalyzer
from .prompt_engineering import PromptEngineeringService

logger = logging.getLogger(__name__)


class BrandConsistencyValidator:
    """Service for validating and enforcing brand consistency in generated images."""
    
    def __init__(self):
        self.prompt_engineer = PromptEngineeringService()
    
    def enhance_prompt_with_brand(
        self,
        original_prompt: str,
        brand_profile: BrandProfile,
        style_override: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Enhance a prompt with brand-specific guidelines and style."""
        
        # Build brand context
        brand_context = self._build_brand_context(brand_profile)
        
        # Merge brand style with any overrides
        brand_style = self._extract_brand_style(brand_profile)
        if style_override:
            brand_style.update(style_override)
        
        # Build enhanced prompt
        enhanced_prompt_parts = []
        
        # Add brand keywords if relevant
        if brand_profile.brand_keywords:
            keywords_context = f"Brand essence: {', '.join(brand_profile.brand_keywords[:5])}"
            enhanced_prompt_parts.append(keywords_context)
        
        # Add original prompt
        enhanced_prompt_parts.append(original_prompt)
        
        # Add brand style descriptors
        if brand_profile.visual_style:
            style_descriptor = self._get_style_descriptor(brand_profile.visual_style)
            enhanced_prompt_parts.append(style_descriptor)
        
        # Add color guidance
        if brand_profile.primary_colors:
            color_guidance = self._build_color_guidance(brand_profile)
            enhanced_prompt_parts.append(color_guidance)
        
        # Add industry-specific enhancements
        industry_enhancement = self._get_industry_enhancement(brand_profile.industry)
        if industry_enhancement:
            enhanced_prompt_parts.append(industry_enhancement)
        
        # Add negative prompt elements
        negative_elements = []
        if brand_profile.avoided_elements:
            negative_elements.extend(brand_profile.avoided_elements)
        
        # Industry-specific negative prompts
        industry_negatives = self._get_industry_negatives(brand_profile.industry)
        negative_elements.extend(industry_negatives)
        
        enhanced_prompt = ", ".join(enhanced_prompt_parts)
        
        # Build metadata
        brand_metadata = {
            "brand_profile_id": brand_profile.id,
            "brand_name": brand_profile.name,
            "industry": brand_profile.industry.value,
            "visual_style": brand_profile.visual_style,
            "primary_colors": brand_profile.primary_colors,
            "brand_keywords": brand_profile.brand_keywords,
            "style_enhancements": brand_style,
            "negative_elements": negative_elements
        }
        
        return enhanced_prompt, brand_metadata
    
    def _build_brand_context(self, brand_profile: BrandProfile) -> Dict[str, Any]:
        """Build comprehensive brand context for prompt enhancement."""
        return {
            "name": brand_profile.name,
            "industry": brand_profile.industry.value,
            "values": brand_profile.brand_values or [],
            "target_audience": brand_profile.target_audience or {},
            "unique_selling_points": brand_profile.unique_selling_points or [],
            "visual_style": brand_profile.visual_style,
            "preferred_styles": brand_profile.preferred_image_styles or []
        }
    
    def _extract_brand_style(self, brand_profile: BrandProfile) -> Dict[str, Any]:
        """Extract style parameters from brand profile."""
        style = {}
        
        # Map visual style to concrete parameters
        style_mappings = {
            "modern": {
                "composition": "minimalist, clean lines, negative space",
                "lighting": "bright, even lighting",
                "mood": "contemporary, sleek"
            },
            "classic": {
                "composition": "balanced, traditional layout",
                "lighting": "soft, natural lighting",
                "mood": "timeless, elegant"
            },
            "bold": {
                "composition": "dynamic angles, strong contrast",
                "lighting": "dramatic lighting, high contrast",
                "mood": "powerful, impactful"
            },
            "playful": {
                "composition": "asymmetric, creative layout",
                "lighting": "vibrant, colorful lighting",
                "mood": "fun, energetic"
            },
            "professional": {
                "composition": "structured, organized layout",
                "lighting": "neutral, professional lighting",
                "mood": "trustworthy, competent"
            },
            "minimal": {
                "composition": "ultra-minimal, essential elements only",
                "lighting": "soft, diffused lighting",
                "mood": "simple, focused"
            },
            "luxury": {
                "composition": "premium feel, sophisticated layout",
                "lighting": "elegant, refined lighting",
                "mood": "exclusive, high-end"
            }
        }
        
        if brand_profile.visual_style and brand_profile.visual_style in style_mappings:
            style.update(style_mappings[brand_profile.visual_style])
        
        # Add preferred image styles
        if brand_profile.preferred_image_styles:
            style["preferred_styles"] = brand_profile.preferred_image_styles
        
        return style
    
    def _get_style_descriptor(self, visual_style: str) -> str:
        """Get descriptive text for a visual style."""
        descriptors = {
            "modern": "modern, clean, minimalist aesthetic",
            "classic": "classic, timeless, traditional style",
            "bold": "bold, dynamic, high-impact visual",
            "playful": "playful, creative, vibrant style",
            "professional": "professional, corporate, polished look",
            "minimal": "minimal, simple, uncluttered design",
            "luxury": "luxury, premium, sophisticated appearance"
        }
        
        return descriptors.get(visual_style, f"{visual_style} style")
    
    def _build_color_guidance(self, brand_profile: BrandProfile) -> str:
        """Build color guidance for the prompt."""
        if not brand_profile.primary_colors:
            return ""
        
        # Convert hex to descriptive names
        color_descriptions = []
        for hex_color in brand_profile.primary_colors[:3]:
            color_name = self._hex_to_descriptive_name(hex_color)
            if color_name:
                color_descriptions.append(color_name)
        
        if color_descriptions:
            return f"using {', '.join(color_descriptions)} color palette"
        
        return ""
    
    def _hex_to_descriptive_name(self, hex_color: str) -> str:
        """Convert hex color to descriptive name."""
        # Simple color mapping - in production, use a more comprehensive library
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Determine dominant channel
            if r > g and r > b:
                if r > 200:
                    return "bright red"
                elif r > 150:
                    return "red"
                else:
                    return "dark red"
            elif g > r and g > b:
                if g > 200:
                    return "bright green"
                elif g > 150:
                    return "green"
                else:
                    return "dark green"
            elif b > r and b > g:
                if b > 200:
                    return "bright blue"
                elif b > 150:
                    return "blue"
                else:
                    return "dark blue"
            elif r > 200 and g > 200 and b < 100:
                return "yellow"
            elif r > 200 and g < 100 and b > 200:
                return "purple"
            elif r > 200 and g > 100 and b < 100:
                return "orange"
            elif r < 50 and g < 50 and b < 50:
                return "black"
            elif r > 200 and g > 200 and b > 200:
                return "white"
            else:
                return "neutral"
                
        except Exception:
            return ""
    
    def _get_industry_enhancement(self, industry) -> Optional[str]:
        """Get industry-specific prompt enhancements."""
        from ..models.brand import Industry
        
        enhancements = {
            Industry.ECOMMERCE: "product-focused, commercial photography style, clean background",
            Industry.SAAS: "modern tech aesthetic, professional interface, clean UI elements",
            Industry.HEALTHCARE: "medical professionalism, trust-inspiring, clean and sterile",
            Industry.FINANCE: "corporate professional, trustworthy, established institution feel",
            Industry.EDUCATION: "educational, informative, accessible and friendly",
            Industry.REALESTATE: "architectural photography, inviting spaces, professional property showcase",
            Industry.RETAIL: "retail display, attractive merchandising, shopping appeal",
            Industry.HOSPITALITY: "welcoming atmosphere, comfort and luxury, guest experience",
            Industry.TECHNOLOGY: "cutting-edge tech, innovation, futuristic elements",
            Industry.FASHION: "fashion photography, stylish, trend-conscious, editorial quality",
            Industry.FOOD: "appetizing food photography, fresh ingredients, culinary appeal",
            Industry.AUTOMOTIVE: "automotive photography, sleek design, performance oriented"
        }
        
        return enhancements.get(industry)
    
    def _get_industry_negatives(self, industry) -> List[str]:
        """Get industry-specific negative prompt elements."""
        from ..models.brand import Industry
        
        negatives = {
            Industry.HEALTHCARE: ["unprofessional", "unsanitary", "chaotic", "disturbing imagery"],
            Industry.FINANCE: ["casual", "unprofessional", "risky", "unstable"],
            Industry.EDUCATION: ["confusing", "inaccessible", "overwhelming", "childish"],
            Industry.FOOD: ["unappetizing", "stale", "messy", "unsanitary"],
            Industry.TECHNOLOGY: ["outdated", "obsolete", "low-tech", "analog"],
            Industry.FASHION: ["unfashionable", "dated", "poor quality", "unstylish"],
            Industry.AUTOMOTIVE: ["damaged", "rusty", "old", "unsafe"]
        }
        
        return negatives.get(industry, [])
    
    def validate_generated_image(
        self,
        db: Session,
        brand_profile_id: int,
        image_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a generated image against brand guidelines."""
        
        brand_profile = db.query(BrandProfile).filter_by(id=brand_profile_id).first()
        if not brand_profile:
            return {
                "valid": True,
                "score": 1.0,
                "issues": [],
                "warnings": []
            }
        
        guidelines = db.query(BrandGuideline).filter_by(
            brand_profile_id=brand_profile_id
        ).order_by(BrandGuideline.priority.desc()).all()
        
        validation_result = {
            "valid": True,
            "score": 1.0,
            "issues": [],
            "warnings": [],
            "passed_checks": []
        }
        
        total_weight = 0
        weighted_score = 0
        
        for guideline in guidelines:
            check_result = self._check_guideline(guideline, image_analysis, brand_profile)
            
            weight = guideline.priority
            total_weight += weight
            weighted_score += check_result["score"] * weight
            
            if check_result["passed"]:
                validation_result["passed_checks"].append({
                    "guideline": guideline.rule_name,
                    "type": guideline.guideline_type
                })
            else:
                if guideline.is_mandatory:
                    validation_result["valid"] = False
                    validation_result["issues"].append({
                        "guideline": guideline.rule_name,
                        "type": guideline.guideline_type,
                        "description": check_result["message"],
                        "severity": "error"
                    })
                else:
                    validation_result["warnings"].append({
                        "guideline": guideline.rule_name,
                        "type": guideline.guideline_type,
                        "description": check_result["message"],
                        "severity": "warning"
                    })
        
        # Calculate final score
        if total_weight > 0:
            validation_result["score"] = weighted_score / total_weight
        
        # Add recommendations
        validation_result["recommendations"] = self._generate_recommendations(
            validation_result, brand_profile
        )
        
        return validation_result
    
    def _check_guideline(
        self,
        guideline: BrandGuideline,
        image_analysis: Dict[str, Any],
        brand_profile: BrandProfile
    ) -> Dict[str, Any]:
        """Check a specific guideline against image analysis."""
        
        if guideline.guideline_type == "color":
            return self._check_color_guideline(guideline, image_analysis, brand_profile)
        elif guideline.guideline_type == "typography":
            return self._check_typography_guideline(guideline, image_analysis)
        elif guideline.guideline_type == "imagery":
            return self._check_imagery_guideline(guideline, image_analysis, brand_profile)
        elif guideline.guideline_type == "layout":
            return self._check_layout_guideline(guideline, image_analysis)
        elif guideline.guideline_type == "tone":
            return self._check_tone_guideline(guideline, image_analysis, brand_profile)
        else:
            # Unknown guideline type, pass by default
            return {
                "passed": True,
                "score": 1.0,
                "message": "Guideline type not implemented"
            }
    
    def _check_color_guideline(
        self,
        guideline: BrandGuideline,
        image_analysis: Dict[str, Any],
        brand_profile: BrandProfile
    ) -> Dict[str, Any]:
        """Check color-related guidelines."""
        
        if not brand_profile.primary_colors:
            return {
                "passed": True,
                "score": 1.0,
                "message": "No brand colors defined"
            }
        
        dominant_colors = image_analysis.get("dominant_colors", [])
        if not dominant_colors:
            return {
                "passed": False,
                "score": 0.0,
                "message": "Could not analyze image colors"
            }
        
        # Check if brand colors are present
        brand_colors_found = 0
        total_coverage = 0
        
        for image_color in dominant_colors[:5]:  # Check top 5 colors
            for brand_color in brand_profile.primary_colors:
                if self._colors_similar(image_color["hex"], brand_color, threshold=40):
                    brand_colors_found += 1
                    total_coverage += image_color["percentage"]
                    break
        
        # Check against guideline requirements
        if guideline.rule_data:
            required_percentage = guideline.rule_data.get("usage_percentage", 50)
            if total_coverage < required_percentage:
                return {
                    "passed": False,
                    "score": total_coverage / required_percentage,
                    "message": f"Brand colors cover only {total_coverage:.1f}% of image (required: {required_percentage}%)"
                }
        
        if brand_colors_found == 0:
            return {
                "passed": False,
                "score": 0.0,
                "message": "No brand colors found in image"
            }
        
        score = min(total_coverage / 50, 1.0)  # 50% coverage is perfect
        return {
            "passed": score >= 0.7,
            "score": score,
            "message": f"Found {brand_colors_found} brand colors covering {total_coverage:.1f}% of image"
        }
    
    def _check_typography_guideline(
        self,
        guideline: BrandGuideline,
        image_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check typography-related guidelines."""
        
        text_elements = image_analysis.get("text_elements", [])
        
        if guideline.rule_name == "Font Consistency" and not text_elements:
            # No text in image, so font consistency is not applicable
            return {
                "passed": True,
                "score": 1.0,
                "message": "No text elements to check"
            }
        
        # For now, we can't determine actual fonts from image analysis
        # This would require OCR with font detection
        return {
            "passed": True,
            "score": 0.8,
            "message": "Typography check requires manual verification"
        }
    
    def _check_imagery_guideline(
        self,
        guideline: BrandGuideline,
        image_analysis: Dict[str, Any],
        brand_profile: BrandProfile
    ) -> Dict[str, Any]:
        """Check imagery style guidelines."""
        
        style_attrs = image_analysis.get("style_attributes", {})
        style_descriptors = style_attrs.get("style_descriptors", [])
        
        if not brand_profile.visual_style:
            return {
                "passed": True,
                "score": 1.0,
                "message": "No brand style defined"
            }
        
        # Check if image style matches brand style
        expected_descriptors = self._get_expected_descriptors(brand_profile.visual_style)
        matching_descriptors = [d for d in style_descriptors if d in expected_descriptors]
        
        if not matching_descriptors:
            return {
                "passed": False,
                "score": 0.3,
                "message": f"Image style doesn't match brand's {brand_profile.visual_style} style"
            }
        
        score = len(matching_descriptors) / len(expected_descriptors) if expected_descriptors else 1.0
        return {
            "passed": score >= 0.5,
            "score": score,
            "message": f"Image style {('matches' if score >= 0.5 else 'partially matches')} brand guidelines"
        }
    
    def _check_layout_guideline(
        self,
        guideline: BrandGuideline,
        image_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check layout-related guidelines."""
        
        composition = image_analysis.get("composition_data", {})
        
        if guideline.rule_name == "Logo Clear Space":
            # Check whitespace around potential logo areas
            whitespace_ratio = composition.get("whitespace_ratio", 0)
            
            if whitespace_ratio < 0.1:
                return {
                    "passed": False,
                    "score": whitespace_ratio * 10,
                    "message": "Insufficient clear space in image composition"
                }
        
        elif guideline.rule_name == "Rule of Thirds":
            rule_of_thirds = composition.get("rule_of_thirds", {})
            alignment_score = rule_of_thirds.get("alignment_score", 0)
            
            return {
                "passed": alignment_score >= 0.6,
                "score": alignment_score,
                "message": f"Composition alignment score: {alignment_score:.2f}"
            }
        
        return {
            "passed": True,
            "score": 0.8,
            "message": "Layout guidelines met"
        }
    
    def _check_tone_guideline(
        self,
        guideline: BrandGuideline,
        image_analysis: Dict[str, Any],
        brand_profile: BrandProfile
    ) -> Dict[str, Any]:
        """Check tone and mood guidelines."""
        
        style_attrs = image_analysis.get("style_attributes", {})
        
        # Map brand values to expected image characteristics
        if "professional" in brand_profile.brand_values:
            if style_attrs.get("brightness", 0) < 100:
                return {
                    "passed": False,
                    "score": 0.5,
                    "message": "Image too dark for professional brand tone"
                }
        
        if "innovative" in brand_profile.brand_values:
            complexity = style_attrs.get("complexity", 0)
            if complexity < 0.3:
                return {
                    "passed": False,
                    "score": complexity * 3,
                    "message": "Image lacks visual innovation expected by brand"
                }
        
        return {
            "passed": True,
            "score": 0.9,
            "message": "Tone aligns with brand values"
        }
    
    def _get_expected_descriptors(self, visual_style: str) -> List[str]:
        """Get expected style descriptors for a visual style."""
        style_map = {
            'modern': ['minimalist', 'clean', 'bright', 'balanced'],
            'classic': ['balanced', 'traditional', 'detailed'],
            'bold': ['high-contrast', 'vibrant', 'dramatic'],
            'playful': ['vibrant', 'colorful', 'dynamic'],
            'professional': ['balanced', 'clean', 'structured'],
            'minimal': ['minimalist', 'simple', 'clean'],
            'luxury': ['elegant', 'sophisticated', 'refined']
        }
        
        return style_map.get(visual_style, [])
    
    def _colors_similar(self, hex1: str, hex2: str, threshold: int = 30) -> bool:
        """Check if two hex colors are similar."""
        try:
            # Convert hex to RGB
            rgb1 = tuple(int(hex1.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            rgb2 = tuple(int(hex2.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            
            # Calculate Euclidean distance
            distance = sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5
            
            return distance < threshold
        except Exception:
            return False
    
    def _generate_recommendations(
        self,
        validation_result: Dict[str, Any],
        brand_profile: BrandProfile
    ) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Color recommendations
        color_issues = [i for i in validation_result["issues"] if i["type"] == "color"]
        if color_issues:
            recommendations.append(
                f"Use more of your brand colors: {', '.join(brand_profile.primary_colors[:3])}"
            )
        
        # Style recommendations
        style_issues = [i for i in validation_result["issues"] if i["type"] == "imagery"]
        if style_issues and brand_profile.visual_style:
            recommendations.append(
                f"Adjust the image to better match your {brand_profile.visual_style} brand style"
            )
        
        # Layout recommendations
        layout_warnings = [w for w in validation_result["warnings"] if w["type"] == "layout"]
        if layout_warnings:
            recommendations.append(
                "Consider improving composition using rule of thirds or better visual balance"
            )
        
        # Score-based recommendations
        if validation_result["score"] < 0.5:
            recommendations.append(
                "This image significantly deviates from brand guidelines. Consider regenerating with stronger brand constraints."
            )
        elif validation_result["score"] < 0.7:
            recommendations.append(
                "Minor adjustments needed to fully align with brand guidelines."
            )
        
        return recommendations[:3]  # Return top 3 recommendations