from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson import ObjectId
import google.generativeai as genai
import os
import json
import random

quiz_bp = Blueprint('quiz', __name__)

# MongoDB collections - will be set up in main app
def init_collections(db_instance):
    global quizzes_collection, quiz_attempts_collection
    quizzes_collection = db_instance.quizzes
    quiz_attempts_collection = db_instance.quiz_attempts

# AI Service for quiz generation
class QuizGenerationService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_quiz_questions(self, subject, topic, difficulty="medium", num_questions=10, exam_type="WAEC"):
        """Generate quiz questions similar to standard exams like WAEC, JAMB"""
        
        exam_context = {
            "WAEC": "West African Examinations Council (WAEC) style questions",
            "JAMB": "Joint Admissions and Matriculation Board (JAMB) style questions",
            "NECO": "National Examinations Council (NECO) style questions",
            "IGCSE": "International General Certificate of Secondary Education style questions"
        }
        
        prompt = f"""
        Generate {num_questions} multiple choice questions for {subject} topic: {topic}
        
        Requirements:
        - Style: {exam_context.get(exam_type, exam_context['WAEC'])}
        - Difficulty: {difficulty}
        - Format: Each question should have 4 options (A, B, C, D)
        - Include explanations for correct answers
        - Questions should be objective and test understanding
        - Use Nigerian context where appropriate
        
        Return the questions in this exact JSON format:
        {{
            "questions": [
                {{
                    "question": "Question text here?",
                    "options": {{
                        "A": "Option A",
                        "B": "Option B", 
                        "C": "Option C",
                        "D": "Option D"
                    }},
                    "correct_answer": "A",
                    "explanation": "Explanation of why this is correct",
                    "difficulty": "{difficulty}",
                    "topic": "{topic}"
                }}
            ]
        }}
        
        Make sure the JSON is valid and properly formatted.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            
            questions_data = json.loads(response_text)
            return questions_data.get('questions', [])
            
        except Exception as e:
            print(f"Error generating quiz questions: {e}")
            return self._get_fallback_questions(subject, topic, num_questions)
    
    def _get_fallback_questions(self, subject, topic, num_questions):
        """Fallback questions if AI generation fails"""
        fallback_questions = {
            "Mathematics": [
                {
                    "question": f"What is the value of x in the equation 2x + 5 = 13?",
                    "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                    "correct_answer": "B",
                    "explanation": "2x + 5 = 13 → 2x = 8 → x = 4",
                    "difficulty": "medium",
                    "topic": topic
                }
            ],
            "Physics": [
                {
                    "question": "What is the SI unit of force?",
                    "options": {"A": "Joule", "B": "Newton", "C": "Watt", "D": "Pascal"},
                    "correct_answer": "B",
                    "explanation": "The SI unit of force is the Newton (N)",
                    "difficulty": "easy",
                    "topic": topic
                }
            ],
            "Chemistry": [
                {
                    "question": "What is the chemical symbol for gold?",
                    "options": {"A": "Ag", "B": "Au", "C": "Fe", "D": "Cu"},
                    "correct_answer": "B",
                    "explanation": "Au is the chemical symbol for gold (from Latin 'aurum')",
                    "difficulty": "easy",
                    "topic": topic
                }
            ]
        }
        
        return fallback_questions.get(subject, fallback_questions["Mathematics"]) * num_questions

quiz_service = QuizGenerationService()

@quiz_bp.route('/api/quiz/generate', methods=['POST'])
@jwt_required()
def generate_quiz():
    """Generate a new quiz based on subject and topic"""
    try:
        data = request.get_json()
        subject = data.get('subject')
        topic = data.get('topic')
        difficulty = data.get('difficulty', 'medium')
        num_questions = data.get('num_questions', 10)
        exam_type = data.get('exam_type', 'WAEC')
        
        if not subject or not topic:
            return jsonify({'error': 'Subject and topic are required'}), 400
        
        # Generate questions using AI
        questions = quiz_service.generate_quiz_questions(
            subject, topic, difficulty, num_questions, exam_type
        )
        
        # Create quiz document
        quiz_data = {
            'title': f"{subject} - {topic} Quiz",
            'subject': subject,
            'topic': topic,
            'difficulty': difficulty,
            'questions': questions,
            'time_limit': 30,  # 30 minutes
            'passing_score': 70,
            'created_at': datetime.utcnow(),
            'created_by': get_jwt_identity()
        }
        
        result = quizzes_collection.insert_one(quiz_data)
        quiz_data['_id'] = result.inserted_id
        
        return jsonify({
            'success': True,
            'quiz': {
                'id': str(result.inserted_id),
                'title': quiz_data['title'],
                'subject': subject,
                'topic': topic,
                'difficulty': difficulty,
                'num_questions': len(questions),
                'time_limit': quiz_data['time_limit']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error generating quiz: {str(e)}'}), 500

@quiz_bp.route('/api/quiz/<quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz(quiz_id):
    """Get quiz details and questions (without correct answers)"""
    try:
        quiz_doc = quizzes_collection.find_one({'_id': ObjectId(quiz_id)})
        if not quiz_doc:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Remove correct answers for security
        questions_for_user = []
        for q in quiz_doc['questions']:
            question_copy = q.copy()
            question_copy.pop('correct_answer', None)
            question_copy.pop('explanation', None)
            questions_for_user.append(question_copy)
        
        return jsonify({
            'quiz': {
                'id': str(quiz_doc['_id']),
                'title': quiz_doc['title'],
                'subject': quiz_doc['subject'],
                'topic': quiz_doc['topic'],
                'difficulty': quiz_doc['difficulty'],
                'questions': questions_for_user,
                'time_limit': quiz_doc['time_limit'],
                'passing_score': quiz_doc['passing_score']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving quiz: {str(e)}'}), 500

@quiz_bp.route('/api/quiz/start/<quiz_id>', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    """Start a quiz attempt"""
    try:
        user_id = get_jwt_identity()
        
        # Check if quiz exists
        quiz_doc = quizzes_collection.find_one({'_id': ObjectId(quiz_id)})
        if not quiz_doc:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Check if user already has an incomplete attempt
        existing_attempt = quiz_attempts_collection.find_one({
            'user_id': user_id,
            'quiz_id': ObjectId(quiz_id),
            'completed': False
        })
        
        if existing_attempt:
            return jsonify({'error': 'You already have an incomplete attempt for this quiz'}), 400
        
        # Create new attempt
        attempt_data = {
            'user_id': user_id,
            'quiz_id': ObjectId(quiz_id),
            'answers': {},
            'score': 0,
            'total_questions': len(quiz_doc['questions']),
            'correct_answers': 0,
            'time_taken': 0,
            'completed': False,
            'started_at': datetime.utcnow(),
            'passed': False
        }
        
        result = quiz_attempts_collection.insert_one(attempt_data)
        
        return jsonify({
            'success': True,
            'attempt_id': str(result.inserted_id),
            'time_limit': quiz_doc['time_limit'],
            'total_questions': len(quiz_doc['questions'])
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error starting quiz: {str(e)}'}), 500

@quiz_bp.route('/api/quiz/submit/<attempt_id>', methods=['POST'])
@jwt_required()
def submit_quiz(attempt_id):
    """Submit quiz answers and calculate score"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
        
        # Get attempt
        attempt_doc = quiz_attempts_collection.find_one({
            '_id': ObjectId(attempt_id),
            'user_id': user_id
        })
        
        if not attempt_doc:
            return jsonify({'error': 'Quiz attempt not found'}), 404
        
        if attempt_doc['completed']:
            return jsonify({'error': 'Quiz already completed'}), 400
        
        # Get quiz for scoring
        quiz_doc = quizzes_collection.find_one({'_id': attempt_doc['quiz_id']})
        if not quiz_doc:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Calculate score
        correct_answers = 0
        total_questions = len(quiz_doc['questions'])
        detailed_results = []
        
        for i, question in enumerate(quiz_doc['questions']):
            user_answer = answers.get(str(i), '')
            is_correct = user_answer == question['correct_answer']
            
            if is_correct:
                correct_answers += 1
            
            detailed_results.append({
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': question['correct_answer'],
                'is_correct': is_correct,
                'explanation': question.get('explanation', '')
            })
        
        score = (correct_answers / total_questions) * 100
        passed = score >= quiz_doc['passing_score']
        
        # Update attempt
        quiz_attempts_collection.update_one(
            {'_id': ObjectId(attempt_id)},
            {
                '$set': {
                    'answers': answers,
                    'score': score,
                    'correct_answers': correct_answers,
                    'time_taken': time_taken,
                    'completed': True,
                    'completed_at': datetime.utcnow(),
                    'passed': passed
                }
            }
        )
        
        return jsonify({
            'success': True,
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'passed': passed,
            'time_taken': time_taken,
            'detailed_results': detailed_results
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error submitting quiz: {str(e)}'}), 500

@quiz_bp.route('/api/quiz/attempts', methods=['GET'])
@jwt_required()
def get_user_attempts():
    """Get user's quiz attempts history"""
    try:
        user_id = get_jwt_identity()
        
        attempts = list(quiz_attempts_collection.find(
            {'user_id': user_id},
            {'answers': 0}  # Exclude answers for privacy
        ).sort('started_at', -1))
        
        # Convert ObjectId to string
        for attempt in attempts:
            attempt['_id'] = str(attempt['_id'])
            attempt['quiz_id'] = str(attempt['quiz_id'])
            attempt['started_at'] = attempt['started_at'].isoformat()
            if attempt.get('completed_at'):
                attempt['completed_at'] = attempt['completed_at'].isoformat()
        
        return jsonify({'attempts': attempts}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving attempts: {str(e)}'}), 500

@quiz_bp.route('/api/quiz/available', methods=['GET'])
@jwt_required()
def get_available_quizzes():
    """Get available quizzes by subject"""
    try:
        subject = request.args.get('subject')
        
        query = {}
        if subject:
            query['subject'] = subject
        
        quizzes = list(quizzes_collection.find(query).sort('created_at', -1))
        
        # Convert ObjectId to string
        for quiz in quizzes:
            quiz['_id'] = str(quiz['_id'])
            quiz['created_at'] = quiz['created_at'].isoformat()
            # Remove questions for list view
            quiz.pop('questions', None)
        
        return jsonify({'quizzes': quizzes}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving quizzes: {str(e)}'}), 500 