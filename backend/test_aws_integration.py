#!/usr/bin/env python3
"""
Test script to verify AWS S3 and Bedrock integration.
Run this before starting the main application.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.s3 import s3_service
from app.services.bedrock import bedrock_service
from app.core.config import get_settings
from loguru import logger

def test_s3_connection():
    """Test S3 connection and bucket access."""
    try:
        logger.info("Testing S3 connection...")
        
        # Test bucket access
        response = s3_service.client.list_objects_v2(
            Bucket=s3_service._bucket, 
            MaxKeys=1
        )
        logger.success(f"✅ S3 connection successful! Bucket: {s3_service._bucket}")
        
        # Test presigned URL generation
        test_key = "test/connection-test.txt"
        presigned_url = s3_service.generate_presigned_url(test_key, expires_in=300)
        logger.success(f"✅ Presigned URL generation working: {presigned_url[:50]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ S3 connection failed: {e}")
        return False

def test_bedrock_connection():
    """Test Bedrock connection and model access."""
    try:
        logger.info("Testing Bedrock connection...")
        
        # Test model listing
        response = bedrock_service.client.list_foundation_models()
        models = response.get('modelSummaries', [])
        
        # Find our target model
        target_model = None
        for model in models:
            if model['modelId'] == bedrock_service._model_id:
                target_model = model
                break
        
        if target_model:
            logger.success(f"✅ Bedrock connection successful! Model: {target_model['modelId']}")
            logger.info(f"   Model name: {target_model.get('modelName', 'N/A')}")
            logger.info(f"   Provider: {target_model.get('providerName', 'N/A')}")
            return True
        else:
            logger.warning(f"⚠️  Target model {bedrock_service._model_id} not found in available models")
            logger.info("Available models:")
            for model in models[:5]:  # Show first 5 models
                logger.info(f"   - {model['modelId']}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Bedrock connection failed: {e}")
        return False

def test_environment_config():
    """Test environment configuration."""
    try:
        logger.info("Testing environment configuration...")
        settings = get_settings()
        
        required_vars = [
            'aws_region',
            'bedrock_model_id', 
            's3_bucket'
        ]
        
        for var in required_vars:
            value = getattr(settings, var, None)
            if value:
                logger.success(f"✅ {var}: {value}")
            else:
                logger.error(f"❌ {var}: Not set")
                return False
        
        # Check for credentials
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            logger.success("✅ AWS credentials configured")
        else:
            logger.warning("⚠️  AWS credentials not set - using IAM role (OK for production)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    logger.info("🚀 Starting AWS Integration Tests...")
    
    # Test configuration first
    if not test_environment_config():
        logger.error("❌ Configuration test failed. Please check your .env file.")
        sys.exit(1)
    
    # Test S3
    s3_ok = test_s3_connection()
    
    # Test Bedrock
    bedrock_ok = test_bedrock_connection()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("📊 INTEGRATION TEST RESULTS")
    logger.info("="*50)
    
    if s3_ok and bedrock_ok:
        logger.success("🎉 All tests passed! Your AWS integration is ready.")
        logger.info("You can now start your backend server.")
    else:
        logger.error("❌ Some tests failed. Please fix the issues above.")
        if not s3_ok:
            logger.error("   - Check S3 bucket name and permissions")
        if not bedrock_ok:
            logger.error("   - Check Bedrock model access and region")
        sys.exit(1)

if __name__ == "__main__":
    main() 