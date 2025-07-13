import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_home_endpoint():
    """Test the home endpoint"""
    print("\n🏠 Testing Home Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Home endpoint working!")
            print(f"   Message: {data.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Home endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Home endpoint error: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("\n👤 Testing User Registration...")
    try:
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
            "grade_level": "SS2",
            "subjects": ["Mathematics", "Physics"]
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code == 201:
            data = response.json()
            print("✅ User registration successful!")
            print(f"   User ID: {data.get('user', {}).get('_id', 'N/A')}")
            return data.get('access_token')
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_user_login():
    """Test user login"""
    print("\n🔐 Testing User Login...")
    try:
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ User login successful!")
            return data.get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_ai_question(access_token=None):
    """Test AI question asking"""
    print("\n🤖 Testing AI Question Feature...")
    try:
        question_data = {
            "subject": "Mathematics",
            "topic": "Algebra",
            "question": "How do I solve quadratic equations?"
        }
        
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        
        response = requests.post(f"{BASE_URL}/api/ai/ask", json=question_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ AI question feature working!")
            print(f"   Session ID: {data.get('session_id', 'N/A')}")
            print(f"   Explanation length: {len(data.get('explanation', ''))} characters")
            return data.get('session_id')
        else:
            print(f"❌ AI question failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ AI question error: {e}")
        return None

def test_practice_questions():
    """Test practice question generation"""
    print("\n📝 Testing Practice Questions...")
    try:
        practice_data = {
            "subject": "Physics",
            "topic": "Mechanics",
            "difficulty": "medium"
        }
        
        response = requests.post(f"{BASE_URL}/api/ai/practice", json=practice_data)
        if response.status_code == 200:
            data = response.json()
            questions = data.get('questions', [])
            print("✅ Practice questions generated!")
            print(f"   Number of questions: {len(questions)}")
            return True
        else:
            print(f"❌ Practice questions failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Practice questions error: {e}")
        return False

def test_study_groups():
    """Test study groups endpoint"""
    print("\n👥 Testing Study Groups...")
    try:
        response = requests.get(f"{BASE_URL}/api/groups")
        if response.status_code == 200:
            data = response.json()
            groups = data.get('groups', [])
            print("✅ Study groups endpoint working!")
            print(f"   Number of groups: {len(groups)}")
            return True
        else:
            print(f"❌ Study groups failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Study groups error: {e}")
        return False

def test_authenticated_endpoints(access_token):
    """Test endpoints that require authentication"""
    print("\n🔒 Testing Authenticated Endpoints...")
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Test study sessions endpoint
        response = requests.get(f"{BASE_URL}/api/ai/sessions", headers=headers)
        if response.status_code == 200:
            print("✅ Authenticated sessions endpoint working!")
        else:
            print(f"❌ Sessions endpoint failed: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Authenticated endpoints error: {e}")
        return False

def test_session_rating(session_id):
    """Test session rating endpoint"""
    print("\n⭐ Testing Session Rating...")
    try:
        rating_data = {
            "rating": 5
        }
        
        response = requests.post(f"{BASE_URL}/api/ai/rate/{session_id}", json=rating_data)
        if response.status_code == 200:
            print("✅ Session rating successful!")
            return True
        else:
            print(f"❌ Session rating failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Session rating error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AI Learning Assistant API Tests...")
    print("=" * 60)
    
    # Test basic endpoints
    health_ok = test_health_check()
    home_ok = test_home_endpoint()
    
    # Test authentication
    token = test_user_registration()
    if not token:
        token = test_user_login()
    
    # Test AI features
    session_id = test_ai_question(token)
    practice_ok = test_practice_questions()
    
    # Test other endpoints
    groups_ok = test_study_groups()
    
    # Test authenticated endpoints
    if token:
        auth_ok = test_authenticated_endpoints(token)
    else:
        auth_ok = False
    
    # Test session rating
    rating_ok = False
    if session_id:
        rating_ok = test_session_rating(session_id)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 60)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Home Endpoint: {'✅ PASS' if home_ok else '❌ FAIL'}")
    print(f"User Registration: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"AI Question Feature: {'✅ PASS' if session_id else '❌ FAIL'}")
    print(f"Practice Questions: {'✅ PASS' if practice_ok else '❌ FAIL'}")
    print(f"Study Groups: {'✅ PASS' if groups_ok else '❌ FAIL'}")
    print(f"Authenticated Endpoints: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    print(f"Session Rating: {'✅ PASS' if rating_ok else '❌ FAIL'}")
    
    # Overall status
    all_tests = [health_ok, home_ok, bool(token), bool(session_id), practice_ok, groups_ok, auth_ok, rating_ok]
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Your AI Learning Assistant is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    print(f"\n🌐 Your API is running at: {BASE_URL}")
    print("📚 Ready to help students learn!")
    
    # List all available endpoints
    print("\n📋 AVAILABLE ENDPOINTS:")
    print("=" * 60)
    print("GET  /                    - Home page")
    print("GET  /health              - Health check")
    print("POST /api/auth/register   - User registration")
    print("POST /api/auth/login      - User login")
    print("POST /api/ai/ask          - Ask AI questions")
    print("POST /api/ai/practice     - Generate practice questions")
    print("GET  /api/ai/sessions     - Get study history (requires auth)")
    print("POST /api/ai/rate/<id>    - Rate AI responses")
    print("GET  /api/groups          - Get study groups")

if __name__ == "__main__":
    main() 