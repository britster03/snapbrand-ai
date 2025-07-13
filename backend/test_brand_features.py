#!/usr/bin/env python3

import sys
sys.path.append('.')
from app.main import app
from fastapi.testclient import TestClient
import json

client = TestClient(app)

def get_auth_headers():
    """Get authentication headers for testing"""
    # First register/login to get token
    try:
        # Try to register first
        response = client.post('/v1/auth/register', json={
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'full_name': 'Test User'
        })
        if response.status_code == 200:
            print("✓ User registered successfully")
        elif response.status_code == 400:
            print("✓ User already exists")
        else:
            print(f"Registration failed: {response.text}")
            
        # Now login with seeded user
        response = client.post('/v1/auth/login', data={
            'username': 'test@imagifyy.ai',
            'password': 'password123'
        })
        if response.status_code == 200:
            token = response.json()['access_token']
            print(f"✓ Login successful, token: {token[:20]}...")
            return {'Authorization': f'Bearer {token}'}
        else:
            print(f"Login failed: {response.text}")
            
    except Exception as e:
        print(f'Auth error: {e}')
    
    return {}

def test_brand_intelligence_generation():
    """Test brand intelligence image generation"""
    headers = get_auth_headers()
    
    print('=== TEST 1: Brand Intelligence Image Generation (null negative_prompt) ===')
    try:
        response = client.post('/v1/generate', json={
            'prompt': 'A modern logo for a tech startup',
            'negative_prompt': None,
            'width': 512,
            'height': 512,
            'num_inference_steps': 20,
            'guidance_scale': 7.5,
            'num_images': 1,
            'brand_profile_id': 1
        }, headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code not in [200, 201]:
            print(f'Error: {response.text}')
        else:
            print('✓ Brand intelligent generation with null negative_prompt working')
    except Exception as e:
        print(f'Error: {e}')

    print('\n=== TEST 2: Brand Intelligence with negative prompt ===')
    try:
        response = client.post('/v1/generate', json={
            'prompt': 'A professional business card design',
            'negative_prompt': 'blurry, low quality, pixelated',
            'width': 512,
            'height': 512,
            'num_inference_steps': 20,
            'guidance_scale': 7.5,
            'num_images': 1,
            'brand_profile_id': 1
        }, headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code not in [200, 201]:
            print(f'Error: {response.text}')
        else:
            print('✓ Brand intelligent generation with negative prompt working')
    except Exception as e:
        print(f'Error: {e}')

def test_collaboration_endpoints():
    """Test collaboration endpoints"""
    headers = get_auth_headers()
    
    print('\n=== TEST 3: Team Member Listing ===')
    try:
        response = client.get('/collaboration/team/1', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code != 200:
            print(f'Error: {response.text}')
        else:
            print('✓ Team member listing working')
    except Exception as e:
        print(f'Error: {e}')

    print('\n=== TEST 4: Pending Approvals ===')
    try:
        response = client.get('/collaboration/approval/pending', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code != 200:
            print(f'Error: {response.text}')
        else:
            print('✓ Pending approvals working')
    except Exception as e:
        print(f'Error: {e}')

def test_brand_features():
    """Test brand profile features"""
    headers = get_auth_headers()
    
    # First create a brand profile for testing
    print('\n=== SETUP: Creating Brand Profile ===')
    try:
        brand_data = {
            "name": "Test Brand",
            "description": "A test brand for testing purposes",
            "industry": "technology",
            "brand_values": ["innovation", "quality", "trust"],
            "target_audience": {"age": "25-45", "interests": ["technology", "innovation"]},
            "competitors": ["Apple", "Google"],
            "unique_selling_points": ["AI-powered", "User-friendly", "Secure"],
            "primary_colors": ["#FF0000", "#00FF00"],
            "secondary_colors": ["#0000FF", "#FFFF00"],
            "font_families": {"primary": "Arial", "secondary": "Helvetica"},
            "logo_style": "modern",
            "visual_style": "minimalist",
            "preferred_image_styles": ["clean", "modern"],
            "avoided_elements": ["clutter", "dark themes"],
            "brand_keywords": ["innovation", "technology", "future"]
        }
        
        response = client.post('/brands/profiles', json=brand_data, headers=headers)
        print(f'Brand creation status: {response.status_code}')
        if response.status_code in [200, 201]:
            brand_id = response.json()['id']
            print(f'✓ Brand profile created with ID: {brand_id}')
        else:
            print(f'Brand creation failed: {response.text}')
            brand_id = 1  # Fall back to assuming brand ID 1 exists
    except Exception as e:
        print(f'Error creating brand: {e}')
        brand_id = 1  # Fall back to assuming brand ID 1 exists
    
    print('\n=== TEST 5: Brand Analytics ===')
    try:
        response = client.get(f'/analytics/brand/{brand_id}', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code != 200:
            print(f'Error: {response.text}')
        else:
            print('✓ Brand analytics working')
    except Exception as e:
        print(f'Error: {e}')

    print('\n=== TEST 6: Brand Asset Analysis ===')
    try:
        response = client.get(f'/brands/profiles/{brand_id}/assets', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code != 200:
            print(f'Error: {response.text}')
        else:
            print('✓ Brand asset analysis working')
    except Exception as e:
        print(f'Error: {e}')

    print('\n=== TEST 7: Brand Insights ===')
    try:
        response = client.get(f'/brands/profiles/{brand_id}/insights', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code != 200:
            print(f'Error: {response.text}')
        else:
            print('✓ Brand insights working')
    except Exception as e:
        print(f'Error: {e}')

    print('\n=== TEST 8: Campaign Management ===')
    try:
        response = client.get(f'/brands/profiles/{brand_id}/campaigns', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code != 200:
            print(f'Error: {response.text}')
        else:
            print('✓ Campaign management working')
    except Exception as e:
        print(f'Error: {e}')

    print('\n=== TEST 9: Brand Consistency Validation ===')
    try:
        # Test brand consistency validation with query parameter
        image_url = "https://example.com/test-image.jpg"
        response = client.post(f'/brands/profiles/{brand_id}/analyze-consistency?image_url={image_url}', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code != 200:
            print(f'Error: {response.text}')
        else:
            print('✓ Brand consistency validation working')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    print("=== COMPREHENSIVE BRAND INTELLIGENCE TESTING ===")
    test_brand_intelligence_generation()
    test_collaboration_endpoints()
    test_brand_features()
    print("\n=== ALL TESTS COMPLETE ===")