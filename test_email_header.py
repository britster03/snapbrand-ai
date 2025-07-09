#!/usr/bin/env python3
"""Test script for email header generation with Titan V2."""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.bedrock import bedrock_service
from app.core.config import get_settings

async def test_email_header_generation():
    """Test email header generation with the fixed size."""
    print("=== Email Header Generation Test ===")
    
    # Print configuration
    settings = get_settings()
    print(f"Model ID: {settings.bedrock_model_id}")
    print(f"AWS Region: {settings.aws_region}")
    
    # Test email header prompt (similar to what the template would generate)
    prompt = "Email header banner design for summer sale campaign, modern and professional aesthetic, vibrant color palette, clean graphic design, marketing banner, email header layout, wide banner format"
    negative_prompt = "text overlay, cluttered, low resolution, storefront, building, people, products, photography, realistic objects, 3D objects"
    
    # Use the corrected size (supported by Titan V2)
    size = "1408x640"
    
    print(f"\nTesting email header generation:")
    print(f"  Size: {size}")
    print(f"  Prompt: {prompt[:100]}...")
    
    try:
        # Generate image
        images = bedrock_service.generate_images(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_images=1,
            size=size,
            guidance_scale=8.0,
            quality="premium"
        )
        
        print(f"\nGeneration successful!")
        print(f"Generated {len(images)} images")
        for i, image_bytes in enumerate(images):
            print(f"Image {i+1}: {len(image_bytes)} bytes")
        
        # Save first image for inspection
        if images:
            with open("test_email_header.png", "wb") as f:
                f.write(images[0])
            print(f"\nSaved email header image to: test_email_header.png")
        
    except Exception as e:
        print(f"\nError generating email header: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_email_header_generation()) 