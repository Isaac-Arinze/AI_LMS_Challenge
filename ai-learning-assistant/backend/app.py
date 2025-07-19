from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import google.generativeai as genai
import os
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from flask_mail import Mail, Message
import secrets

# Import routes
from routes.quiz import quiz_bp
from routes.study_groups import study_groups_bp
from routes.dashboard import dashboard_bp
from routes.ai_tutor import ai_tutor_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
jwt = JWTManager(app)
CORS(app, origins=[
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',
    'http://127.0.0.1:3000'
], supports_credentials=True)

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.learning_assistant

# Collections
users_collection = db.users
sessions_collection = db.study_sessions
quizzes_collection = db.quizzes
quiz_attempts_collection = db.quiz_attempts
study_groups_collection = db.study_groups
group_messages_collection = db.group_messages
group_resources_collection = db.group_resources

# Register blueprints
app.register_blueprint(quiz_bp)
app.register_blueprint(study_groups_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(ai_tutor_bp, url_prefix='/api/ai')

# Initialize collections
from routes.quiz import init_collections as init_quiz_collections
from routes.study_groups import init_collections as init_study_groups_collections
from routes.dashboard import init_collections as init_dashboard_collections

init_quiz_collections(db)
init_study_groups_collections(db)
init_dashboard_collections(db)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your-app-password')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')

mail = Mail(app)

# Set up Google Gemini
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
except Exception as e:
    print(f"Warning: Could not configure Gemini API: {e}")

# User Model
class User:
    def __init__(self, user_data):
        self.id = user_data['_id']
        self.username = user_data['username']
        self.email = user_data['email']
        self.password_hash = user_data['password_hash']
        self.full_name = user_data['full_name']
        self.grade_level = user_data['grade_level']
        self.subjects = user_data['subjects']
        self.created_at = user_data['created_at']
        self.email_verified = user_data.get('email_verified', False)
        self.verification_token = user_data.get('verification_token', None)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'grade_level': self.grade_level,
            'subjects': self.subjects,
            'created_at': self.created_at,
            'email_verified': self.email_verified
        }

def send_verification_email(user_email, user_name, verification_token):
    """Send verification email to user"""
    try:
        verification_url = f"http://127.0.0.1:5000/api/auth/verify/{verification_token}"
        
        msg = Message(
            'Welcome to AI Tutor Pro - Verify Your Account',
            recipients=[user_email]
        )
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">Welcome to AI Tutor Pro! 🎓</h2>
            
            <p>Hi {user_name},</p>
            
            <p>Thank you for signing up for AI Tutor Pro! We're excited to have you on board.</p>
            
            <p>To complete your registration and start using our AI-powered tutoring system, please verify your email address by clicking the button below:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Verify My Account
                </a>
            </div>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #7f8c8d;">{verification_url}</p>
            
            <p>This link will expire in 24 hours for security reasons.</p>
            
            <p>If you didn't create an account with AI Tutor Pro, you can safely ignore this email.</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ecf0f1;">
            
            <p style="color: #7f8c8d; font-size: 12px;">
                Best regards,<br>
                The AI Tutor Pro Team
            </p>
        </div>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

# Study Session Model
class StudySession:
    def __init__(self, session_data):
        self.id = session_data['_id']
        self.user_id = session_data['user_id']
        self.subject = session_data['subject']
        self.topic = session_data['topic']
        self.question = session_data['question']
        self.ai_response = session_data['ai_response']
        self.satisfaction_rating = session_data['satisfaction_rating']
        self.created_at = session_data['created_at']
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'topic': self.topic,
            'question': self.question,
            'ai_response': self.ai_response,
            'satisfaction_rating': self.satisfaction_rating,
            'created_at': self.created_at
        }

