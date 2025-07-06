from __future__ import annotations

import json
import base64
import subprocess
import tempfile
import os
from typing import Any, Dict, List, Optional
from loguru import logger
from PIL import Image
import io

from ..core.config import get_settings
from .bedrock_enhanced import EnhancedBedrockService


class VectorBedrockService(EnhancedBedrockService):
    """Custom Bedrock service for vector generation that uses vector_engine_model_id."""
    
    def __init__(self) -> None:
        # Initialize parent class
        super().__init__()
        # Override model ID to use vector engine model
        settings = get_settings()
        self._model_id = settings.vector_engine_model_id
        logger.info(f"VectorBedrockService initialized with model: {self._model_id}")


class VectorEngine:
    """Service for generating vector images from text prompts."""

    def __init__(self) -> None:
        self.settings = get_settings()
        # Always enable AI generation if we have a valid model ID
        self.use_ai_generation = (
            self.settings.vector_engine_enabled and 
            self.settings.vector_engine_model_id and 
            self.settings.vector_engine_model_id != "placeholder"
        )
        
        # Create custom bedrock service for vector generation
        if self.use_ai_generation:
            self.bedrock_service = VectorBedrockService()
        
        logger.info(f"VectorEngine initialization:")
        logger.info(f"  - vector_engine_enabled: {self.settings.vector_engine_enabled}")
        logger.info(f"  - vector_engine_model_id: {self.settings.vector_engine_model_id}")
        logger.info(f"  - use_ai_generation: {self.use_ai_generation}")
        
        if self.use_ai_generation:
            logger.info("VectorEngine initialized with AI-powered generation using Bedrock + vector conversion")
        else:
            logger.warning("VectorEngine initialized with placeholder implementation (check VECTOR_ENGINE_MODEL_ID configuration)")

    def _create_placeholder_svg(
        self,
        prompt: str,
        size: str = "512x512",
        style: str = "modern",
        seed: Optional[int] = None
    ) -> str:
        """Create a placeholder SVG based on the prompt."""
        width, height = map(int, size.split("x"))
        
        # Generate a simple SVG based on prompt keywords
        colors = self._extract_colors_from_prompt(prompt)
        shapes = self._extract_shapes_from_prompt(prompt)
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{colors[0]};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{colors[1]};stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="url(#grad1)" />
    
    <!-- Generated shapes based on prompt -->
    {self._generate_shapes(shapes, width, height, colors)}
    
    <!-- Prompt text -->
    <text x="{width//2}" y="{height-30}" text-anchor="middle" 
          font-family="Arial, sans-serif" font-size="14" fill="#333" opacity="0.7">
        {prompt[:50]}{'...' if len(prompt) > 50 else ''}
    </text>
