#!/usr/bin/env python3
"""
Test script to verify end-to-end image generation and S3 storage.
Run this after the integration test passes.
"""

import os
import sys
import time
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.s3 import s3_service
from app.services.bedrock import bedrock_service
from app.core.config import get_settings
from loguru import logger

def test_image_generation():
    """Test complete image generation and S3 upload workflow."""
    try:
        logger.info("🎨 Testing image generation and S3 upload...")
        
        # Test prompt
        test_prompt = "A professional product photo of a modern smartphone on a clean white background, high quality, studio lighting"
        
        start_time = time.time()
        
        # Generate image
        logger.info(f"Generating image with prompt: {test_prompt[:50]}...")
        images = bedrock_service.generate_images(
            prompt=test_prompt,
            num_images=1,
            size="1024x1024"
        )
        
        generation_time = time.time() - start_time
        logger.success(f"✅ Generated {len(images)} image(s) in {generation_time:.2f}s")
        
        if not images:
            logger.error("❌ No images generated")
            return False, None, None
        
        # Upload to S3
        logger.info("Uploading image to S3...")
        image_bytes = images[0]
        
        # Create a test key
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        test_key = f"test/generated-test-{timestamp}.png"
        
        # Upload
        s3_url = s3_service.upload_bytes(image_bytes, test_key, "image/png")
        logger.success(f"✅ Image uploaded to S3: {s3_url}")
        
        # Generate presigned URL
        presigned_url = s3_service.generate_presigned_url(test_key, expires_in=3600)
        logger.success(f"✅ Presigned URL generated: {presigned_url[:50]}...")
        
        # Test file size
        file_size_kb = len(image_bytes) / 1024
        logger.info(f"📊 Generated image size: {file_size_kb:.1f} KB")
        
        return True, s3_url, presigned_url
        
    except Exception as e:
        logger.error(f"❌ Image generation test failed: {e}")
        return False, None, None

def main():
    """Run the image generation test."""
    logger.info("🚀 Starting Image Generation Test...")
    
    success, s3_url, presigned_url = test_image_generation()
    
    if success:
        logger.success("\n🎉 Image generation test passed!")
        logger.info("Your AWS S3 and Bedrock integration is working correctly.")
        logger.info(f"Generated image URL: {s3_url}")
        logger.info(f"Presigned URL: {presigned_url[:50]}...")
        logger.info("\nYou can now start generating images through your API!")
    else:
        logger.error("\n❌ Image generation test failed.")
        logger.error("Please check the error messages above and fix any issues.")
        sys.exit(1)

if __name__ == "__main__":
    main() 