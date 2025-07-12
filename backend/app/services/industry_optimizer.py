import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from ..models.brand import Industry

logger = logging.getLogger(__name__)


class ConversionElement(Enum):
    """Elements that drive conversions in marketing visuals."""
    CALL_TO_ACTION = "call_to_action"
    URGENCY = "urgency"
    SOCIAL_PROOF = "social_proof"
    VALUE_PROPOSITION = "value_proposition"
    TRUST_SIGNALS = "trust_signals"
    EMOTIONAL_APPEAL = "emotional_appeal"
    CLARITY = "clarity"
    VISUAL_HIERARCHY = "visual_hierarchy"


class IndustryOptimizer:
    """Service for industry-specific image generation optimization."""
    
    def __init__(self):
        self.industry_configs = self._initialize_industry_configs()
        self.conversion_templates = self._initialize_conversion_templates()
    
    def get_industry_optimization(
        self,
        industry: Industry,
        content_type: str,
        target_platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get industry-specific optimization parameters."""
        
        base_config = self.industry_configs.get(industry, {})
        
        # Adjust for content type
        content_adjustments = self._get_content_type_adjustments(industry, content_type)
        
        # Adjust for platform
        platform_adjustments = {}
        if target_platform:
            platform_adjustments = self._get_platform_adjustments(target_platform)
        
        # Merge configurations
        optimization = {
            **base_config,
            **content_adjustments,
            **platform_adjustments,
            "conversion_elements": self._get_conversion_elements(industry, content_type),
            "layout_recommendations": self._get_layout_recommendations(industry, content_type)
        }
        
        return optimization
    
    def _initialize_industry_configs(self) -> Dict[Industry, Dict[str, Any]]:
        """Initialize industry-specific configurations."""
        return {
            Industry.ECOMMERCE: {
                "visual_style": "clean product photography",
                "color_psychology": "trust and urgency",
                "key_elements": ["product focus", "clear pricing", "lifestyle context"],
                "lighting": "bright, even lighting to show product details",
                "composition": "product hero shots, lifestyle settings",
                "avoid": ["cluttered backgrounds", "poor product visibility", "confusing layouts"],
                "prompt_modifiers": "e-commerce style, product showcase, commercial photography, clean background, professional product shot",
                "negative_modifiers": "amateur, blurry product, messy background, poor lighting",
                "trust_elements": ["secure badges", "customer ratings", "money-back guarantee"],
                "cta_style": "prominent, action-oriented",
                "optimal_text_overlay": ["price", "discount", "free shipping", "limited time"]
            },
            
            Industry.SAAS: {
                "visual_style": "modern, tech-forward, clean UI",
                "color_psychology": "innovation and reliability",
                "key_elements": ["interface screenshots", "feature highlights", "workflow diagrams"],
                "lighting": "bright, modern lighting",
                "composition": "UI mockups, dashboard views, feature demonstrations",
                "avoid": ["outdated interfaces", "complex diagrams", "technical jargon"],
                "prompt_modifiers": "SaaS interface, modern software UI, clean dashboard, tech startup aesthetic, professional software",
                "negative_modifiers": "outdated UI, cluttered interface, confusing design, legacy software",
                "trust_elements": ["security icons", "integration logos", "uptime badges"],
                "cta_style": "try free, demo, get started",
                "optimal_text_overlay": ["features", "pricing tiers", "free trial", "no credit card"]
            },
            
            Industry.HEALTHCARE: {
                "visual_style": "professional, clean, trustworthy",
                "color_psychology": "calm, trust, and cleanliness",
                "key_elements": ["medical professionals", "clean facilities", "patient care"],
                "lighting": "bright, clinical lighting",
                "composition": "professional healthcare settings, patient-doctor interactions",
                "avoid": ["graphic medical content", "unprofessional settings", "fear-inducing imagery"],
                "prompt_modifiers": "healthcare professional, medical facility, clean clinical environment, trustworthy medical, patient care",
                "negative_modifiers": "unsanitary, unprofessional medical, scary medical, graphic content",
                "trust_elements": ["certifications", "professional staff", "modern equipment"],
                "cta_style": "schedule appointment, learn more, contact us",
                "optimal_text_overlay": ["board certified", "patient testimonials", "insurance accepted"]
            },
            
            Industry.FINANCE: {
                "visual_style": "corporate, established, secure",
                "color_psychology": "stability and growth",
                "key_elements": ["professional settings", "data visualizations", "security symbols"],
                "lighting": "professional office lighting",
                "composition": "corporate environments, financial charts, professional people",
                "avoid": ["casual settings", "risky imagery", "get-rich-quick themes"],
                "prompt_modifiers": "financial professional, corporate finance, established institution, secure banking, professional investment",
                "negative_modifiers": "risky investment, casual finance, unprofessional, scam, get rich quick",
                "trust_elements": ["FDIC insured", "established date", "security badges"],
                "cta_style": "open account, schedule consultation, learn more",
                "optimal_text_overlay": ["rates", "FDIC insured", "established", "secure"]
            },
            
            Industry.EDUCATION: {
                "visual_style": "engaging, accessible, professional",
                "color_psychology": "inspiration and growth",
                "key_elements": ["learning environments", "students/teachers", "educational materials"],
                "lighting": "bright, welcoming lighting",
                "composition": "classroom settings, online learning, educational interactions",
                "avoid": ["overwhelming content", "outdated methods", "boring layouts"],
                "prompt_modifiers": "educational setting, modern classroom, engaged learning, professional education, inspiring academic",
                "negative_modifiers": "boring classroom, outdated education, overwhelming content, disengaged students",
                "trust_elements": ["accreditation", "success rates", "testimonials"],
                "cta_style": "enroll now, start learning, apply today",
                "optimal_text_overlay": ["accredited", "enrollment open", "scholarships available"]
            },
            
            Industry.REALESTATE: {
                "visual_style": "inviting, professional property showcase",
                "color_psychology": "warmth and possibility",
                "key_elements": ["property exteriors", "interior spaces", "neighborhood features"],
                "lighting": "natural lighting, golden hour for exteriors",
                "composition": "wide angle property shots, inviting interiors, lifestyle settings",
                "avoid": ["unflattering angles", "poor lighting", "cluttered spaces"],
                "prompt_modifiers": "real estate photography, professional property photo, inviting home, architectural photography, luxury property",
                "negative_modifiers": "poor property photo, cluttered space, unflattering angle, dark rooms",
                "trust_elements": ["MLS listing", "virtual tour", "agent credentials"],
                "cta_style": "schedule viewing, virtual tour, contact agent",
                "optimal_text_overlay": ["price", "bedrooms/bathrooms", "square footage", "open house"]
            },
            
            Industry.FASHION: {
                "visual_style": "editorial, trendy, aspirational",
                "color_psychology": "style and desire",
                "key_elements": ["fashion models", "clothing details", "lifestyle context"],
                "lighting": "professional fashion lighting, dramatic or soft",
                "composition": "editorial fashion shots, product details, lifestyle fashion",
                "avoid": ["poor styling", "unflattering poses", "cheap appearance"],
                "prompt_modifiers": "fashion photography, editorial style, high fashion, professional model, luxury fashion, style shoot",
                "negative_modifiers": "cheap fashion, poor styling, unflattering, amateur fashion shoot",
                "trust_elements": ["brand heritage", "quality materials", "size guide"],
                "cta_style": "shop now, view collection, exclusive access",
                "optimal_text_overlay": ["new collection", "limited edition", "sale", "exclusive"]
            },
            
            Industry.FOOD: {
                "visual_style": "appetizing, fresh, vibrant",
                "color_psychology": "appetite and freshness",
                "key_elements": ["food presentation", "fresh ingredients", "dining atmosphere"],
                "lighting": "natural food photography lighting",
                "composition": "overhead shots, close-up details, lifestyle dining",
                "avoid": ["unappetizing presentation", "artificial look", "messy plating"],
                "prompt_modifiers": "food photography, appetizing cuisine, fresh ingredients, professional food styling, culinary presentation",
                "negative_modifiers": "unappetizing food, messy plating, artificial food, stale appearance",
                "trust_elements": ["fresh daily", "locally sourced", "chef prepared"],
                "cta_style": "order now, view menu, book table",
                "optimal_text_overlay": ["fresh daily", "chef special", "limited time", "delivery available"]
            },
            
            Industry.AUTOMOTIVE: {
                "visual_style": "dynamic, sleek, powerful",
                "color_psychology": "power and aspiration",
                "key_elements": ["vehicle beauty shots", "performance features", "lifestyle integration"],
                "lighting": "dramatic automotive lighting",
                "composition": "hero car shots, detail shots, driving scenarios",
                "avoid": ["static boring angles", "poor reflections", "damage visible"],
                "prompt_modifiers": "automotive photography, luxury car, dynamic vehicle shot, professional car photography, sleek automobile",
                "negative_modifiers": "damaged vehicle, poor car photo, static boring angle, dirty car",
                "trust_elements": ["warranty", "safety ratings", "awards"],
                "cta_style": "schedule test drive, build yours, view inventory",
                "optimal_text_overlay": ["MPG", "starting price", "0% APR", "available now"]
            }
        }
    
    def _initialize_conversion_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize conversion-focused layout templates."""
        return {
            "hero_banner": {
                "layout": "prominent focal point with clear hierarchy",
                "text_placement": "left or center aligned with contrast",
                "cta_position": "above the fold, high contrast",
                "visual_flow": "Z-pattern or F-pattern",
                "whitespace": "30-40% for clarity"
            },
            "product_showcase": {
                "layout": "product center stage with supporting elements",
                "text_placement": "minimal, focus on product",
                "cta_position": "near product with price",
                "visual_flow": "center-out attention",
                "whitespace": "generous around product"
            },
            "social_proof": {
                "layout": "testimonial or review focus",
                "text_placement": "quote prominent with attribution",
                "cta_position": "after social proof",
                "visual_flow": "testimonial to action",
                "whitespace": "clean, uncluttered"
            },
            "comparison": {
                "layout": "side-by-side or grid comparison",
                "text_placement": "structured data points",
                "cta_position": "for each option or preferred",
                "visual_flow": "easy scanning",
                "whitespace": "clear separation"
            },
            "storytelling": {
                "layout": "narrative flow with imagery",
                "text_placement": "integrated with visuals",
                "cta_position": "at story conclusion",
                "visual_flow": "sequential narrative",
                "whitespace": "breathing room between sections"
            }
        }
    
    def _get_content_type_adjustments(
        self,
        industry: Industry,
        content_type: str
    ) -> Dict[str, Any]:
        """Get adjustments based on content type."""
        
        adjustments = {}
        
        if content_type == "email_header":
            adjustments["aspect_ratio"] = "wide"
            adjustments["text_space"] = "reserved for email text"
            adjustments["complexity"] = "simple for quick scanning"
        
        elif content_type == "social_media_post":
            adjustments["aspect_ratio"] = "square or vertical"
            adjustments["visual_impact"] = "immediate attention grab"
            adjustments["mobile_optimized"] = True
        
        elif content_type == "website_banner":
            adjustments["aspect_ratio"] = "wide hero"
            adjustments["responsive_considerations"] = True
            adjustments["text_overlay_safe_zones"] = True
        
        elif content_type == "product_image":
            adjustments["focus"] = "product details"
            adjustments["background"] = "clean or lifestyle"
            adjustments["multiple_angles"] = True
        
        elif content_type == "infographic":
            adjustments["data_visualization"] = True
            adjustments["visual_hierarchy"] = "critical"
            adjustments["readability"] = "high priority"
        
        return adjustments
    
    def _get_platform_adjustments(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific adjustments."""
        
        platform_specs = {
            "instagram": {
                "sizes": ["1080x1080", "1080x1350"],
                "safe_zones": "center 80%",
                "text_considerations": "minimal text, visual storytelling"
            },
            "facebook": {
                "sizes": ["1200x630", "1080x1080"],
                "text_limit": "20% rule consideration",
                "engagement_elements": "shareable content"
            },
            "linkedin": {
                "sizes": ["1200x627", "1080x1080"],
                "professional_tone": True,
                "b2b_focus": True
            },
            "twitter": {
                "sizes": ["1200x675", "1200x600"],
                "quick_impact": True,
                "conversation_starter": True
            },
            "email": {
                "sizes": ["600x200", "600x300"],
                "load_time": "optimize for quick loading",
                "dark_mode_consideration": True
            },
            "website": {
                "sizes": ["1920x600", "1920x800"],
                "responsive": True,
                "performance": "optimized file size"
            }
        }
        
        return platform_specs.get(platform.lower(), {})
    
    def _get_conversion_elements(
        self,
        industry: Industry,
        content_type: str
    ) -> List[Dict[str, Any]]:
        """Get conversion elements for the industry and content type."""
        
        elements = []
        
        # Industry-specific conversion drivers
        industry_elements = {
            Industry.ECOMMERCE: [
                ConversionElement.URGENCY,
                ConversionElement.VALUE_PROPOSITION,
                ConversionElement.SOCIAL_PROOF
            ],
            Industry.SAAS: [
                ConversionElement.VALUE_PROPOSITION,
                ConversionElement.TRUST_SIGNALS,
                ConversionElement.CALL_TO_ACTION
            ],
            Industry.HEALTHCARE: [
                ConversionElement.TRUST_SIGNALS,
                ConversionElement.CLARITY,
                ConversionElement.EMOTIONAL_APPEAL
            ],
            Industry.FINANCE: [
                ConversionElement.TRUST_SIGNALS,
                ConversionElement.VALUE_PROPOSITION,
                ConversionElement.CLARITY
            ]
        }
        
        for element in industry_elements.get(industry, []):
            elements.append({
                "type": element.value,
                "implementation": self._get_element_implementation(element, industry)
            })
        
        return elements
    
    def _get_element_implementation(
        self,
        element: ConversionElement,
        industry: Industry
    ) -> str:
        """Get specific implementation for a conversion element."""
        
        implementations = {
            ConversionElement.CALL_TO_ACTION: {
                Industry.ECOMMERCE: "Shop Now, Add to Cart, Buy Now",
                Industry.SAAS: "Start Free Trial, Get Demo, Sign Up",
                Industry.HEALTHCARE: "Book Appointment, Contact Us, Learn More",
                Industry.FINANCE: "Open Account, Get Quote, Apply Now"
            },
            ConversionElement.URGENCY: {
                Industry.ECOMMERCE: "Limited Stock, Sale Ends Soon, Today Only",
                Industry.SAAS: "Limited Time Offer, Spots Filling Fast",
                Industry.HEALTHCARE: "Appointments Available, Schedule Today",
                Industry.FINANCE: "Rates May Change, Lock In Today"
            },
            ConversionElement.SOCIAL_PROOF: {
                Industry.ECOMMERCE: "5-star reviews, Customer photos, Best seller",
                Industry.SAAS: "Join 10,000+ companies, Customer logos, Case studies",
                Industry.HEALTHCARE: "Patient testimonials, Years of experience",
                Industry.FINANCE: "Client success stories, Assets managed"
            },
            ConversionElement.TRUST_SIGNALS: {
                Industry.ECOMMERCE: "Secure checkout, Money-back guarantee, Free returns",
                Industry.SAAS: "SOC2 compliant, 99.9% uptime, Data encryption",
                Industry.HEALTHCARE: "Board certified, Accredited facility, HIPAA compliant",
                Industry.FINANCE: "FDIC insured, Regulated, Established 1990"
            }
        }
        
        return implementations.get(element, {}).get(industry, "Industry-specific implementation")
    
    def _get_layout_recommendations(
        self,
        industry: Industry,
        content_type: str
    ) -> Dict[str, Any]:
        """Get layout recommendations for conversion optimization."""
        
        base_layout = self.conversion_templates.get(content_type, self.conversion_templates["hero_banner"])
        
        # Industry-specific adjustments
        industry_layouts = {
            Industry.ECOMMERCE: {
                "product_prominence": "70% of visual space",
                "price_visibility": "clear and prominent",
                "trust_badge_placement": "near CTA"
            },
            Industry.SAAS: {
                "interface_showcase": "center stage",
                "feature_highlights": "visual callouts",
                "demo_cta": "multiple touchpoints"
            },
            Industry.HEALTHCARE: {
                "human_element": "trustworthy professionals",
                "credentials": "visible but not overwhelming",
                "contact_info": "easily accessible"
            },
            Industry.FINANCE: {
                "data_visualization": "clear and accurate",
                "security_emphasis": "subtle but present",
                "professional_imagery": "corporate setting"
            }
        }
        
        return {
            **base_layout,
            **industry_layouts.get(industry, {})
        }
    
    def generate_optimized_prompt(
        self,
        base_prompt: str,
        industry: Industry,
        content_type: str,
        conversion_goal: Optional[str] = None
    ) -> Tuple[str, str]:
        """Generate an optimized prompt for the industry and conversion goals."""
        
        config = self.industry_configs.get(industry, {})
        
        # Build positive prompt
        prompt_parts = [base_prompt]
        
        # Add industry modifiers
        if config.get("prompt_modifiers"):
            prompt_parts.append(config["prompt_modifiers"])
        
        # Add conversion elements
        if conversion_goal:
            conversion_prompts = {
                "sales": "compelling product presentation, clear value proposition",
                "leads": "professional trust-building imagery, approachable",
                "awareness": "memorable brand presence, unique visual impact",
                "engagement": "shareable content, conversation starter"
            }
            if conversion_goal in conversion_prompts:
                prompt_parts.append(conversion_prompts[conversion_goal])
        
        # Add content type specifics
        content_prompts = {
            "email_header": "email-safe design, clear focal point, mobile-friendly",
            "social_media_post": "scroll-stopping visual, social media optimized",
            "website_banner": "hero banner design, web-optimized, clear hierarchy",
            "product_image": "product photography, e-commerce ready, detailed view"
        }
        if content_type in content_prompts:
            prompt_parts.append(content_prompts[content_type])
        
        enhanced_prompt = ", ".join(prompt_parts)
        
        # Build negative prompt
        negative_parts = []
        if config.get("negative_modifiers"):
            negative_parts.append(config["negative_modifiers"])
        
        # Add general quality negatives
        negative_parts.extend([
            "low quality", "amateur", "stock photo watermark",
            "pixelated", "blurry", "poorly lit"
        ])
        
        # Add industry-specific negatives
        avoid_elements = config.get("avoid", [])
        negative_parts.extend(avoid_elements)
        
        enhanced_negative = ", ".join(negative_parts)
        
        return enhanced_prompt, enhanced_negative