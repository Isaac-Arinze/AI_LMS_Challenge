#!/usr/bin/env python3
"""
Test script for the Quiz System
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://127.0.0.1:5000"

def test_quiz_system():
    """Test the quiz system functionality"""
    
    print("🧪 Testing Quiz System...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running.")
        return
    
    # Test 2: Test quiz generation (requires authentication)
    print("\n📝 Testing Quiz Generation...")
    
    # First, try to register a test user
    test_user = {
        "full_name": "Test User",
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "grade_level": "SS2",
        "subjects": ["Mathematics", "Physics"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        if response.status_code == 201:
            print("✅ Test user registered successfully")
        elif response.status_code == 400:
            print("ℹ️  Test user already exists")
        else:
            print(f"❌ Failed to register test user: {response.status_code}")
    except Exception as e:
        print(f"❌ Error registering test user: {e}")
    
    # Test 3: Test login
    print("\n🔐 Testing Login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            if token:
                print("✅ Login successful")
                
                # Test 4: Test quiz generation with token
                print("\n🎯 Testing Quiz Generation with Authentication...")
                quiz_data = {
                    "subject": "Mathematics",
                    "topic": "Quadratic Equations",
                    "difficulty": "medium",
                    "exam_type": "WAEC",
                    "num_questions": 5
                }
                
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.post(f"{BASE_URL}/api/quiz/generate", json=quiz_data, headers=headers)
                
                if response.status_code == 201:
                    data = response.json()
                    quiz_id = data['quiz']['id']
                    print(f"✅ Quiz generated successfully! Quiz ID: {quiz_id}")
                    
                    # Test 5: Test getting quiz details
                    print("\n📋 Testing Quiz Details Retrieval...")
                    response = requests.get(f"{BASE_URL}/api/quiz/{quiz_id}", headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        questions = data['quiz']['questions']
                        print(f"✅ Quiz details retrieved! {len(questions)} questions loaded")
                        
                        # Test 6: Test starting quiz
                        print("\n🚀 Testing Quiz Start...")
                        response = requests.post(f"{BASE_URL}/api/quiz/start/{quiz_id}", headers=headers)
                        
                        if response.status_code == 201:
                            data = response.json()
                            attempt_id = data['attempt_id']
                            print(f"✅ Quiz started successfully! Attempt ID: {attempt_id}")
                            
                            # Test 7: Test quiz submission
                            print("\n📤 Testing Quiz Submission...")
                            answers = {"0": "A", "1": "B", "2": "C", "3": "D", "4": "A"}
                            submit_data = {
                                "answers": answers,
                                "time_taken": 300  # 5 minutes
                            }
                            
                            response = requests.post(f"{BASE_URL}/api/quiz/submit/{attempt_id}", 
                                                   json=submit_data, headers=headers)
                            
                            if response.status_code == 200:
                                data = response.json()
                                score = data['score']
                                passed = data['passed']
                                print(f"✅ Quiz submitted successfully! Score: {score}%, Passed: {passed}")
                            else:
                                print(f"❌ Quiz submission failed: {response.status_code}")
                        else:
                            print(f"❌ Quiz start failed: {response.status_code}")
                    else:
                        print(f"❌ Quiz details retrieval failed: {response.status_code}")
                else:
                    print(f"❌ Quiz generation failed: {response.status_code}")
                    print(f"Error: {response.text}")
            else:
                print("❌ No access token received")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error during login: {e}")
    
    print("\n🎉 Quiz System Test Complete!")

if __name__ == "__main__":
    test_quiz_system() 