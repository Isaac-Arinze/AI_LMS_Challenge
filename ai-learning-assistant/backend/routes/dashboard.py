from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson import ObjectId
import statistics

dashboard_bp = Blueprint('dashboard', __name__)

# MongoDB collections - will be set up in main app
users_collection = None
sessions_collection = None
quiz_attempts_collection = None
study_groups_collection = None

def init_collections(db_instance):
    global users_collection, sessions_collection, quiz_attempts_collection, study_groups_collection
    users_collection = db_instance.users
    sessions_collection = db_instance.study_sessions
    quiz_attempts_collection = db_instance.quiz_attempts
    study_groups_collection = db_instance.study_groups

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get user dashboard statistics"""
    try:
        user_id = get_jwt_identity()
        
        # Get user data
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get study sessions
        sessions = list(sessions_collection.find({'user_id': user_id}).sort('created_at', -1))
        
        # Get quiz attempts
        quiz_attempts = list(quiz_attempts_collection.find({'user_id': user_id}).sort('started_at', -1))
        
        # Get study groups
        groups = list(study_groups_collection.find({'members': user_id}))
        
        # Calculate statistics
        total_sessions = len(sessions)
        total_questions = sum(len(session.get('questions', [])) for session in sessions)
        avg_rating = 0
        if sessions:
            ratings = [s.get('satisfaction_rating', 0) for s in sessions if s.get('satisfaction_rating')]
            avg_rating = statistics.mean(ratings) if ratings else 0
        
        # Quiz statistics
        total_quizzes = len(quiz_attempts)
        passed_quizzes = len([q for q in quiz_attempts if q.get('passed', False)])
        avg_quiz_score = 0
        if quiz_attempts:
            scores = [q.get('score', 0) for q in quiz_attempts if q.get('score')]
            avg_quiz_score = statistics.mean(scores) if scores else 0
        
        # Study groups
        total_groups = len(groups)
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_sessions = len([s for s in sessions if s['created_at'] > week_ago])
        recent_quizzes = len([q for q in quiz_attempts if q['started_at'] > week_ago])
        
        stats = {
            'user': {
                'name': user['full_name'],
                'grade_level': user.get('grade_level', ''),
                'subjects': user.get('subjects', []),
                'joined_date': user['created_at'].isoformat()
            },
            'study_sessions': {
                'total': total_sessions,
                'total_questions': total_questions,
                'avg_rating': round(avg_rating, 1),
                'recent': recent_sessions
            },
            'quizzes': {
                'total': total_quizzes,
                'passed': passed_quizzes,
                'avg_score': round(avg_quiz_score, 1),
                'recent': recent_quizzes
            },
            'groups': {
                'total': total_groups
            },
            'recent_activity': {
                'sessions': recent_sessions,
                'quizzes': recent_quizzes
            }
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving dashboard stats: {str(e)}'}), 500

@dashboard_bp.route('/api/dashboard/recent-activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    """Get user's recent activity"""
    try:
        user_id = get_jwt_identity()
        
        # Get recent study sessions
        recent_sessions = list(sessions_collection.find(
            {'user_id': user_id}
        ).sort('created_at', -1).limit(5))
        
        # Get recent quiz attempts
        recent_quizzes = list(quiz_attempts_collection.find(
            {'user_id': user_id}
        ).sort('started_at', -1).limit(5))
        
        # Format sessions
        for session in recent_sessions:
            session['_id'] = str(session['_id'])
            session['created_at'] = session['created_at'].isoformat()
        
        # Format quizzes
        for quiz in recent_quizzes:
            quiz['_id'] = str(quiz['_id'])
            quiz['started_at'] = quiz['started_at'].isoformat()
            if quiz.get('completed_at'):
                quiz['completed_at'] = quiz['completed_at'].isoformat()
        
        return jsonify({
            'sessions': recent_sessions,
            'quizzes': recent_quizzes
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving recent activity: {str(e)}'}), 500

@dashboard_bp.route('/api/dashboard/progress', methods=['GET'])
@jwt_required()
def get_learning_progress():
    """Get user's learning progress by subject"""
    try:
        user_id = get_jwt_identity()
        
        # Get user's subjects
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        subjects = user.get('subjects', [])
        
        progress = {}
        
        for subject in subjects:
            # Get sessions for this subject
            subject_sessions = list(sessions_collection.find({
                'user_id': user_id,
                'subject': subject
            }))
            
            # Get quiz attempts for this subject
            subject_quizzes = list(quiz_attempts_collection.find({
                'user_id': user_id
            }))
            
            # Calculate progress
            total_sessions = len(subject_sessions)
            total_questions = sum(len(s.get('questions', [])) for s in subject_sessions)
            avg_rating = 0
            if subject_sessions:
                ratings = [s.get('satisfaction_rating', 0) for s in subject_sessions if s.get('satisfaction_rating')]
                avg_rating = statistics.mean(ratings) if ratings else 0
            
            # Quiz progress for this subject
            subject_quiz_attempts = []
            for quiz in subject_quizzes:
                # Get quiz details to check subject
                from routes.quiz import quizzes_collection
                quiz_details = quizzes_collection.find_one({'_id': quiz['quiz_id']})
                if quiz_details and quiz_details.get('subject') == subject:
                    subject_quiz_attempts.append(quiz)
            
            total_quizzes = len(subject_quiz_attempts)
            passed_quizzes = len([q for q in subject_quiz_attempts if q.get('passed', False)])
            avg_score = 0
            if subject_quiz_attempts:
                scores = [q.get('score', 0) for q in subject_quiz_attempts if q.get('score')]
                avg_score = statistics.mean(scores) if scores else 0
            
            progress[subject] = {
                'sessions': total_sessions,
                'questions': total_questions,
                'avg_rating': round(avg_rating, 1),
                'quizzes': total_quizzes,
                'passed_quizzes': passed_quizzes,
                'avg_score': round(avg_score, 1)
            }
        
        return jsonify({'progress': progress}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving progress: {str(e)}'}), 500

@dashboard_bp.route('/api/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get user profile information"""
    try:
        user_id = get_jwt_identity()
        
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Remove sensitive information
        user_data = {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'grade_level': user.get('grade_level', ''),
            'subjects': user.get('subjects', []),
            'created_at': user['created_at'].isoformat(),
            'email_verified': user.get('email_verified', False)
        }
        
        return jsonify({'profile': user_data}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving profile: {str(e)}'}), 500

@dashboard_bp.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Update user profile information"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Fields that can be updated
        update_data = {}
        
        if 'full_name' in data:
            update_data['full_name'] = data['full_name']
        
        if 'grade_level' in data:
            update_data['grade_level'] = data['grade_level']
        
        if 'subjects' in data:
            update_data['subjects'] = data['subjects']
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update user
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'No changes made'}), 400
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error updating profile: {str(e)}'}), 500

@dashboard_bp.route('/api/profile/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Get user
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check current password
        from werkzeug.security import check_password_hash, generate_password_hash
        if not check_password_hash(user['password_hash'], current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Update password
        new_password_hash = generate_password_hash(new_password)
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password_hash': new_password_hash}}
        )
        
        return jsonify({'success': True, 'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error changing password: {str(e)}'}), 500

@dashboard_bp.route('/api/dashboard/achievements', methods=['GET'])
@jwt_required()
def get_achievements():
    """Get user achievements and badges"""
    try:
        user_id = get_jwt_identity()
        
        # Get user stats
        sessions = list(sessions_collection.find({'user_id': user_id}))
        quiz_attempts = list(quiz_attempts_collection.find({'user_id': user_id}))
        
        achievements = []
        
        # Session achievements
        total_sessions = len(sessions)
        if total_sessions >= 1:
            achievements.append({
                'id': 'first_session',
                'title': 'First Step',
                'description': 'Completed your first study session',
                'icon': '🎯',
                'earned': True
            })
        
        if total_sessions >= 10:
            achievements.append({
                'id': 'dedicated_learner',
                'title': 'Dedicated Learner',
                'description': 'Completed 10 study sessions',
                'icon': '📚',
                'earned': True
            })
        
        if total_sessions >= 50:
            achievements.append({
                'id': 'study_master',
                'title': 'Study Master',
                'description': 'Completed 50 study sessions',
                'icon': '🏆',
                'earned': True
            })
        
        # Quiz achievements
        total_quizzes = len(quiz_attempts)
        if total_quizzes >= 1:
            achievements.append({
                'id': 'first_quiz',
                'title': 'Quiz Explorer',
                'description': 'Completed your first quiz',
                'icon': '🧠',
                'earned': True
            })
        
        passed_quizzes = len([q for q in quiz_attempts if q.get('passed', False)])
        if passed_quizzes >= 5:
            achievements.append({
                'id': 'quiz_champion',
                'title': 'Quiz Champion',
                'description': 'Passed 5 quizzes',
                'icon': '🥇',
                'earned': True
            })
        
        # Rating achievements
        if sessions:
            high_ratings = len([s for s in sessions if s.get('satisfaction_rating', 0) >= 4])
            if high_ratings >= 10:
                achievements.append({
                    'id': 'helpful_explanations',
                    'title': 'Helpful Explanations',
                    'description': 'Rated 10+ explanations as very helpful',
                    'icon': '⭐',
                    'earned': True
                })
        
        return jsonify({'achievements': achievements}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving achievements: {str(e)}'}), 500 