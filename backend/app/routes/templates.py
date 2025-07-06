from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from ..models.schemas import Template

router = APIRouter(prefix="/v1/templates", tags=["templates"])

# Predefined templates
TEMPLATES = [
    Template(
        id="product-hero",
        name="Product Hero Shot",
        category="E-commerce",
        description="Professional product photography with clean background",
        prompt_template="Professional product photography of {product_name}, {style_description}, clean white background, studio lighting, high resolution, commercial photography",
        negative_prompt="blurry, low quality, watermark, text overlay, cluttered background",
        default_size="1024x1024",
        parameters={
            "style_description": "modern minimalist design",
            "lighting": "studio lighting",
            "background": "clean white"
        }
    ),
    Template(
        id="instagram-post",
        name="Instagram Post",
        category="Social Media",
        description="Square format optimized for Instagram feed",
        prompt_template="Instagram-worthy image of {subject}, {mood} atmosphere, {style} style, perfect for social media, square composition",
        negative_prompt="text overlay, watermark, low quality, blurry",
        default_size="1024x1024",
        parameters={
            "mood": "bright and cheerful",
            "style": "modern",
            "composition": "square"
        }
    ),
    Template(
        id="lifestyle-scene",
        name="Lifestyle Scene",
        category="Marketing",
        description="Authentic lifestyle photography showing products in use",
        prompt_template="Lifestyle photography of {subject} in {setting}, {mood} atmosphere, natural lighting, authentic, relatable scene",
        negative_prompt="staged, artificial, overly perfect, stock photo look",
        default_size="1024x1024",
        parameters={
            "setting": "modern home environment",
            "mood": "warm and inviting",
            "lighting": "natural"
        }
    ),
    Template(
        id="email-header",
        name="Email Header",
        category="Marketing",
        description="Wide format header image for email campaigns",
        prompt_template="Email header banner design for {subject}, {brand_style} aesthetic, {color_scheme} color palette, clean graphic design, marketing banner, email header layout, wide banner format",
        negative_prompt="text overlay, cluttered, low resolution, storefront, building, people, products, photography, realistic objects, 3D objects",
        default_size="1408x640",
        parameters={
            "brand_style": "modern and professional",
            "color_scheme": "brand colors",
            "format": "wide header"
        }
    ),
    Template(
        id="website-banner",
        name="Website Banner",
        category="Web",
        description="Hero banner for website homepage",
        prompt_template="Website hero banner featuring {subject}, {brand_style} design, {color_scheme}, modern web design aesthetic",
        negative_prompt="text, buttons, navigation elements, low quality",
        default_size="1408x640",
        parameters={
            "brand_style": "clean and modern",
            "color_scheme": "brand palette",
            "format": "wide banner"
        }
    ),
    Template(
        id="linkedin-post",
        name="LinkedIn Post",
        category="Social Media",
        description="Professional image optimized for LinkedIn",
        prompt_template="Professional LinkedIn post image featuring {subject}, {business_context}, clean design, corporate aesthetic",
        negative_prompt="casual, informal, bright colors, text overlay",
        default_size="1216x640",
        parameters={
            "business_context": "professional business environment",
            "style": "corporate and clean",
            "format": "LinkedIn optimized"
        }
    ),
    Template(
        id="product-catalog",
        name="Product Catalog",
        category="E-commerce",
        description="Grid-style product catalog image",
        prompt_template="Product catalog layout featuring {product_name}, {catalog_style} arrangement, clean grid, commercial photography",
        negative_prompt="cluttered, messy, low quality, inconsistent lighting",
        default_size="1024x1024",
        parameters={
            "catalog_style": "clean grid layout",
            "lighting": "consistent studio lighting",
            "background": "neutral"
        }
    ),
    Template(
        id="seasonal-campaign",
        name="Seasonal Campaign",
        category="Marketing",
        description="Seasonal or holiday-themed marketing image",
        prompt_template="Seasonal marketing image featuring {subject}, {season} theme, {holiday_context}, festive atmosphere",
        negative_prompt="generic, non-seasonal, inappropriate for season",
        default_size="1024x1024",
        parameters={
            "season": "current season",
            "holiday_context": "appropriate holiday theme",
            "mood": "festive and engaging"
        }
    )
]

