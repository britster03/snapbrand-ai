#!/usr/bin/env python3

import sys
sys.path.append('.')
from app.main import app
from fastapi.testclient import TestClient
import json
from datetime import datetime

client = TestClient(app)

# Test authentication flow
print("=== AUTHENTICATION DEBUG TEST ===")

# Login and get token
print("\n1. Login with test user...")
response = client.post('/v1/auth/login', data={
    'username': 'test@snapbrand.ai',
    'password': 'password123'
})

print(f"Login Status: {response.status_code}")
if response.status_code == 200:
    token_data = response.json()
    token = token_data['access_token']
    print(f"✓ Token received: {token[:50]}...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test /me endpoint
    print("\n2. Testing /me endpoint...")
    response = client.get('/v1/auth/me', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"✓ User data: {user_data['email']}")
    else:
        print(f"✗ Error: {response.text}")
    
    # Test brands endpoint
    print("\n3. Testing brands endpoint...")
    response = client.get('/brands/profiles', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        brands = response.json()
        print(f"✓ Brands: {len(brands)} profiles found")
    else:
        print(f"✗ Error: {response.text}")
    
    # Wait 2 seconds and test again
    print("\n4. Testing after 2 seconds...")
    import time
    time.sleep(2)
    
    response = client.get('/v1/auth/me', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Token still valid")
    else:
        print(f"✗ Token expired: {response.text}")
        
else:
    print(f"✗ Login failed: {response.text}")

print("\n=== DEBUG TEST COMPLETE ===")