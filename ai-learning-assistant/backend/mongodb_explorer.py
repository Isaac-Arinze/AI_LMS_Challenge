from pymongo import MongoClient
from bson import ObjectId
import json
from datetime import datetime

def connect_to_mongodb():
    """Connect to MongoDB and return client"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None

def explore_database(client):
    """Explore the learning_assistant database"""
    if client is None:
        return None
    
    db = client.learning_assistant
    print(f"\n📊 Database: {db.name}")
    
    # List all collections
    collections = db.list_collection_names()
    print(f"📁 Collections: {collections}")
    
    return db

def explore_users(db):
    """Explore users collection"""
    print("\n👥 USERS COLLECTION:")
    print("=" * 50)
    
    users = db.users.find()
    user_count = db.users.count_documents({})
    print(f"Total users: {user_count}")
    
    if user_count > 0:
        print("\n📋 User List:")
        for user in users:
            print(f"  - ID: {user['_id']}")
            print(f"    Username: {user.get('username', 'N/A')}")
            print(f"    Email: {user.get('email', 'N/A')}")
            print(f"    Full Name: {user.get('full_name', 'N/A')}")
            print(f"    Grade Level: {user.get('grade_level', 'N/A')}")
            print(f"    Created: {user.get('created_at', 'N/A')}")
            print("    " + "-" * 30)

def explore_sessions(db):
    """Explore study sessions collection"""
    print("\n📚 STUDY SESSIONS COLLECTION:")
    print("=" * 50)
    
    sessions = db.study_sessions.find()
    session_count = db.study_sessions.count_documents({})
    print(f"Total sessions: {session_count}")
    
    if session_count > 0:
        print("\n📋 Recent Sessions:")
        recent_sessions = db.study_sessions.find().sort('created_at', -1).limit(5)
        for session in recent_sessions:
            print(f"  - Session ID: {session['_id']}")
            print(f"    Subject: {session.get('subject', 'N/A')}")
            print(f"    Topic: {session.get('topic', 'N/A')}")
            print(f"    Question: {session.get('question', 'N/A')[:100]}...")
            print(f"    Rating: {session.get('satisfaction_rating', 'Not rated')}")
            print(f"    Created: {session.get('created_at', 'N/A')}")
            print("    " + "-" * 30)

def add_sample_user(db):
    """Add a sample user for testing"""
    print("\n➕ Adding sample user...")
    
    sample_user = {
        "username": "demo_student",
        "email": "demo@example.com",
        "full_name": "Demo Student",
        "grade_level": "SS2",
        "subjects": ["Mathematics", "Physics"],
        "password_hash": "demo_hash",
        "created_at": datetime.utcnow()
    }
    
    try:
        result = db.users.insert_one(sample_user)
        print(f"✅ Sample user added with ID: {result.inserted_id}")
    except Exception as e:
        print(f"❌ Failed to add sample user: {e}")

def add_sample_session(db):
    """Add a sample study session"""
    print("\n➕ Adding sample study session...")
    
    sample_session = {
        "user_id": None,  # No specific user
        "subject": "Mathematics",
        "topic": "Algebra",
        "question": "How do I solve quadratic equations?",
        "ai_response": "To solve quadratic equations, you can use the quadratic formula: x = (-b ± √(b² - 4ac)) / 2a",
        "satisfaction_rating": 5,
        "created_at": datetime.utcnow()
    }
    
    try:
        result = db.study_sessions.insert_one(sample_session)
        print(f"✅ Sample session added with ID: {result.inserted_id}")
    except Exception as e:
        print(f"❌ Failed to add sample session: {e}")

def main():
    """Main function to explore MongoDB"""
    print("🔍 MongoDB Explorer for AI Learning Assistant")
    print("=" * 60)
    
    # Connect to MongoDB
    client = connect_to_mongodb()
    if not client:
        return
    
    # Explore database
    db = explore_database(client)
    if db is None:
        return
    
    # Explore collections
    explore_users(db)
    explore_sessions(db)
    
    # Ask user what they want to do
    print("\n🛠️  What would you like to do?")
    print("1. Add sample user")
    print("2. Add sample session")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        add_sample_user(db)
    elif choice == "2":
        add_sample_session(db)
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")
    
    # Close connection
    client.close()
    print("\n✅ MongoDB connection closed")

if __name__ == "__main__":
    main() 