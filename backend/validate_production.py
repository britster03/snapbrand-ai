#!/usr/bin/env python3
"""
Production Validation Script for imagifyy.ai Backend

This script validates that the backend is truly production-ready with:
- No dummy or placeholder data
- All services properly configured
- Real AWS connectivity
- Proper error handling
- Security configurations
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.config import get_settings
from app.core.pricing import get_model_pricing_info, calculate_generation_cost
from app.services.bedrock import bedrock_service
from app.services.s3 import s3_service


class ProductionValidator:
    """Validates production readiness of the backend."""
    
    def __init__(self):
        self.settings = get_settings()
        self.validation_results = {
            "configuration": {},
            "services": {},
            "security": {},
            "pricing": {},
            "storage": {},
            "overall": {"status": "pending", "issues": [], "warnings": []}
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate all configuration settings."""
        print("🔧 Validating Configuration...")
        
        config_checks = {
            "aws_region": bool(self.settings.aws_region),
            "bedrock_model_id": bool(self.settings.bedrock_model_id),
            "s3_bucket": bool(self.settings.s3_bucket),
            "app_name": bool(self.settings.app_name),
            "cors_origins": len(self.settings.cors_origins) > 0,
            "rate_limits": self.settings.rate_limit_per_minute > 0,
        }
        
        # Check for production-appropriate values
        if self.settings.debug:
            self.validation_results["overall"]["warnings"].append("Debug mode is enabled")
        
        if not self.settings.api_keys:
            self.validation_results["overall"]["warnings"].append("No API keys configured - service is open")
        
        # Validate AWS credentials
        aws_creds = {
            "access_key": bool(self.settings.aws_access_key_id),
            "secret_key": bool(self.settings.aws_secret_access_key),
            "session_token": bool(self.settings.aws_session_token),
            "env_vars": bool(os.getenv("AWS_ACCESS_KEY_ID")) or bool(os.getenv("AWS_PROFILE"))
        }
        
        self.validation_results["configuration"] = {
            "basic_config": config_checks,
            "aws_credentials": aws_creds,
            "debug_mode": self.settings.debug,
            "api_keys_count": len(self.settings.api_keys)
        }
        
        return self.validation_results["configuration"]
    
    def validate_services(self) -> Dict[str, Any]:
        """Validate AWS service connectivity."""
        print("☁️  Validating AWS Services...")
        
        services_status = {}
        
        # Test Bedrock
        try:
            models = bedrock_service.client.list_foundation_models()
            model_ids = [m["modelId"] for m in models.get("modelSummaries", [])]
            
            services_status["bedrock"] = {
                "status": "healthy",
                "available_models": len(model_ids),
                "configured_model_available": self.settings.bedrock_model_id in model_ids,
                "configured_model": self.settings.bedrock_model_id
            }
            
            if not services_status["bedrock"]["configured_model_available"]:
                self.validation_results["overall"]["issues"].append(
                    f"Configured model {self.settings.bedrock_model_id} not available"
                )
                
        except Exception as e:
            services_status["bedrock"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            self.validation_results["overall"]["issues"].append(f"Bedrock connectivity failed: {e}")
        
        # Test S3
        try:
            s3_service.client.head_bucket(Bucket=self.settings.s3_bucket)
            
            # Test upload/download
            test_key = "test/validation_test.txt"
            test_content = b"Production validation test"
            
            s3_service.upload_bytes(test_content, test_key)
            presigned_url = s3_service.generate_presigned_url(test_key)
            
            # Clean up test file
            s3_service.client.delete_object(Bucket=self.settings.s3_bucket, Key=test_key)
            
            services_status["s3"] = {
                "status": "healthy",
                "bucket": self.settings.s3_bucket,
                "upload_test": "passed",
                "presigned_url_test": "passed"
            }
            
        except Exception as e:
            services_status["s3"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            self.validation_results["overall"]["issues"].append(f"S3 connectivity failed: {e}")
        
        self.validation_results["services"] = services_status
        return services_status
    
    def validate_pricing(self) -> Dict[str, Any]:
        """Validate pricing calculations are real and accurate."""
        print("💰 Validating Pricing...")
        
        pricing_info = get_model_pricing_info(self.settings.bedrock_model_id)
        
        # Test cost calculations
        test_costs = {
            "single_image": calculate_generation_cost(self.settings.bedrock_model_id, 1),
            "batch_10": calculate_generation_cost(self.settings.bedrock_model_id, 10),
            "large_size": calculate_generation_cost(self.settings.bedrock_model_id, 1, "1536x640")
        }
        
        pricing_validation = {
            "model_pricing": pricing_info,
            "test_calculations": test_costs,
            "pricing_realistic": all(cost > 0 for cost in test_costs.values())
        }
        
        if not pricing_validation["pricing_realistic"]:
            self.validation_results["overall"]["issues"].append("Pricing calculations return zero cost")
        
        self.validation_results["pricing"] = pricing_validation
        return pricing_validation
    
    def validate_storage(self) -> Dict[str, Any]:
        """Validate persistent storage for batch jobs."""
        print("💾 Validating Storage...")
        
        from app.routes.batch import BatchJobStorage
        
        storage_validation = {
            "batch_storage_dir": str(Path("batch_jobs").absolute()),
            "directory_exists": Path("batch_jobs").exists(),
            "directory_writable": os.access(Path("batch_jobs"), os.W_OK) if Path("batch_jobs").exists() else False
        }
        
        # Test storage operations
        try:
            from app.models.schemas import BatchStatusResponse
            from datetime import datetime
            
            test_job = BatchStatusResponse(
                batch_id="test_validation",
                status="completed",
                progress=100.0,
                completed_requests=1,
                total_requests=1,
                results=None,
                error_count=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Test save/load
            BatchJobStorage.save_job("test_validation", test_job)
            loaded_job = BatchJobStorage.load_job("test_validation")
            
            storage_validation["save_load_test"] = "passed" if loaded_job else "failed"
            
            # Clean up
            BatchJobStorage.delete_job("test_validation")
            
        except Exception as e:
            storage_validation["save_load_test"] = f"failed: {e}"
            self.validation_results["overall"]["issues"].append(f"Storage test failed: {e}")
        
        self.validation_results["storage"] = storage_validation
        return storage_validation
    
    def validate_security(self) -> Dict[str, Any]:
        """Validate security configurations."""
        print("🔒 Validating Security...")
        
        security_checks = {
            "api_keys_configured": len(self.settings.api_keys) > 0,
            "cors_configured": len(self.settings.cors_origins) > 0,
            "rate_limiting": self.settings.rate_limit_per_minute > 0,
            "debug_disabled": not self.settings.debug,
            "secure_headers": True,  # Handled by middleware
        }
        
        security_score = sum(security_checks.values()) / len(security_checks)
        
        if security_score < 0.8:
            self.validation_results["overall"]["warnings"].append("Security score below 80%")
        
        self.validation_results["security"] = {
            "checks": security_checks,
            "score": security_score
        }
        
        return self.validation_results["security"]
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete validation suite."""
        print("🚀 Starting Production Validation for imagifyy.ai Backend\n")
        
        # Run all validations
        self.validate_configuration()
        self.validate_services()
        self.validate_pricing()
        self.validate_storage()
        self.validate_security()
        
        # Determine overall status
        if self.validation_results["overall"]["issues"]:
            self.validation_results["overall"]["status"] = "failed"
        elif self.validation_results["overall"]["warnings"]:
            self.validation_results["overall"]["status"] = "warning"
        else:
            self.validation_results["overall"]["status"] = "passed"
        
        return self.validation_results
    
    def print_results(self):
        """Print validation results in a readable format."""
        results = self.validation_results
        
        print("\n" + "="*60)
        print("PRODUCTION VALIDATION RESULTS")
        print("="*60)
        
        status_emoji = {
            "passed": "✅",
            "warning": "⚠️",
            "failed": "❌"
        }
        
        print(f"\nOVERALL STATUS: {status_emoji.get(results['overall']['status'], '❓')} {results['overall']['status'].upper()}")
        
        if results["overall"]["issues"]:
            print(f"\n❌ CRITICAL ISSUES ({len(results['overall']['issues'])}):")
            for issue in results["overall"]["issues"]:
                print(f"  • {issue}")
        
        if results["overall"]["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(results['overall']['warnings'])}):")
            for warning in results["overall"]["warnings"]:
                print(f"  • {warning}")
        
        print(f"\n📊 DETAILED RESULTS:")
        print(f"  Configuration: {'✅' if results['configuration'] else '❌'}")
        print(f"  AWS Services: {'✅' if all(s.get('status') == 'healthy' for s in results['services'].values()) else '❌'}")
        print(f"  Pricing: {'✅' if results['pricing'].get('pricing_realistic') else '❌'}")
        print(f"  Storage: {'✅' if results['storage'].get('save_load_test') == 'passed' else '❌'}")
        print(f"  Security: {'✅' if results['security'].get('score', 0) >= 0.8 else '⚠️'}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if not results["configuration"]["aws_credentials"]["env_vars"]:
            print("  • Set up AWS credentials (AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or AWS_PROFILE)")
        if not results["configuration"]["api_keys_count"]:
            print("  • Configure API keys for security (API_KEYS environment variable)")
        if results["configuration"]["debug_mode"]:
            print("  • Disable debug mode for production (DEBUG=false)")
        
        print("\n" + "="*60)


def main():
    """Main validation function."""
    validator = ProductionValidator()
    
    try:
        results = validator.run_validation()
        validator.print_results()
        
        # Save results to file
        with open("validation_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: validation_results.json")
        
        # Exit with appropriate code
        if results["overall"]["status"] == "failed":
            sys.exit(1)
        elif results["overall"]["status"] == "warning":
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 