from datetime import datetime
from bson.objectid import ObjectId

# Convert a MongoDB study session document to Python dict
def session_to_dict(session_doc):
    return {
        'id': str(session_doc['_id']),
        'user_id': str(session_doc['user_id']),
        'subject': session_doc['subject'],
        'topic': session_doc['topic'],
        'question': session_doc['question'],
        'ai_response': session_doc['ai_response'],
        'satisfaction_rating': session_doc.get('satisfaction_rating'),
        'created_at': session_doc['created_at'].isoformat()
    }

# Create a new study session
def create_study_session(sessions_collection, user_id, subject, topic, question, ai_response, satisfaction_rating=None):
    session_data = {
        'user_id': ObjectId(user_id),
        'subject': subject,
        'topic': topic,
        'question': question,
        'ai_response': ai_response,
        'satisfaction_rating': satisfaction_rating,
        'created_at': datetime.utcnow()
    }
    result = sessions_collection.insert_one(session_data)
    return str(result.inserted_id)

# Get all study sessions for a user
def get_sessions_by_user(sessions_collection, user_id):
    return sessions_collection.find({'user_id': ObjectId(user_id)})

# Get a specific session by ID
def get_session_by_id(sessions_collection, session_id):
    return sessions_collection.find_one({'_id': ObjectId(session_id)})
