from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from ..models.schemas import Template
from ..services.llm_prompt_generator import llm_prompt_generator

router = APIRouter(prefix="/v1/templates", tags=["templates"])

# Dynamic LLM-generated templates
def create_dynamic_template(template_id: str, name: str, category: str, description: str, 
                          template_type: str, default_size: str) -> Template:
    """Create a template that uses LLM-generated prompts."""
    return Template(
        id=template_id,
        name=name,
        category=category,
        description=description,
        prompt_template="DYNAMIC_LLM_GENERATED",  # Special marker for dynamic generation
        negative_prompt="DYNAMIC_LLM_GENERATED",  # Special marker for dynamic generation
        default_size=default_size,
        parameters={
            "subject": "theme or message",
            "template_type": template_type
        }
    )

TEMPLATES = [
    create_dynamic_template(
        template_id="social-media-post",
        name="Social Media Post",
        category="Social Media", 
        description="Clean, professional social media graphics",
        template_type="social_media",
        default_size="1024x1024"
    )
]

# No additional professional templates - keeping it simple with 3 high-quality templates


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