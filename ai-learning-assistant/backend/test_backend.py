#!/usr/bin/env python3
"""
Simple test script to check if the backend is working
"""

import requests
import json

def test_backend():
    base_url = "http://127.0.0.1:5000"
    
    print("Testing backend connection...")
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint (GET /): {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to root endpoint: {e}")
    
    # Test 2: Health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health endpoint (GET /health): {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to health endpoint: {e}")
    
    # Test 3: Registration endpoint (POST)
    try:
        test_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
            "grade_level": "10"
        }
        response = requests.post(f"{base_url}/api/auth/register", 
                               json=test_data,
                               headers={"Content-Type": "application/json"})
        print(f"Registration endpoint (POST /api/auth/register): {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to registration endpoint: {e}")

if __name__ == "__main__":
    test_backend() 