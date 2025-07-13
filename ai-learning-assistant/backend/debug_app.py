#!/usr/bin/env python3
"""
Debug script to check Flask app
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Loading Flask app...")
    from app import app
    print("✅ Flask app loaded successfully")
    
    print("Testing app routes...")
    with app.test_client() as client:
        # Test root route
        response = client.get('/')
        print(f"Root route: {response.status_code}")
        print(f"Response: {response.get_data(as_text=True)}")
        
        # Test health route
        response = client.get('/health')
        print(f"Health route: {response.status_code}")
        print(f"Response: {response.get_data(as_text=True)}")
        
except Exception as e:
    print(f"❌ Error loading Flask app: {e}")
    import traceback
    traceback.print_exc() 