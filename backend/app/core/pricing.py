# Production-ready pricing calculations for AWS Bedrock models

from typing import Dict

# AWS Bedrock pricing as of 2024 (USD per image)
BEDROCK_PRICING: Dict[str, float] = {
    "stability.stable-diffusion-xl-v1": 0.04,  # SDXL 1024x1024 or smaller
    "stability.stable-diffusion-xl-v0": 0.04,  # SDXL legacy
    "amazon.titan-image-generator-v1": 0.008,  # Titan Image Generator
}

# Size-based pricing adjustments for some models
SIZE_MULTIPLIERS: Dict[str, Dict[str, float]] = {
    "stability.stable-diffusion-xl-v1": {
        "512x512": 1.0,
        "768x768": 1.0,
        "1024x1024": 1.0,
        "1152x896": 1.5,
        "1216x832": 1.5,
        "1344x768": 1.5,
        "1536x640": 1.5,
    }
}


def calculate_generation_cost(model_id: str, num_images: int, size: str = "1024x1024") -> float:
    """
    Calculate the cost for generating images with a specific model.
    
    Args:
        model_id: The Bedrock model identifier
        num_images: Number of images to generate
        size: Image size (e.g., "1024x1024")
    
    Returns:
        Total cost in USD
    """
    base_cost = BEDROCK_PRICING.get(model_id, 0.04)  # Default to SDXL pricing
    
    # Apply size multiplier if applicable
    if model_id in SIZE_MULTIPLIERS and size in SIZE_MULTIPLIERS[model_id]:
        multiplier = SIZE_MULTIPLIERS[model_id][size]
        base_cost *= multiplier
    
    return base_cost * num_images


def get_model_pricing_info(model_id: str) -> Dict[str, any]:
    """
    Get pricing information for a specific model.
    
    Args:
        model_id: The Bedrock model identifier
    
    Returns:
        Dictionary with pricing information
    """
    base_cost = BEDROCK_PRICING.get(model_id, 0.04)
    
    return {
        "model_id": model_id,
        "base_cost_per_image": base_cost,
        "currency": "USD",
        "size_multipliers": SIZE_MULTIPLIERS.get(model_id, {}),
        "notes": "Pricing based on AWS Bedrock official rates"
    } 