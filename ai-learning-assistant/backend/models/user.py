from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

# Convert MongoDB user document to Python dict
def user_to_dict(user_doc):
    return {
        'id': str(user_doc['_id']),
        'username': user_doc['username'],
        'email': user_doc['email'],
        'full_name': user_doc['full_name'],
        'grade_level': user_doc.get('grade_level'),
        'subjects': user_doc.get('subjects'),
        'created_at': user_doc['created_at'].isoformat()
    }

# Create a new user document
def create_user(users_collection, username, email, password, full_name, grade_level=None, subjects=None):
    password_hash = generate_password_hash(password)
    user_data = {
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'full_name': full_name,
        'grade_level': grade_level,
        'subjects': subjects,  # Can be list or JSON-like structure
        'created_at': datetime.utcnow()
    }
    result = users_collection.insert_one(user_data)
    return str(result.inserted_id)

# Find a user by username
def find_user_by_username(users_collection, username):
    return users_collection.find_one({'username': username})

# Check password
def verify_user_password(user_doc, password):
    return check_password_hash(user_doc['password_hash'], password)
