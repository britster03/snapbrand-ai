#!/usr/bin/env python3
"""Test script for vector generation debugging."""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.vector_engine import vector_engine
from app.core.config import get_settings

async def test_vector_generation():
    """Test vector generation with debug output."""
    print("=== Vector Generation Test ===")
    
    # Print configuration
    settings = get_settings()
    print(f"Vector Engine Enabled: {settings.vector_engine_enabled}")
    print(f"Vector Engine Model ID: {settings.vector_engine_model_id}")
    print(f"AWS Region: {settings.aws_region}")
    
    # Test prompt
    prompt = "a cup of coffee"
    style = "minimalist"
    
    print(f"\nTesting prompt: '{prompt}' with style: '{style}'")
    
    try:
        # Generate vector
        vectors = vector_engine.generate_vectors(
            prompt=prompt,
            style=style,
            num_images=1,
            size="512x512"
        )
        
        print(f"\nGenerated {len(vectors)} vectors")
        for i, vector in enumerate(vectors):
            print(f"Vector {i+1}: {len(vector)} characters")
            # Check if it's AI-generated or placeholder
            if "AI-generated" in vector or "data:image/png;base64," in vector:
                print(f"  -> AI-generated SVG with embedded image")
            elif "Generated shapes based on prompt" in vector:
                print(f"  -> Placeholder SVG")
            else:
                print(f"  -> Unknown SVG type")
        
        # Save first vector for inspection
        if vectors:
            with open("test_vector_output.svg", "w") as f:
                f.write(vectors[0])
            print(f"\nSaved first vector to: test_vector_output.svg")
        
    except Exception as e:
        print(f"\nError generating vectors: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_vector_generation()) 