# AI Service Class
class AITutorService:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            print(f"Warning: Could not initialize Gemini model: {e}")
            self.model = None
    
    def generate_explanation(self, subject, topic, question, grade_level=None, user_context=None, conversation_history=None):
        """Generate AI-powered explanation for student questions with user context"""
        
        if not self.model:
            return "I apologize, but the AI service is currently unavailable. Please try again later."
        
        grade_context = f"for a {grade_level} student" if grade_level else "for a secondary school student"
        
        # Build personalized context
        user_info = ""
        if user_context:
            user_info = f"""
            Student Information:
            - Grade Level: {user_context.get('grade_level', 'Not specified')}
            - Subjects: {', '.join(user_context.get('subjects', []))}
            - Previous Topics: {', '.join(user_context.get('recent_topics', []))}
            """
        
        # Build conversation history context
        history_context = ""
        if conversation_history and len(conversation_history) > 0:
            recent_questions = conversation_history[-3:]  # Last 3 questions
            history_context = f"""
            Recent Conversation History:
            {chr(10).join([f"- Q: {q.get('question', '')} | A: {q.get('ai_response', '')[:100]}..." for q in recent_questions])}
            """
        
        prompt = f"""
        You are a friendly, knowledgeable Nigerian tutor helping students learn.
        
        {user_info}
        
        Subject: {subject}
        Topic: {topic}
        Student's Question: {question}
        
        {history_context}
        
        Please provide a clear, step-by-step explanation {grade_context}. 
        Use simple language and include relevant examples from Nigerian context where appropriate.
        If this is a math problem, show the working steps clearly.
        If this is a science concept, use everyday examples to explain.
        Keep your response encouraging and supportive.
        Reference previous conversations if relevant to build on what the student has learned.
        Limit your response to 300 words.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            return f"I apologize, but I'm having trouble generating an explanation right now. Please try again later. Error: {str(e)}"
    
    def generate_practice_questions(self, subject, topic, difficulty="medium", user_context=None):
        """Generate practice questions for a given topic with user context"""
        
        if not self.model:
            return [{"error": "AI service is currently unavailable"}]
        
        user_info = ""
        if user_context:
            user_info = f"""
            Student Information:
            - Grade Level: {user_context.get('grade_level', 'Not specified')}
            - Subjects: {', '.join(user_context.get('subjects', []))}
            """
        
        prompt = f"""
        Generate 3 practice questions for a Nigerian student studying {subject}, specifically on the topic of {topic}.
        Difficulty level: {difficulty}
        
        {user_info}
        
        Format your response EXACTLY as follows (use proper markdown formatting):
        
        ## Practice Questions for {subject} - {topic}
        
        ### Question 1
        **Question:** [Write a clear, specific question here]
        **Answer:** [Provide the correct answer with explanation]
        **Explanation:** [Give a brief explanation of the solution]
        
        ### Question 2
        **Question:** [Write a clear, specific question here]
        **Answer:** [Provide the correct answer with explanation]
        **Explanation:** [Give a brief explanation of the solution]
        
        ### Question 3
        **Question:** [Write a clear, specific question here]
        **Answer:** [Provide the correct answer with explanation]
        **Explanation:** [Give a brief explanation of the solution]
        
        Make questions relevant to Nigerian context where possible.
        Keep each question concise and educational.
        Adjust difficulty based on the student's grade level.
        Use clear, simple language appropriate for secondary school students.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse response into structured format
            questions = self._parse_questions_response(response.text)
            return questions
        
        except Exception as e:
            return [{"error": f"Unable to generate questions: {str(e)}"}]
    
    def _parse_questions_response(self, response):
        """Parse AI response into structured question format"""
        questions = []
        
        # Split by question sections
        sections = response.split('### Question')
        
        for i, section in enumerate(sections[1:], 1):  # Skip first empty section
            question_dict = {}
            
            # Extract question text
            if '**Question:**' in section:
                question_start = section.find('**Question:**') + 12
                question_end = section.find('**Answer:**')
                if question_end > question_start:
                    question_dict['question'] = section[question_start:question_end].strip()
            
            # Extract answer text
            if '**Answer:**' in section:
                answer_start = section.find('**Answer:**') + 10
                answer_end = section.find('**Explanation:**')
                if answer_end > answer_start:
                    question_dict['answer'] = section[answer_start:answer_end].strip()
            
            # Extract explanation text
            if '**Explanation:**' in section:
                explanation_start = section.find('**Explanation:**') + 15
                explanation_end = section.find('### Question', explanation_start)
                if explanation_end == -1:
                    explanation_end = len(section)
                question_dict['explanation'] = section[explanation_start:explanation_end].strip()
                
            if question_dict and 'question' in question_dict:
                questions.append(question_dict)
        
        # If parsing fails, return a structured fallback
        if not questions:
            return [
                {
                    "question": "Sample question will be generated",
                    "answer": "Sample answer with explanation",
                    "explanation": "Sample explanation of the solution"
                }
            ]
        
        return questions

