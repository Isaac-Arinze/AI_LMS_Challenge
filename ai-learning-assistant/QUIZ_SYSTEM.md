# Quiz System Documentation

## Overview

The Quiz System is a comprehensive feature that allows students to take objective questions similar to WAEC, JAMB, and other internationally recognized exams. It provides a complete quiz-taking experience with AI-generated questions, timer, scoring, and detailed results.

## Features

### 🎯 Core Features

1. **AI-Generated Questions**: Questions are generated using Google's Gemini AI, styled after standard Nigerian exams
2. **Multiple Exam Types**: Support for WAEC, JAMB, NECO, and IGCSE question styles
3. **Timer System**: Configurable time limits with visual warnings
4. **Progress Tracking**: Real-time progress indicators and question navigation
5. **Detailed Scoring**: Comprehensive scoring with explanations for each answer
6. **Attempt History**: Track all quiz attempts and performance over time

### 📊 Quiz Types

- **WAEC Style**: West African Examinations Council format
- **JAMB Style**: Joint Admissions and Matriculation Board format  
- **NECO Style**: National Examinations Council format
- **IGCSE Style**: International General Certificate of Secondary Education format

### 🎨 User Interface

- **Modern Design**: Clean, responsive interface with smooth animations
- **Question Navigation**: Easy navigation between questions with visual indicators
- **Timer Display**: Real-time countdown with color-coded warnings
- **Results Dashboard**: Comprehensive results with detailed explanations

## Technical Architecture

### Backend Components

#### Models (`models/quiz.py`)
- `Quiz`: Main quiz data structure
- `QuizAttempt`: User attempt tracking
- `QuizQuestion`: Individual question structure

#### Routes (`routes/quiz.py`)
- `POST /api/quiz/generate`: Generate new quiz
- `GET /api/quiz/<quiz_id>`: Get quiz details
- `POST /api/quiz/start/<quiz_id>`: Start quiz attempt
- `POST /api/quiz/submit/<attempt_id>`: Submit quiz answers
- `GET /api/quiz/attempts`: Get user attempt history
- `GET /api/quiz/available`: Get available quizzes

#### AI Service
- Uses Google Gemini AI for question generation
- Fallback questions for reliability
- Exam-specific prompting for authentic questions

### Frontend Components

#### JavaScript (`assets/js/quiz.js`)
- `QuizSystem` class manages all quiz functionality
- Real-time timer and progress tracking
- Dynamic question display and navigation
- Results visualization

#### CSS (`assets/css/components.css`)
- Responsive quiz interface styles
- Timer animations and warnings
- Question navigation indicators
- Results dashboard styling

## Setup Instructions

### Backend Setup

1. **Install Dependencies**:
   ```bash
   cd ai-learning-assistant/backend
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   ```bash
   # Add to your .env file
   GEMINI_API_KEY=your_gemini_api_key
   MONGO_URI=mongodb://localhost:27017/
   JWT_SECRET_KEY=your_jwt_secret
   ```

3. **Start Backend**:
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Serve Frontend**:
   ```bash
   cd frontend
   python -m http.server 8000
   ```

2. **Access Quiz Section**:
   - Navigate to `http://localhost:8000`
   - Click "Quizzes" in the navigation
   - Login to access quiz features

## Usage Guide

### Creating a Quiz

1. **Select Subject**: Choose from Mathematics, Physics, Chemistry, Biology, English, Literature, Economics, Government
2. **Enter Topic**: Specify the specific topic (e.g., "Quadratic Equations", "Force and Motion")
3. **Choose Difficulty**: Easy, Medium, or Hard
4. **Select Exam Type**: WAEC, JAMB, NECO, or IGCSE
5. **Set Question Count**: 5, 10, 15, or 20 questions
6. **Generate Quiz**: Click "Generate Quiz" to create AI-powered questions

### Taking a Quiz

1. **Quiz Interface**: Clean, distraction-free interface
2. **Question Navigation**: Use Previous/Next buttons or click question indicators
3. **Timer**: Real-time countdown with color-coded warnings
   - Green: Normal time
   - Yellow: 10 minutes remaining
   - Red: 5 minutes remaining (pulsing animation)
4. **Answer Selection**: Click on options to select answers
5. **Progress Tracking**: Visual indicators show answered vs unanswered questions

### Quiz Results

1. **Score Display**: Large circular score indicator
2. **Pass/Fail Status**: Clear pass/fail indication
3. **Detailed Results**: Question-by-question breakdown
4. **Explanations**: AI-generated explanations for correct answers
5. **Action Options**: Retake quiz or create new quiz

## API Endpoints

### Quiz Generation
```http
POST /api/quiz/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "subject": "Mathematics",
  "topic": "Quadratic Equations",
  "difficulty": "medium",
  "exam_type": "WAEC",
  "num_questions": 10
}
```

### Start Quiz
```http
POST /api/quiz/start/<quiz_id>
Authorization: Bearer <token>
```

### Submit Quiz
```http
POST /api/quiz/submit/<attempt_id>
Authorization: Bearer <token>
Content-Type: application/json

{
  "answers": {"0": "A", "1": "B", "2": "C"},
  "time_taken": 1800
}
```

### Get Quiz Details
```http
GET /api/quiz/<quiz_id>
Authorization: Bearer <token>
```

## Database Schema

### Quizzes Collection
```javascript
{
  _id: ObjectId,
  title: String,
  subject: String,
  topic: String,
  difficulty: String,
  questions: Array,
  time_limit: Number,
  passing_score: Number,
  created_at: Date,
  created_by: String
}
```

### Quiz Attempts Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  quiz_id: ObjectId,
  answers: Object,
  score: Number,
  total_questions: Number,
  correct_answers: Number,
  time_taken: Number,
  completed: Boolean,
  started_at: Date,
  completed_at: Date,
  passed: Boolean
}
```

## Security Features

1. **Authentication Required**: All quiz operations require valid JWT token
2. **Answer Protection**: Correct answers are hidden from frontend
3. **Attempt Validation**: Prevents multiple incomplete attempts
4. **Time Tracking**: Accurate time tracking for fair assessment

## Performance Features

1. **AI Fallback**: Reliable fallback questions if AI generation fails
2. **Caching**: Quiz questions cached for better performance
3. **Progressive Loading**: Questions loaded as needed
4. **Responsive Design**: Works on all device sizes

## Testing

Run the test script to verify functionality:
```bash
cd ai-learning-assistant/backend
python test_quiz.py
```

## Future Enhancements

1. **Question Bank**: Pre-generated question database
2. **Performance Analytics**: Detailed performance tracking
3. **Study Recommendations**: AI-powered study suggestions
4. **Competitive Features**: Leaderboards and challenges
5. **Offline Support**: Download quizzes for offline use

## Troubleshooting

### Common Issues

1. **Quiz Generation Fails**:
   - Check Gemini API key
   - Verify internet connection
   - Check server logs for errors

2. **Timer Issues**:
   - Clear browser cache
   - Check JavaScript console for errors

3. **Authentication Problems**:
   - Verify JWT token is valid
   - Check token expiration

4. **Database Issues**:
   - Verify MongoDB connection
   - Check collection permissions

## Support

For technical support or feature requests, please contact the development team or create an issue in the project repository. 