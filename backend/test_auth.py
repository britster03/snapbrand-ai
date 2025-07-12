#!/usr/bin/env python3

import sys
sys.path.append('.')
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Try to login with existing test user
print('Testing login with existing test user...')
response = client.post('/auth/login', data={
    'username': 'testuser@example.com',
    'password': 'testpass123'
})
print(f'Login Status: {response.status_code}')
if response.status_code != 200:
    print(f'Login Error: {response.text}')
else:
    token = response.json()['access_token']
    print(f'Token received: {token[:50]}...')

# Check what users exist
print('\nTesting registration...')
response = client.post('/auth/register', json={
    'email': 'testuser2@example.com',
    'username': 'testuser2',
    'password': 'testpass123',
    'full_name': 'Test User 2'
})
print(f'Register Status: {response.status_code}')
if response.status_code != 200:
    print(f'Register Error: {response.text}')
else:
    print('Registration successful')
    # Now login
    response = client.post('/auth/login', data={
        'username': 'testuser2@example.com',
        'password': 'testpass123'
    })
    print(f'Login Status: {response.status_code}')
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f'Token received: {token[:50]}...')