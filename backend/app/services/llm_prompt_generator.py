"""
LLM-based prompt generation service for creating contextually accurate image prompts.
Uses structured prompt engineering to generate proper prompts instead of keyword concatenation.
"""

from typing import Dict, Optional
import json

class LLMPromptGenerator:
    """Generate contextually accurate prompts using LLM-style prompt engineering."""
    
    def __init__(self):
        self.prompt_templates = {
            "social_media": {
                "base_structure": "Create a {style} social media graphic about {subject}. Use {visual_elements} with {color_scheme}. Square format, abstract design, no text, no people.",
                "styles": {
                    "modern": "modern, clean",
                    "trendy": "trendy, contemporary", 
                    "professional": "professional, polished",
                    "creative": "creative, unique",
                    "minimal": "minimal, sophisticated"
                },
                "visual_elements": [
                    "geometric shapes and patterns",
                    "abstract forms and compositions", 
                    "gradient backgrounds",
                    "clean minimalist design",
                    "colorful geometric elements"
                ]
            }
        }
        
        self.strong_negative_prompts = {
            "universal": [
                "text", "letters", "words", "typography", "writing", "alphabet", "numbers",
                "people", "person", "human", "face", "faces", "man", "woman", "child", 
                "body", "hands", "eyes", "mouth", "nose", "hair", "portrait", "model",
                "photography", "photo", "realistic", "photorealistic", "camera", "lens",
                "products", "objects", "items", "buildings", "architecture", "storefront",
                "cluttered", "busy", "messy", "chaotic", "disorganized",
                "watermark", "logo", "signature", "copyright", "brand mark"
            ],
            "email_header": [
                "lifestyle", "fashion", "people wearing clothes", "models", "outdoor scenes",
                "natural lighting", "studio lighting", "commercial photography",
                "product placement", "retail", "shopping", "lifestyle photography"
            ],
            "social_media": [
                "amateur", "unprofessional", "low quality", "pixelated", "blurry"
            ],
            "website_hero": [
                "navigation", "buttons", "UI elements", "interface", "menu", "header"
            ]
        }

    def generate_prompt(self, template_type: str, subject: str, style: str = "modern") -> Dict[str, str]:
        """Generate a simple, effective prompt for social media graphics."""
        
        # Default to social media if template not found
        if template_type not in self.prompt_templates:
            template_type = "social_media"
            
        template = self.prompt_templates[template_type]
        
        # Select visual elements randomly for variety
        import random
        visual_elements = random.choice(template["visual_elements"])
        
        # Generate color scheme based on subject
        color_scheme = self._generate_color_scheme(subject)
        
        # Build simple, effective prompt
        main_prompt = template["base_structure"].format(
            style=template["styles"].get(style, template["styles"]["modern"]),
            subject=subject,
            visual_elements=visual_elements,
            color_scheme=color_scheme
        )
        
        # Simple but comprehensive negative prompt
        negative_prompt = "text, letters, words, people, faces, humans, photography, realistic objects, cluttered, messy"
        
        return {
            "prompt": main_prompt,
            "negative_prompt": negative_prompt
        }

    def _extract_purpose(self, subject: str, template_type: str) -> str:
        """Extract the purpose from the subject text."""
        subject_lower = subject.lower()
        
        if template_type == "email_header":
            if any(word in subject_lower for word in ["sale", "discount", "off", "deal", "promotion"]):
                return "sale"
            elif any(word in subject_lower for word in ["announcement", "news", "update", "launch"]):
                return "announcement"
            elif any(word in subject_lower for word in ["event", "conference", "meeting", "webinar"]):
                return "event"
            elif any(word in subject_lower for word in ["product", "collection", "catalog"]):
                return "product"
            else:
                return "newsletter"
                
        elif template_type == "social_media":
            if any(word in subject_lower for word in ["brand", "company", "business"]):
                return "brand"
            elif any(word in subject_lower for word in ["announcement", "news", "launch"]):
                return "announcement"
            else:
                return "engagement"
                
        elif template_type == "website_hero":
            if any(word in subject_lower for word in ["tech", "software", "digital", "app"]):
                return "tech"
            elif any(word in subject_lower for word in ["creative", "design", "art", "agency"]):
                return "creative"
            elif any(word in subject_lower for word in ["corporate", "enterprise", "business"]):
                return "corporate"
            else:
                return "business"
        
        return "announcement"  # Default fallback

    def _select_visual_elements(self, subject: str, available_elements: Dict[str, str]) -> str:
        """Select appropriate visual elements based on subject."""
        subject_lower = subject.lower()
        
        if any(word in subject_lower for word in ["minimal", "clean", "simple"]):
            return available_elements.get("minimal", available_elements["geometric"])
        elif any(word in subject_lower for word in ["dynamic", "energy", "bold", "vibrant"]):
            return available_elements.get("dynamic", available_elements["geometric"])
        elif any(word in subject_lower for word in ["organic", "natural", "flowing"]):
            return available_elements.get("organic", available_elements["geometric"])
        else:
            return available_elements["geometric"]

    def _generate_color_scheme(self, subject: str) -> str:
        """Generate appropriate color scheme description."""
        subject_lower = subject.lower()
        
        if any(word in subject_lower for word in ["summer", "bright", "vibrant", "energy"]):
            return "bright, vibrant colors with warm tones"
        elif any(word in subject_lower for word in ["professional", "corporate", "business"]):
            return "professional color palette with blues and grays"
        elif any(word in subject_lower for word in ["luxury", "premium", "elegant"]):
            return "sophisticated color scheme with gold and dark tones"
        elif any(word in subject_lower for word in ["tech", "digital", "modern"]):
            return "modern color palette with blues and teals"
        elif any(word in subject_lower for word in ["creative", "art", "design"]):
            return "creative color combinations with artistic flair"
        else:
            return "balanced color palette with complementary tones"

    def _build_negative_prompt(self, template_type: str) -> str:
        """Build comprehensive negative prompt."""
        negative_terms = self.strong_negative_prompts["universal"].copy()
        
        if template_type in self.strong_negative_prompts:
            negative_terms.extend(self.strong_negative_prompts[template_type])
        
        return ", ".join(negative_terms)


# Global instance
llm_prompt_generator = LLMPromptGenerator() 