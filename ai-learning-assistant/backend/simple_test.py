import requests
import time

def test_flask_app():
    """Simple test to check if Flask app is working"""
    print("🔍 Testing Flask App...")
    
    # Wait for app to start
    time.sleep(2)
    
    try:
        # Test home endpoint
        print("Testing home endpoint...")
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        # Test health endpoint
        print("\nTesting health endpoint...")
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Flask app might not be running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_flask_app() 