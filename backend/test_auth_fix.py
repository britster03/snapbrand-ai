#!/usr/bin/env python3

import sys
sys.path.append('.')
from app.main import app
from fastapi.testclient import TestClient
import json

client = TestClient(app)

print("=== TESTING AUTH FIX ===")

# Test 1: Login and get token
print("\n1. Login and get token...")
response = client.post('/v1/auth/login', data={
    'username': 'test@imagifyy.ai',
    'password': 'password123'
})

if response.status_code == 200:
    token = response.json()['access_token']
    print(f"✓ Login successful, token: {token[:30]}...")
    
    # Test 2: Valid token request
    print("\n2. Testing valid token...")
    response = client.get('/brands/profiles', headers={
        'Authorization': f'Bearer {token}'
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Valid token works")
    else:
        print(f"✗ Valid token failed: {response.text}")
    
    # Test 3: Null token request
    print("\n3. Testing null token...")
    response = client.get('/brands/profiles', headers={
        'Authorization': 'Bearer null'
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        error = response.json()
        detail = error.get('detail', error.get('error', 'Unknown error'))
        print(f"✓ Null token properly rejected: {detail}")
    else:
        print(f"✗ Null token not properly handled: {response.text}")
    
    # Test 4: Undefined token request
    print("\n4. Testing undefined token...")
    response = client.get('/brands/profiles', headers={
        'Authorization': 'Bearer undefined'
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        error = response.json()
        detail = error.get('detail', error.get('error', 'Unknown error'))
        print(f"✓ Undefined token properly rejected: {detail}")
    else:
        print(f"✗ Undefined token not properly handled: {response.text}")
    
    # Test 5: Token validation endpoint
    print("\n5. Testing token validation...")
    response = client.get('/v1/auth/validate', headers={
        'Authorization': f'Bearer {token}'
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Token validation works: {result}")
    else:
        print(f"✗ Token validation failed: {response.text}")
    
    # Test 6: Token refresh
    print("\n6. Testing token refresh...")
    response = client.post('/v1/auth/refresh', headers={
        'Authorization': f'Bearer {token}'
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        new_token = response.json()['access_token']
        print(f"✓ Token refresh works: {new_token[:30]}...")
    else:
        print(f"✗ Token refresh failed: {response.text}")

else:
    print(f"✗ Login failed: {response.text}")

print("\n=== AUTH FIX TEST COMPLETE ===")