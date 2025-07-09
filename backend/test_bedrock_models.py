#!/usr/bin/env python3
"""
Test script to check available Bedrock models and test image generation.
"""

import os
import sys
import json
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

import boto3
from loguru import logger
from app.core.config import get_settings

def check_available_models():
    """Check which Bedrock models are available."""
    try:
        logger.info("🔍 Checking available Bedrock models...")
        
        settings = get_settings()
        
        # Create Bedrock client
        session_params = {
            "region_name": settings.aws_region,
        }
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            session_params.update({
                "aws_access_key_id": settings.aws_access_key_id,
                "aws_secret_access_key": settings.aws_secret_access_key,
                "aws_session_token": settings.aws_session_token,
            })
        
        session = boto3.Session(**session_params)
        bedrock_client = session.client("bedrock")
        
        # List all foundation models
        response = bedrock_client.list_foundation_models()
        models = response.get('modelSummaries', [])
        
        logger.info(f"📊 Found {len(models)} total models")
        
        # Filter for image generation models
        image_models = []
        for model in models:
            model_id = model.get('modelId', '')
            if any(keyword in model_id.lower() for keyword in ['image', 'diffusion', 'titan-image']):
                image_models.append(model)
        
        logger.info(f"🎨 Found {len(image_models)} image generation models:")
        
        available_models = []
        for model in image_models:
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', 'N/A')
            provider = model.get('providerName', 'N/A')
            
            logger.info(f"   ✅ {model_id}")
            logger.info(f"      Name: {model_name}")
            logger.info(f"      Provider: {provider}")
            
            available_models.append(model_id)
        
        return available_models
        
    except Exception as e:
        logger.error(f"❌ Error checking models: {e}")
        return []

def test_model_access(model_id):
    """Test if we can access a specific model."""
    try:
        logger.info(f"🧪 Testing access to model: {model_id}")
        
        settings = get_settings()
        
        # Create Bedrock Runtime client
        session_params = {
            "region_name": settings.aws_region,
        }
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            session_params.update({
                "aws_access_key_id": settings.aws_access_key_id,
                "aws_secret_access_key": settings.aws_secret_access_key,
                "aws_session_token": settings.aws_session_token,
            })
        
        session = boto3.Session(**session_params)
        bedrock_runtime = session.client("bedrock-runtime")
        
        # Try to get model info (this will fail if model is not accessible)
        if "stability" in model_id:
            # Test payload for Stable Diffusion
            test_payload = {
                "text_prompts": [{"text": "test", "weight": 1.0}],
                "cfg_scale": 7.5,
                "steps": 1,  # Minimal steps for testing
                "samples": 1,
                "width": 512,
                "height": 512,
            }
        elif "titan" in model_id:
            # Test payload for Titan
            test_payload = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": "test",
                    "negativeText": "",
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,
                    "quality": "standard",
                    "cfgScale": 7.5,
                    "height": 512,
                    "width": 512,
                    "seed": 0,
                }
            }
        else:
            logger.warning(f"⚠️  Unknown model type: {model_id}")
            return False
        
        # Try to invoke the model (this will fail if not accessible)
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(test_payload),
        )
        
        logger.success(f"✅ Model {model_id} is accessible!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Model {model_id} is not accessible: {e}")
        return False

def main():
    """Main test function."""
    logger.info("🚀 Starting Bedrock Model Availability Test...")
    
    # Check available models
    available_models = check_available_models()
    
    if not available_models:
        logger.error("❌ No image generation models found!")
        logger.info("Please enable image generation models in AWS Bedrock Console")
        return
    
    # Test access to each model
    accessible_models = []
    for model_id in available_models:
        if test_model_access(model_id):
            accessible_models.append(model_id)
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("📊 BEDROCK MODEL TEST RESULTS")
    logger.info("="*50)
    
    if accessible_models:
        logger.success(f"🎉 {len(accessible_models)} models are accessible!")
        logger.info("Available models for your application:")
        for model_id in accessible_models:
            logger.info(f"   ✅ {model_id}")
        
        # Recommend the best model
        if "stability.stable-diffusion-xl-v1" in accessible_models:
            recommended = "stability.stable-diffusion-xl-v1"
        elif "amazon.titan-image-generator-v1" in accessible_models:
            recommended = "amazon.titan-image-generator-v1:0"
        else:
            recommended = accessible_models[0]
        
        logger.info(f"\n💡 Recommended model: {recommended}")
        logger.info("Update your .env file with:")
        logger.info(f"BEDROCK_MODEL_ID={recommended}")
        
    else:
        logger.error("❌ No models are accessible!")
        logger.error("Please check your IAM permissions and model access")
    
    logger.info("\nNext steps:")
    logger.info("1. Update your .env file with the recommended model")
    logger.info("2. Run: python test_aws_integration.py")
    logger.info("3. Run: python test_image_generation.py")

if __name__ == "__main__":
    main() 