# Initialize AI service
ai_service = AITutorService()

# Routes
@app.route('/')
def home():
    return jsonify({
        "message": "AI Learning Assistant API",
        "version": "flash",
        "status": "active",
        "endpoints": {
            "auth": "/api/auth/*",
            "ai_tutor": "/api/ai/*",
            "health": "/health"
        }
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print("Registration data received:", data)  # Debug print
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if field not in data:
                print(f"Missing field: {field}")  # Debug print
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if user already exists
        if users_collection.find_one({'username': data['username']}):
            return jsonify({'error': 'Username already exists'}), 400
        
        if users_collection.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Create new user
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'full_name': data['full_name'],
            'grade_level': data.get('grade_level'),
            'subjects': data.get('subjects', []),
            'password_hash': generate_password_hash(data['password']),
            'created_at': datetime.utcnow(),
            'email_verified': False,
            'verification_token': verification_token
        }
        result = users_collection.insert_one(user_data)
        
        # Send verification email
        email_sent = send_verification_email(data['email'], data['full_name'], verification_token)
        
        # Convert ObjectId to string for JSON serialization
        user_data['_id'] = str(result.inserted_id)
        user_data['created_at'] = user_data['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful! Please check your email to verify your account.',
            'email_sent': email_sent,
            'user': user_data
        }), 201
    
    except Exception as e:
        print("Registration error:", str(e))  # Debug print
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify/<token>', methods=['GET'])
def verify_email(token):
    """Verify user email with token"""
    try:
        # Find user with this verification token
        user_data = users_collection.find_one({'verification_token': token})
        
        if not user_data:
            return jsonify({'error': 'Invalid or expired verification token'}), 400
        
        # Update user to verified
        users_collection.update_one(
            {'_id': user_data['_id']},
            {
                '$set': {
                    'email_verified': True,
                    'verification_token': None
                }
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Email verified successfully! You can now login to your account.'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user by username or email
        user_data = users_collection.find_one(
            {'$or': [{'username': data['username']}, {'email': data['username']}]}
        )
        
        if not user_data or not check_password_hash(user_data['password_hash'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if email is verified
        if not user_data.get('email_verified', False):
            return jsonify({'error': 'Please verify your email address before logging in. Check your inbox for the verification link.'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user_data['_id']))
        
        # Convert ObjectId to string for JSON serialization
        user_data['_id'] = str(user_data['_id'])
        user_data['created_at'] = user_data['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'user': user_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# AI Tutor Routes
@app.route('/api/ai/ask', methods=['POST'])
def ask_question():
    """Handle student questions and provide AI-powered explanations"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['subject', 'topic', 'question']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get user info if authenticated
        user_id = None
        grade_level = None
        user_context = None
        conversation_history = []
        
        # Check if user is authenticated (optional for demo)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                from flask_jwt_extended import decode_token
                token = auth_header.split(' ')[1]
                decoded_token = decode_token(token)
                user_id = decoded_token['sub']
                user_data = users_collection.find_one({'_id': ObjectId(user_id)})
                if user_data:
                    grade_level = user_data['grade_level']
                    user_context = {
                        'grade_level': user_data['grade_level'],
                        'subjects': user_data['subjects'],
                        'recent_topics': [] # Placeholder for recent topics
                    }
                    # Fetch recent sessions for context
                    recent_sessions = list(sessions_collection.find({'user_id': user_id}).sort('created_at', -1).limit(5))
                    for session in recent_sessions:
                        conversation_history.append({
                            'question': session['question'],
                            'ai_response': session['ai_response']
                        })
            except:
                pass  # Continue without authentication
        
        # Generate AI explanation
        explanation = ai_service.generate_explanation(
            subject=data['subject'],
            topic=data['topic'],
            question=data['question'],
            grade_level=grade_level,
            user_context=user_context,
            conversation_history=conversation_history
        )
        
        # Save study session
        session_data = {
            'user_id': user_id,
            'subject': data['subject'],
            'topic': data['topic'],
            'question': data['question'],
            'ai_response': explanation,
            'created_at': datetime.utcnow()
        }
        result = sessions_collection.insert_one(session_data)
        
        return jsonify({
            'success': True,
            'session_id': str(result.inserted_id),
            'response': explanation,
            'subject': data['subject'],
            'topic': data['topic'],
            'question': data['question']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/practice', methods=['POST'])
def generate_practice():
    """Generate practice questions for a topic"""
    try:
        data = request.get_json()
        
        # Validate input
        if 'subject' not in data or 'topic' not in data:
            return jsonify({'error': 'Subject and topic are required'}), 400
        
        difficulty = data.get('difficulty', 'medium')
        user_context = None
        
        # Check if user is authenticated (optional for demo)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                from flask_jwt_extended import decode_token
                token = auth_header.split(' ')[1]
                decoded_token = decode_token(token)
                user_id = decoded_token['sub']
                user_data = users_collection.find_one({'_id': ObjectId(user_id)})
                if user_data:
                    user_context = {
                        'grade_level': user_data['grade_level'],
                        'subjects': user_data['subjects']
                    }
            except:
                pass  # Continue without authentication
        
        # Generate practice questions
        questions = ai_service.generate_practice_questions(
            subject=data['subject'],
            topic=data['topic'],
            difficulty=difficulty,
            user_context=user_context
        )
        
        return jsonify({
            'success': True,
            'questions': questions,
            'subject': data['subject'],
            'topic': data['topic'],
            'difficulty': difficulty
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/sessions', methods=['GET'])
@jwt_required()
def get_study_sessions():
    """Get user's study session history"""
    try:
        user_id = get_jwt_identity()
        sessions = list(sessions_collection.find({'user_id': user_id}).sort('created_at', -1).limit(20))
        
        # Convert ObjectIds to strings for JSON serialization
        for session in sessions:
            session['_id'] = str(session['_id'])
            session['created_at'] = session['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/rate/<string:session_id>', methods=['POST'])
def rate_session(session_id):
    """Rate the quality of an AI response"""
    try:
        data = request.get_json()
        
        if 'rating' not in data:
            return jsonify({'error': 'Rating is required'}), 400
        
        rating = data['rating']
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
        
        session = sessions_collection.find_one({'_id': ObjectId(session_id)})
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        sessions_collection.update_one({'_id': ObjectId(session_id)}, {'$set': {'satisfaction_rating': rating}})
        
        return jsonify({
            'success': True,
            'message': 'Rating saved successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Study Groups Routes
@app.route('/api/groups', methods=['GET'])
def get_study_groups():
    """Get available study groups"""
    try:
        # Sample data for demo
        groups = [
            {
                "id": 1,
                "name": "Mathematics SS2",
                "subject": "Mathematics",
                "grade_level": "SS2",
                "members": 15,
                "description": "Advanced algebra and geometry practice"
            },
            {
                "id": 2,
                "name": "Physics Champions",
                "subject": "Physics",
                "grade_level": "SS3",
                "members": 8,
                "description": "JAMB physics preparation group"
            },
            {
                "id": 3,
                "name": "Chemistry Lab",
                "subject": "Chemistry",
                "grade_level": "SS1",
                "members": 12,
                "description": "Organic chemistry study group"
            }
        ]
        
        return jsonify({
            'success': True,
            'groups': groups
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)