</svg>'''
        
        return svg_content

    def _extract_colors_from_prompt(self, prompt: str) -> List[str]:
        """Extract color scheme from prompt."""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['blue', 'ocean', 'sky', 'water']):
            return ['#3B82F6', '#1E40AF']
        elif any(word in prompt_lower for word in ['red', 'fire', 'passion', 'love']):
            return ['#EF4444', '#DC2626']
        elif any(word in prompt_lower for word in ['green', 'nature', 'forest', 'plant']):
            return ['#10B981', '#059669']
        elif any(word in prompt_lower for word in ['purple', 'magic', 'mystery']):
            return ['#8B5CF6', '#7C3AED']
        elif any(word in prompt_lower for word in ['orange', 'sunset', 'warm']):
            return ['#F59E0B', '#D97706']
        else:
            return ['#6B7280', '#4B5563']  # Default gray

    def _extract_shapes_from_prompt(self, prompt: str) -> List[str]:
        """Extract shape types from prompt."""
        prompt_lower = prompt.lower()
        shapes = []
        
        if any(word in prompt_lower for word in ['circle', 'round', 'ball', 'sun']):
            shapes.append('circle')
        if any(word in prompt_lower for word in ['square', 'box', 'cube']):
            shapes.append('square')
        if any(word in prompt_lower for word in ['triangle', 'arrow', 'mountain']):
            shapes.append('triangle')
        if any(word in prompt_lower for word in ['star', 'sparkle']):
            shapes.append('star')
        if any(word in prompt_lower for word in ['wave', 'water', 'flow']):
            shapes.append('wave')
            
        return shapes if shapes else ['circle']  # Default to circle

    def _generate_shapes(self, shapes: List[str], width: int, height: int, colors: List[str]) -> str:
        """Generate SVG shapes based on extracted shape types."""
        svg_shapes = []
        
        for i, shape in enumerate(shapes[:3]):  # Limit to 3 shapes
            color = colors[i % len(colors)]
            x = (width // (len(shapes) + 1)) * (i + 1)
            y = height // 2
            
            if shape == 'circle':
                svg_shapes.append(f'<circle cx="{x}" cy="{y}" r="{min(width, height)//8}" fill="{color}" opacity="0.8" />')
            elif shape == 'square':
                size = min(width, height) // 6
                svg_shapes.append(f'<rect x="{x-size//2}" y="{y-size//2}" width="{size}" height="{size}" fill="{color}" opacity="0.8" />')
            elif shape == 'triangle':
                size = min(width, height) // 6
                points = f"{x},{y-size//2} {x-size//2},{y+size//2} {x+size//2},{y+size//2}"
                svg_shapes.append(f'<polygon points="{points}" fill="{color}" opacity="0.8" />')
            elif shape == 'star':
                svg_shapes.append(self._create_star(x, y, min(width, height)//8, color))
            elif shape == 'wave':
                svg_shapes.append(self._create_wave(x, y, width//4, color))
                
        return '\n    '.join(svg_shapes)

    def _create_star(self, cx: int, cy: int, r: int, color: str) -> str:
        """Create a star shape."""
        points = []
        for i in range(10):
            angle = (i * 36 - 90) * 3.14159 / 180
            radius = r if i % 2 == 0 else r // 2
            x = cx + radius * (angle.__cos__() if hasattr(angle, '__cos__') else 1)
            y = cy + radius * (angle.__sin__() if hasattr(angle, '__sin__') else 0)
            points.append(f"{x:.1f},{y:.1f}")
        
        return f'<polygon points="{" ".join(points)}" fill="{color}" opacity="0.8" />'

    def _create_wave(self, x: int, y: int, width: int, color: str) -> str:
        """Create a wave shape."""
        path = f"M {x-width//2} {y} Q {x-width//4} {y-20} {x} {y} Q {x+width//4} {y+20} {x+width//2} {y}"
        return f'<path d="{path}" stroke="{color}" stroke-width="3" fill="none" opacity="0.8" />'

    def _enhance_prompt_for_vector(self, prompt: str, style: str) -> str:
        """Enhance prompt for Titan V2 vector illustration generation."""
        # Titan V2 works better with clear, descriptive prompts
        base_vector_style = "vector illustration style, flat design, clean simple artwork, solid colors, minimal details, icon-like design"
        
        style_enhancements = {
            "modern": "modern minimalist design, corporate branding style, geometric shapes",
            "minimalist": "ultra simple design, basic shapes, limited color palette, clean lines",
            "artistic": "creative illustration style, stylized artwork, artistic interpretation",
            "geometric": "geometric vector design, angular patterns, abstract shapes",
            "organic": "organic curved shapes, natural forms, flowing design elements"
        }
        
        style_specific = style_enhancements.get(style, "clean vector design")
        
        # Titan V2 responds well to structured prompts
        enhanced_prompt = f"{prompt} as a {base_vector_style}, {style_specific}, digital illustration, vector art"
        
        return enhanced_prompt

    def _convert_image_to_vector(self, image_bytes: bytes, style: str = "modern") -> str:
        """Convert raster image to SVG vector format using image tracing."""
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_input:
                temp_input.write(image_bytes)
                temp_input_path = temp_input.name
            
            temp_output_path = temp_input_path.replace('.png', '.svg')
            
            try:
                # Try using potrace for vector tracing (if available)
                # This is a common tool for converting bitmaps to vectors
                subprocess.run([
                    'potrace', 
                    temp_input_path, 
                    '-s',  # SVG output
                    '-o', temp_output_path,
                    '--tight'  # Tight bounding box
                ], check=True, capture_output=True)
                
                # Read the generated SVG
                with open(temp_output_path, 'r') as f:
                    svg_content = f.read()
                
                logger.info("Successfully converted image to vector using potrace")
                return svg_content
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback: Create SVG with embedded image
                logger.warning("potrace not available, creating SVG with embedded raster image")
                
                # Convert image to base64
                b64_image = base64.b64encode(image_bytes).decode('utf-8')
                
                # Get image dimensions
                img = Image.open(io.BytesIO(image_bytes))
                width, height = img.size
                
                # Create SVG with embedded image
                svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <image x="0" y="0" width="{width}" height="{height}" xlink:href="data:image/png;base64,{b64_image}" />
</svg>'''
                return svg_content
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(temp_input_path)
                    if os.path.exists(temp_output_path):
                        os.unlink(temp_output_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error converting image to vector: {e}")
            # Return a simple placeholder SVG
            return self._create_placeholder_svg("Error converting image", "512x512", style)

    def generate_vectors(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        size: str = "512x512",
        style: str = "modern",
        seed: Optional[int] = None,
        **kwargs: Any,
    ) -> List[str]:
        """
        Generate vector images and return them as SVG strings.
        
        Args:
            prompt: Text description of the desired image
            negative_prompt: What to avoid in the image
            num_images: Number of images to generate
            size: Image dimensions (e.g., "512x512")
            style: Style preset
            seed: Random seed for reproducibility
            **kwargs: Additional parameters
            
        Returns:
            List of SVG strings
        """
        logger.info(f"Generating {num_images} vector images for prompt: '{prompt}' with style: '{style}'")
        logger.info(f"AI generation enabled: {self.use_ai_generation}")
        
        if self.use_ai_generation:
            try:
                # Use Bedrock to generate raster images first
                enhanced_prompt = self._enhance_prompt_for_vector(prompt, style)
                
                logger.info(f"Enhanced prompt: {enhanced_prompt}")
                
                # Enhanced negative prompt optimized for Titan V2
                enhanced_negative_prompt = negative_prompt or ""
                if enhanced_negative_prompt:
                    enhanced_negative_prompt += ", "
                # Titan V2 specific negative prompts for better vector results
                enhanced_negative_prompt += "photorealistic, realistic photo, 3D render, complex textures, detailed shading, gradients, shadows, depth, perspective, noise, grain, blurry, low quality, distorted, watermark, text, signature"
                
                logger.info(f"Enhanced negative prompt: {enhanced_negative_prompt}")
                
                # Generate raster images using Bedrock with Titan V2 optimized settings
                vector_kwargs = kwargs.copy()
                vector_kwargs.update({
                    'guidance_scale': 8.0,  # Optimal for Titan V2 (7-10 range)
                    'quality': 'premium',   # Use premium quality for better vector conversion
                })
                
                logger.info(f"Calling Bedrock with model: {self.settings.vector_engine_model_id}")
                
                raster_images = self.bedrock_service.generate_images(
                    prompt=enhanced_prompt,
                    negative_prompt=enhanced_negative_prompt,
                    num_images=num_images,
                    size=size,
                    seed=seed,
                    **vector_kwargs
                )
                
                logger.info(f"Bedrock returned {len(raster_images)} images")
                
                # Convert each raster image to vector
                vectors = []
                for i, image_bytes in enumerate(raster_images):
                    logger.info(f"Converting raster image {i+1} to vector format (size: {len(image_bytes)} bytes)")
                    svg_content = self._convert_image_to_vector(image_bytes, style)
                    vectors.append(svg_content)
                
                logger.info(f"Successfully generated {len(vectors)} AI-powered vector images")
                return vectors
                
            except Exception as e:
                logger.error(f"AI vector generation failed with error: {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Don't fall back to placeholder - raise the error so we can debug
                raise e
        else:
            logger.warning("AI generation disabled, using placeholder implementation")
        
        # Placeholder implementation (existing code)
        vectors = []
        for i in range(num_images):
            current_seed = (seed + i) if seed else None
            svg_content = self._create_placeholder_svg(
                prompt=prompt,
                size=size,
                style=style,
                seed=current_seed
            )
            vectors.append(svg_content)
            
        logger.info(f"Generated {len(vectors)} placeholder vector images")
        return vectors

    def generate_vectors_base64(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        **kwargs: Any,
    ) -> List[str]:
        """Generate vector images and return them as base64 encoded strings."""
        svg_strings = self.generate_vectors(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_images=num_images,
            **kwargs
        )
        
        base64_vectors = []
        for svg in svg_strings:
            svg_bytes = svg.encode('utf-8')
            b64_string = base64.b64encode(svg_bytes).decode('utf-8')
            base64_vectors.append(b64_string)
            
        return base64_vectors


# Create service instance
vector_engine = VectorEngine() 