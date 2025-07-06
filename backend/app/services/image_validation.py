"""
Image quality validation service for professional standards.
Validates generated images against quality metrics and industry standards.
"""

import io
import base64
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageStat
from loguru import logger

class ImageQualityValidator:
    """Service for validating image quality against professional standards."""
    
    def __init__(self):
        self.quality_thresholds = {
            "standard": {
                "min_resolution": 256,
                "min_sharpness": 0.3,
                "min_contrast": 0.2,
                "max_noise": 0.8
            },
            "high": {
                "min_resolution": 512,
                "min_sharpness": 0.5,
                "min_contrast": 0.3,
                "max_noise": 0.6
            },
            "ultra": {
                "min_resolution": 768,
                "min_sharpness": 0.7,
                "min_contrast": 0.4,
                "max_noise": 0.4
            },
            "professional": {
                "min_resolution": 1024,
                "min_sharpness": 0.8,
                "min_contrast": 0.5,
                "max_noise": 0.3
            }
        }
    
    def validate_image_quality(
        self, 
        image_bytes: bytes, 
        expected_quality: str = "high",
        expected_size: Optional[Tuple[int, int]] = None
    ) -> Dict[str, Any]:
        """
        Validate image quality against professional standards.
        
        Args:
            image_bytes: Raw image bytes
            expected_quality: Expected quality level
            expected_size: Expected image dimensions
            
        Returns:
            Dictionary with validation results and metrics
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Get quality thresholds
            thresholds = self.quality_thresholds.get(expected_quality, self.quality_thresholds["high"])
            
            # Perform quality checks
            validation_results = {
                "is_valid": True,
                "quality_score": 0.0,
                "issues": [],
                "metrics": {},
                "recommendations": []
            }
            
            # Check resolution
            width, height = image.size
            min_dimension = min(width, height)
            validation_results["metrics"]["resolution"] = {"width": width, "height": height}
            
            if min_dimension < thresholds["min_resolution"]:
                validation_results["is_valid"] = False
                validation_results["issues"].append(f"Resolution too low: {min_dimension}px < {thresholds['min_resolution']}px")
                validation_results["recommendations"].append("Increase image size for better quality")
            
            # Check expected size if provided
            if expected_size:
                expected_width, expected_height = expected_size
                if abs(width - expected_width) > 10 or abs(height - expected_height) > 10:
                    validation_results["issues"].append(f"Size mismatch: got {width}x{height}, expected {expected_width}x{expected_height}")
            
            # Calculate image statistics
            stats = ImageStat.Stat(image)
            
            # Check sharpness (using variance as proxy)
            if image.mode == 'RGB':
                # Convert to grayscale for sharpness calculation
                gray_image = image.convert('L')
                sharpness = self._calculate_sharpness(gray_image)
                validation_results["metrics"]["sharpness"] = sharpness
                
                if sharpness < thresholds["min_sharpness"]:
                    validation_results["is_valid"] = False
                    validation_results["issues"].append(f"Image too blurry: sharpness {sharpness:.2f} < {thresholds['min_sharpness']}")
                    validation_results["recommendations"].append("Increase guidance scale or use higher quality settings")
            
            # Check contrast
            if image.mode == 'RGB':
                contrast = self._calculate_contrast(image)
                validation_results["metrics"]["contrast"] = contrast
                
                if contrast < thresholds["min_contrast"]:
                    validation_results["issues"].append(f"Low contrast: {contrast:.2f} < {thresholds['min_contrast']}")
                    validation_results["recommendations"].append("Adjust lighting or use dramatic lighting preset")
            
            # Check for noise/artifacts
            noise_level = self._estimate_noise_level(image)
            validation_results["metrics"]["noise_level"] = noise_level
            
            if noise_level > thresholds["max_noise"]:
                validation_results["issues"].append(f"High noise level: {noise_level:.2f} > {thresholds['max_noise']}")
                validation_results["recommendations"].append("Use professional quality setting or reduce guidance scale")
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(validation_results["metrics"], thresholds)
            validation_results["quality_score"] = quality_score
            
            # Professional quality assessment
            if expected_quality == "professional":
                professional_issues = self._check_professional_standards(image, validation_results["metrics"])
                validation_results["issues"].extend(professional_issues)
                if professional_issues:
                    validation_results["is_valid"] = False
            
            logger.info(f"Image quality validation: score={quality_score:.2f}, valid={validation_results['is_valid']}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Image quality validation failed: {e}")
            return {
                "is_valid": False,
                "quality_score": 0.0,
                "issues": [f"Validation error: {str(e)}"],
                "metrics": {},
                "recommendations": ["Retry generation with different parameters"]
            }
    
    def _calculate_sharpness(self, gray_image: Image.Image) -> float:
        """Calculate image sharpness using Laplacian variance."""
        try:
            import numpy as np
            from scipy import ndimage
            
            # Convert PIL image to numpy array
            img_array = np.array(gray_image)
            
            # Apply Laplacian filter
            laplacian = ndimage.laplace(img_array)
            
            # Calculate variance (higher = sharper)
            variance = np.var(laplacian)
            
            # Normalize to 0-1 range
            return min(variance / 10000, 1.0)
            
        except ImportError:
            # Fallback method using PIL
            # Simple edge detection using filter
            from PIL import ImageFilter
            edges = gray_image.filter(ImageFilter.FIND_EDGES)
            stat = ImageStat.Stat(edges)
            return min(stat.var[0] / 10000, 1.0)
    
    def _calculate_contrast(self, image: Image.Image) -> float:
        """Calculate image contrast using standard deviation."""
        try:
            # Convert to grayscale
            gray_image = image.convert('L')
            stat = ImageStat.Stat(gray_image)
            
            # Use standard deviation as contrast measure
            contrast = stat.stddev[0] / 255.0
            return contrast
            
        except Exception:
            return 0.0
    
    def _estimate_noise_level(self, image: Image.Image) -> float:
        """Estimate noise level in the image."""
        try:
            import numpy as np
            from scipy import ndimage
            
            # Convert to grayscale numpy array
            gray_image = image.convert('L')
            img_array = np.array(gray_image)
            
            # Use high-pass filter to estimate noise
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            filtered = ndimage.convolve(img_array, kernel)
            
            # Calculate noise as standard deviation of filtered image
            noise = np.std(filtered) / 255.0
            return min(noise, 1.0)
            
        except ImportError:
            # Fallback: use image statistics
            stat = ImageStat.Stat(image.convert('L'))
            # Estimate noise from variance
            return min(stat.var[0] / 50000, 1.0)
    
    def _calculate_quality_score(self, metrics: Dict[str, Any], thresholds: Dict[str, float]) -> float:
        """Calculate overall quality score from metrics."""
        score = 0.0
        weights = {
            "sharpness": 0.3,
            "contrast": 0.3,
            "noise_level": 0.2,  # Lower is better
            "resolution": 0.2
        }
        
        # Sharpness score
        if "sharpness" in metrics:
            sharpness_score = min(metrics["sharpness"] / thresholds["min_sharpness"], 1.0)
            score += weights["sharpness"] * sharpness_score
        
        # Contrast score
        if "contrast" in metrics:
            contrast_score = min(metrics["contrast"] / thresholds["min_contrast"], 1.0)
            score += weights["contrast"] * contrast_score
        
        # Noise score (inverted - lower noise is better)
        if "noise_level" in metrics:
            noise_score = max(0, 1.0 - (metrics["noise_level"] / thresholds["max_noise"]))
            score += weights["noise_level"] * noise_score
        
        # Resolution score
        if "resolution" in metrics:
            min_dim = min(metrics["resolution"]["width"], metrics["resolution"]["height"])
            resolution_score = min(min_dim / thresholds["min_resolution"], 1.0)
            score += weights["resolution"] * resolution_score
        
        return score
    
    def _check_professional_standards(self, image: Image.Image, metrics: Dict[str, Any]) -> List[str]:
        """Check additional professional standards."""
        issues = []
        
        # Check for proper aspect ratios
        width, height = image.size
        aspect_ratio = width / height
        
        # Common professional aspect ratios
        professional_ratios = [
            (1.0, "Square (1:1)"),
            (1.333, "4:3"),
            (1.5, "3:2"),
            (1.618, "Golden Ratio"),
            (1.777, "16:9"),
            (2.0, "2:1")
        ]
        
        # Check if aspect ratio is close to professional standards
        is_professional_ratio = any(
            abs(aspect_ratio - ratio) < 0.1 for ratio, _ in professional_ratios
        )
        
        if not is_professional_ratio:
            issues.append(f"Non-standard aspect ratio: {aspect_ratio:.2f}")
        
        # Check minimum resolution for professional use
        if min(width, height) < 1024:
            issues.append("Resolution below professional standards (minimum 1024px)")
        
        # Check for color consistency (basic check)
        if image.mode == 'RGB':
            stat = ImageStat.Stat(image)
            # Check if colors are too saturated or too dull
            avg_saturation = sum(stat.stddev) / len(stat.stddev)
            if avg_saturation < 10:
                issues.append("Image appears too dull for professional use")
            elif avg_saturation > 100:
                issues.append("Image appears over-saturated for professional use")
        
        return issues
    
    def get_quality_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Get specific recommendations based on validation results."""
        recommendations = validation_results.get("recommendations", [])
        
        # Add general recommendations based on quality score
        quality_score = validation_results.get("quality_score", 0)
        
        if quality_score < 0.5:
            recommendations.append("Consider using higher quality settings")
            recommendations.append("Try professional or ultra quality modes")
        elif quality_score < 0.7:
            recommendations.append("Good quality - consider professional mode for critical use")
        else:
            recommendations.append("Excellent quality - suitable for professional use")
        
        return list(set(recommendations))  # Remove duplicates

# Global instance
image_validator = ImageQualityValidator() 