# Professional templates with enhanced quality controls
PROFESSIONAL_TEMPLATES = [
    {
        "id": "product-hero-pro",
        "name": "Professional Product Hero",
        "category": "product",
        "description": "Professional product photography with studio lighting and perfect composition",
        "prompt_template": "Professional product photography of {product_name}, {product_description}",
        "negative_prompt": "amateur, poor lighting, cluttered background, distracting elements, low quality, blurry",
        "default_size": "1024x768",
        "parameters": {
            "product_name": "Product Name",
            "product_description": "Brief product description"
        },
        "is_active": True,
        "quality": "professional",
        "style": "product",
        "composition": "center_composition",
        "lighting": "studio"
    },
    {
        "id": "social-media-pro",
        "name": "Professional Social Media",
        "category": "social",
        "description": "High-quality social media content with engaging composition",
        "prompt_template": "Professional social media content for {platform}, {content_theme}",
        "negative_prompt": "unprofessional, amateur, poor composition, low engagement, cluttered",
        "default_size": "1024x1024",
        "parameters": {
            "platform": "Instagram/LinkedIn/Facebook",
            "content_theme": "Content theme or message"
        },
        "is_active": True,
        "quality": "high",
        "style": "marketing",
        "composition": "rule_of_thirds",
        "lighting": "natural"
    },
    {
        "id": "website-hero-pro",
        "name": "Professional Website Hero",
        "category": "web",
        "description": "Ultra-high quality website hero banners with perfect composition",
        "prompt_template": "Professional website hero banner for {business_type}, {key_message}",
        "negative_prompt": "amateur, poor composition, low quality, cluttered, distracting elements",
        "default_size": "1024x512",
        "parameters": {
            "business_type": "Type of business",
            "key_message": "Main message or value proposition"
        },
        "is_active": True,
        "quality": "ultra",
        "style": "marketing",
        "composition": "golden_ratio",
        "lighting": "professional"
    },
    {
        "id": "email-header-pro",
        "name": "Professional Email Header",
        "category": "email",
        "description": "Professional email marketing headers with leading lines composition",
        "prompt_template": "Professional email marketing header banner design for {campaign_theme}, {call_to_action}, clean graphic design, marketing banner, email header layout, professional typography space, modern design aesthetic, wide banner format",
        "negative_prompt": "amateur, poor email design, low quality, unprofessional, cluttered, storefront, building, people, products, photography, realistic objects, 3D objects",
        "default_size": "1408x640",
        "parameters": {
            "campaign_theme": "Campaign theme",
            "call_to_action": "Main call to action"
        },
        "is_active": True,
        "quality": "high",
        "style": "marketing",
        "composition": "leading_lines",
        "lighting": "professional"
    },
    {
        "id": "technical-illustration-pro",
        "name": "Professional Technical Illustration",
        "category": "technical",
        "description": "Professional technical illustrations with precise documentation style",
        "prompt_template": "Professional technical illustration of {subject}, {technical_details}",
        "negative_prompt": "amateur, imprecise, unclear, low quality, artistic style, decorative",
        "default_size": "1024x768",
        "parameters": {
            "subject": "Technical subject",
            "technical_details": "Specific technical details"
        },
        "is_active": True,
        "quality": "professional",
        "style": "technical",
        "composition": "center_composition",
        "lighting": "soft"
    },
    {
        "id": "luxury-brand-pro",
        "name": "Luxury Brand Photography",
        "category": "brand",
        "description": "Premium luxury brand photography with elegant composition",
        "prompt_template": "Luxury brand photography of {product_category}, {luxury_elements}",
        "negative_prompt": "cheap, amateur, poor quality, mass market, cluttered, unprofessional",
        "default_size": "1024x1024",
        "parameters": {
            "product_category": "Product category",
            "luxury_elements": "Luxury elements or materials"
        },
        "is_active": True,
        "quality": "professional",
        "style": "product",
        "composition": "symmetry",
        "lighting": "dramatic"
    },
    {
        "id": "corporate-headshot-pro",
        "name": "Professional Corporate Headshot",
        "category": "corporate",
        "description": "Professional corporate headshots with studio lighting",
        "prompt_template": "Professional corporate headshot of {person_description}, {setting}",
        "negative_prompt": "amateur, poor lighting, unprofessional, casual, low quality, blurry",
        "default_size": "768x1024",
        "parameters": {
            "person_description": "Person description",
            "setting": "Professional setting"
        },
        "is_active": True,
        "quality": "professional",
        "style": "photorealistic",
        "composition": "center_composition",
        "lighting": "studio"
    },
    {
        "id": "event-photography-pro",
        "name": "Professional Event Photography",
        "category": "event",
        "description": "Professional event photography with natural lighting",
        "prompt_template": "Professional event photography of {event_type}, {atmosphere}",
        "negative_prompt": "amateur, poor lighting, blurry, low quality, unprofessional composition",
        "default_size": "1024x768",
        "parameters": {
            "event_type": "Type of event",
            "atmosphere": "Desired atmosphere"
        },
        "is_active": True,
        "quality": "high",
        "style": "photorealistic",
        "composition": "rule_of_thirds",
        "lighting": "natural"
    }
]

# Convert professional template dictionaries to Template objects and add to existing templates
for template_dict in PROFESSIONAL_TEMPLATES:
    template_obj = Template(
        id=template_dict["id"],
        name=template_dict["name"],
        category=template_dict["category"],
        description=template_dict["description"],
        prompt_template=template_dict["prompt_template"],
        negative_prompt=template_dict.get("negative_prompt"),
        default_size=template_dict["default_size"],
        parameters=template_dict["parameters"],
        is_active=template_dict["is_active"]
    )
    TEMPLATES.append(template_obj)


@router.get("/", response_model=List[Template])
async def list_templates(category: str = None) -> List[Template]:
    """List all available templates, optionally filtered by category."""
    if category:
        filtered_templates = [t for t in TEMPLATES if t.category.lower() == category.lower()]
        return filtered_templates
    return TEMPLATES


@router.get("/categories", response_model=List[str])
async def list_categories() -> List[str]:
    """List all available template categories."""
    categories = list(set(template.category for template in TEMPLATES))
    return sorted(categories)


@router.get("/{template_id}", response_model=Template)
async def get_template(template_id: str) -> Template:
    """Get a specific template by ID."""
    template = next((t for t in TEMPLATES if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return template


@router.get("/{template_id}/prompt", response_model=dict)
async def get_template_prompt(template_id: str, **params) -> dict:
    """Get a rendered prompt from a template with provided parameters."""
    template = next((t for t in TEMPLATES if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    
    # Render the prompt template with provided parameters
    try:
        rendered_prompt = template.prompt_template.format(**params)
        return {
            "template_id": template_id,
            "prompt": rendered_prompt,
            "negative_prompt": template.negative_prompt,
            "size": template.default_size,
            "parameters": params
        }
    except KeyError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required parameter: {e}"
        ) 