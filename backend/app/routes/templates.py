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
        default_size="1080x1080",
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
        prompt_template="Email header design featuring {subject}, {brand_style} aesthetic, {color_scheme} color palette, professional marketing image",
        negative_prompt="text overlay, cluttered, low resolution",
        default_size="1200x400",
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
        default_size="1920x600",
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
        default_size="1200x627",
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