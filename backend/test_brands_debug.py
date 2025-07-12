#!/usr/bin/env python3

import sys
sys.path.append('.')
from app.main import app
from fastapi.testclient import TestClient
import json

client = TestClient(app)

# Test the specific brands endpoint
print("=== BRANDS ENDPOINT DEBUG TEST ===")

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
    
    # Test /me endpoint first
    print("\n2. Testing /me endpoint...")
    response = client.get('/v1/auth/me', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"✓ User data: {user_data['email']}")
    else:
        print(f"✗ Error: {response.text}")
    
    # Test brands endpoint with different headers
    print("\n3. Testing brands endpoint with Authorization header...")
    response = client.get('/brands/profiles', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test with different token format
    print("\n4. Testing with different token format...")
    response = client.get('/brands/profiles', headers={'Authorization': token})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test with raw token
    print("\n5. Testing with raw token...")
    response = client.get('/brands/profiles', headers={'Authorization': f'Bearer {token}'})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Check response headers
    print("\n6. Checking response headers...")
    print(f"Response headers: {dict(response.headers)}")
        
else:
    print(f"✗ Login failed: {response.text}")

print("\n=== DEBUG TEST COMPLETE ===")