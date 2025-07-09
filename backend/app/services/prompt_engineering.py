"""
Professional prompt engineering service for high-quality image generation.
Implements industry-standard guidelines and best practices.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import re

class ImageQuality(Enum):
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"
    PROFESSIONAL = "professional"

class ImageStyle(Enum):
    PHOTOREALISTIC = "photorealistic"
    ARTISTIC = "artistic" 
    TECHNICAL = "technical"
    MARKETING = "marketing"
    PRODUCT = "product"

class CompositionRule(Enum):
    RULE_OF_THIRDS = "rule_of_thirds"
    CENTER_COMPOSITION = "center_composition"
    LEADING_LINES = "leading_lines"
    SYMMETRY = "symmetry"
    GOLDEN_RATIO = "golden_ratio"

class PromptEngineeringService:
    """Professional prompt engineering service with industry standards."""
    
    def __init__(self):
        self.quality_modifiers = {
            ImageQuality.STANDARD: ["good quality", "clear"],
            ImageQuality.HIGH: ["high quality", "detailed", "sharp", "professional"],
            ImageQuality.ULTRA: ["ultra high quality", "8K resolution", "highly detailed", "masterpiece", "professional photography"],
            ImageQuality.PROFESSIONAL: ["professional grade", "commercial quality", "studio lighting", "perfect composition", "award winning", "ultra realistic"]
        }
        
        self.style_modifiers = {
            ImageStyle.PHOTOREALISTIC: ["photorealistic", "realistic", "natural lighting", "authentic"],
            ImageStyle.ARTISTIC: ["artistic", "creative", "stylized", "expressive"],
            ImageStyle.TECHNICAL: ["technical illustration", "precise", "clean", "documentation style"],
            ImageStyle.MARKETING: ["marketing photography", "commercial", "appealing", "brand focused"],
            ImageStyle.PRODUCT: ["product photography", "commercial grade", "studio lighting", "clean background"]
        }
        
        self.composition_rules = {
            CompositionRule.RULE_OF_THIRDS: "following rule of thirds composition",
            CompositionRule.CENTER_COMPOSITION: "centered composition",
            CompositionRule.LEADING_LINES: "with leading lines composition",
            CompositionRule.SYMMETRY: "symmetrical composition",
            CompositionRule.GOLDEN_RATIO: "golden ratio composition"
        }
        
        self.lighting_presets = {
            "studio": "professional studio lighting, soft shadows, even illumination",
            "natural": "natural lighting, soft daylight, realistic shadows",
            "dramatic": "dramatic lighting, strong contrast, cinematic",
            "soft": "soft diffused lighting, minimal shadows",
            "golden_hour": "golden hour lighting, warm tones, natural glow",
            "professional": "professional photography lighting, three-point lighting setup"
        }
        
        self.negative_prompt_standards = [
            "blurry", "low quality", "pixelated", "distorted", "amateur",
            "poor lighting", "overexposed", "underexposed", "noisy", "grainy",
            "watermark", "text overlay", "signature", "logo", "copyright",
            "deformed", "disfigured", "bad anatomy", "wrong proportions",
            "duplicate", "cropped", "out of frame", "mutation", "mutated"
        ]

    def enhance_prompt(
        self,
        base_prompt: str,
        quality: ImageQuality = ImageQuality.HIGH,
        style: ImageStyle = ImageStyle.PHOTOREALISTIC,
        composition: Optional[CompositionRule] = None,
        lighting: str = "professional",
        brand_style: Optional[Dict[str, Any]] = None,
        template_context: Optional[str] = None
    ) -> str:
        """
        Minimally enhance a base prompt while preserving user intent.
        
        Args:
            base_prompt: The original prompt (preserved as-is)
            template_context: Template-specific context
            brand_style: Brand style parameters
            
        Returns:
            Lightly enhanced prompt preserving user intent
        """
        
        # Keep user's original prompt as the primary content
        enhanced_prompt = base_prompt.strip()
        
        # Only add minimal, contextual improvements
        if template_context and "email" in template_context.lower():
            enhanced_prompt += ", abstract graphic design"
        elif template_context and "social" in template_context.lower():
            enhanced_prompt += ", clean modern design"
        elif template_context and "website" in template_context.lower():
            enhanced_prompt += ", professional web design"
        else:
            enhanced_prompt += ", high quality"
        
        # Add brand style integration (minimal)
        if brand_style and brand_style.get("keywords"):
            # Only add the first brand keyword to avoid over-enhancement
            first_keyword = brand_style["keywords"][0]
            enhanced_prompt += f", {first_keyword}"
        
        return enhanced_prompt

    def generate_negative_prompt(
        self,
        base_negative: Optional[str] = None,
        style: ImageStyle = ImageStyle.PHOTOREALISTIC,
        additional_exclusions: Optional[List[str]] = None
    ) -> str:
        """
        Generate a comprehensive negative prompt following professional standards.
        
        Args:
            base_negative: Base negative prompt from user
            style: Style category for context-specific exclusions
            additional_exclusions: Additional terms to exclude
            
        Returns:
            Professional negative prompt
        """
        
        negative_terms = self.negative_prompt_standards.copy()
        
        # Add base negative prompt if provided
        if base_negative:
            negative_terms.insert(0, base_negative)
        
        # Add style-specific exclusions
        if style == ImageStyle.PRODUCT:
            negative_terms.extend([
                "cluttered background", "distracting elements", "poor product visibility",
                "inconsistent lighting", "reflections", "shadows on product"
            ])
        elif style == ImageStyle.MARKETING:
            negative_terms.extend([
                "unprofessional", "amateur composition", "poor brand representation",
                "inconsistent messaging", "cluttered design", "people", "person", "human", 
                "face", "faces", "man", "woman", "child", "body", "hands", "eyes", "mouth", 
                "nose", "hair", "portrait", "model", "photorealistic", "realistic", 
                "natural lighting", "studio lighting", "photography"
            ])
        elif style == ImageStyle.PHOTOREALISTIC:
            negative_terms.extend([
                "cartoon", "anime", "painting", "sketch", "drawing",
                "artificial", "synthetic", "computer generated look"
            ])
        
        # Add additional exclusions
        if additional_exclusions:
            negative_terms.extend(additional_exclusions)
        
        return ", ".join(negative_terms)

    def _clean_prompt(self, prompt: str) -> str:
        """Clean and normalize the input prompt."""
        # Remove extra whitespace
        prompt = re.sub(r'\s+', ' ', prompt.strip())
        
        # Remove common issues
        prompt = re.sub(r'\b(image of|picture of|photo of)\b', '', prompt, flags=re.IGNORECASE)
        prompt = prompt.strip().strip(',').strip()
        
        return prompt

    def _integrate_brand_style(self, prompt: str, brand_style: Dict[str, Any]) -> str:
        """Integrate brand style parameters into the prompt."""
        
        if not brand_style:
            return prompt
        
        # Add brand keywords
        if "keywords" in brand_style and brand_style["keywords"]:
            brand_keywords = ", ".join(brand_style["keywords"])
            prompt += f", {brand_keywords} aesthetic"
        
        # Add color palette
        if "colors" in brand_style and brand_style["colors"]:
            colors = brand_style["colors"]
            if len(colors) > 0:
                color_desc = self._describe_color_palette(colors)
                prompt += f", {color_desc}"
        
        # Add style name context
        if "style_name" in brand_style:
            style_name = brand_style["style_name"]
            if style_name != "default":
                prompt += f", {style_name} brand style"
        
        return prompt

    def _describe_color_palette(self, colors: List[str]) -> str:
        """Convert hex colors to descriptive color palette."""
        
        color_map = {
            "#FFFFFF": "white", "#000000": "black", "#808080": "gray",
            "#FF0000": "red", "#00FF00": "green", "#0000FF": "blue",
            "#FFFF00": "yellow", "#FF00FF": "magenta", "#00FFFF": "cyan",
            "#FFA500": "orange", "#800080": "purple", "#FFC0CB": "pink",
            "#A52A2A": "brown", "#008000": "dark green", "#000080": "navy blue"
        }
        
        # Convert hex to color names (simplified)
        color_names = []
        for color in colors[:3]:  # Limit to 3 main colors
            # Simple color matching (in production, use proper color space conversion)
            closest_color = self._find_closest_color(color, color_map)
            if closest_color:
                color_names.append(closest_color)
        
        if color_names:
            return f"color palette with {', '.join(color_names)} tones"
        
        return "brand color palette"

    def _find_closest_color(self, hex_color: str, color_map: Dict[str, str]) -> Optional[str]:
        """Find the closest named color for a hex value."""
        # Simplified color matching - in production, use proper color distance calculation
        hex_color = hex_color.upper()
        
        if hex_color in color_map:
            return color_map[hex_color]
        
        # Basic brightness-based matching
        try:
            # Remove # if present
            hex_color = hex_color.replace("#", "")
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Calculate brightness
            brightness = (r + g + b) / 3
            
            if brightness > 200:
                return "light"
            elif brightness < 80:
                return "dark"
            else:
                return "medium"
                
        except (ValueError, IndexError):
            return None

    def get_template_enhancement(self, template_id: str) -> Dict[str, Any]:
        """Get template-specific enhancement parameters."""
        
        template_enhancements = {
            "product-hero": {
                "quality": ImageQuality.PROFESSIONAL,
                "style": ImageStyle.PRODUCT,
                "composition": CompositionRule.CENTER_COMPOSITION,
                "lighting": "studio",
                "context": "professional product photography"
            },
            "instagram-post": {
                "quality": ImageQuality.HIGH,
                "style": ImageStyle.MARKETING,
                "composition": CompositionRule.RULE_OF_THIRDS,
                "lighting": "natural",
                "context": "social media content"
            },
            "email-header": {
                "quality": ImageQuality.HIGH,
                "style": ImageStyle.MARKETING,
                "composition": CompositionRule.LEADING_LINES,
                "lighting": "professional",
                "context": "email marketing header"
            },
            "website-banner": {
                "quality": ImageQuality.ULTRA,
                "style": ImageStyle.MARKETING,
                "composition": CompositionRule.GOLDEN_RATIO,
                "lighting": "professional",
                "context": "website hero banner"
            },
            "linkedin-post": {
                "quality": ImageQuality.HIGH,
                "style": ImageStyle.MARKETING,
                "composition": CompositionRule.CENTER_COMPOSITION,
                "lighting": "professional",
                "context": "professional social media content"
            }
        }
        
        return template_enhancements.get(template_id, {
            "quality": ImageQuality.HIGH,
            "style": ImageStyle.PHOTOREALISTIC,
            "lighting": "professional"
        })

# Global instance
prompt_engineering_service = PromptEngineeringService() 