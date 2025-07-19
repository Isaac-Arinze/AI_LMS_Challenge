from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.ai_service import AITutorService
from models.session import create_study_session, get_sessions_by_user, get_session_by_id
from models.user import find_user_by_username, user_to_dict
from bson import ObjectId

ai_tutor_bp = Blueprint('ai_tutor', __name__)
ai_service = AITutorService()

@ai_tutor_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask_question():
    """Handle student questions and provide AI-powered explanations"""
    
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Validate input
        required_fields = ['subject', 'topic', 'question']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get user info for context (we'll use a simple approach for now)
        # In a real app, you'd get this from the database
        grade_level = 'secondary'  # Default grade level
        
        # Generate AI explanation
        explanation = ai_service.generate_explanation(
            subject=data['subject'],
            topic=data['topic'],
            question=data['question'],
            grade_level=grade_level
        )
        
        # Save study session (we'll need to import the database connection)
        from app import sessions_collection
        session_id = create_study_session(
            sessions_collection,
            user_id,
            data['subject'],
            data['topic'],
            data['question'],
            explanation
        )
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'response': explanation,
            'subject': data['subject'],
            'topic': data['topic']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_tutor_bp.route('/demo/ask', methods=['POST'])
def demo_ask_question():
    """Public endpoint for home page demo - no authentication required"""
    
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['subject', 'topic', 'question']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate AI explanation
        explanation = ai_service.generate_explanation(
            subject=data['subject'],
            topic=data['topic'],
            question=data['question'],
            grade_level='secondary'
        )
        
        return jsonify({
            'success': True,
            'response': explanation,
            'subject': data['subject'],
            'topic': data['topic']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_tutor_bp.route('/demo/practice', methods=['POST'])
def demo_generate_practice():
    """Public endpoint for practice questions demo - no authentication required"""
    
    try:
        data = request.get_json()
        
        # Validate input
        if 'subject' not in data or 'topic' not in data:
            return jsonify({'error': 'Subject and topic are required'}), 400
        
        difficulty = data.get('difficulty', 'medium')
        exam_type = data.get('exam_type')
        
        # Generate practice questions
        questions = ai_service.generate_practice_questions(
            subject=data['subject'],
            topic=data['topic'],
            difficulty=difficulty,
            exam_type=exam_type
        )
        
        return jsonify({
            'success': True,
            'questions': questions,
            'subject': data['subject'],
            'topic': data['topic'],
            'difficulty': difficulty,
            'exam_type': exam_type
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_tutor_bp.route('/practice', methods=['POST'])
@jwt_required()
def generate_practice():
    """Generate practice questions for a topic"""
    
    try:
        data = request.get_json()
        
        # Validate input
        if 'subject' not in data or 'topic' not in data:
            return jsonify({'error': 'Subject and topic are required'}), 400
        
        difficulty = data.get('difficulty', 'medium')
        exam_type = data.get('exam_type')
        
        # Generate practice questions
        questions = ai_service.generate_practice_questions(
            subject=data['subject'],
            topic=data['topic'],
            difficulty=difficulty,
            exam_type=exam_type
        )
        
        return jsonify({
            'success': True,
            'questions': questions,
            'subject': data['subject'],
            'topic': data['topic'],
            'difficulty': difficulty,
            'exam_type': exam_type
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_tutor_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_study_sessions():
    """Get user's study session history"""
    
    try:
        user_id = get_jwt_identity()
        from app import sessions_collection
        sessions = list(get_sessions_by_user(sessions_collection, user_id))
        
        # Convert to dict format
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': str(session['_id']),
                'user_id': str(session['user_id']),
                'subject': session['subject'],
                'topic': session['topic'],
                'question': session['question'],
                'ai_response': session['ai_response'],
                'satisfaction_rating': session.get('satisfaction_rating'),
                'created_at': session['created_at'].isoformat()
            })
        
        return jsonify({
            'success': True,
            'sessions': sessions_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_tutor_bp.route('/rate/<string:session_id>', methods=['POST'])
def rate_session(session_id):
    """Rate the quality of an AI response"""
    
    try:
        data = request.get_json()
        
        if 'rating' not in data:
            return jsonify({'error': 'Rating is required'}), 400
        
        rating = data['rating']
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
        
        from app import sessions_collection
        session = get_session_by_id(sessions_collection, session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Update session with rating
        sessions_collection.update_one(
            {'_id': session['_id']},
            {'$set': {'satisfaction_rating': rating}}
        )
        
        return jsonify({
            'success': True,
            'message': 'Rating saved successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500