from datetime import datetime
from bson import ObjectId
from typing import List, Dict, Optional

class Quiz:
    def __init__(self, quiz_data):
        self.id = quiz_data['_id']
        self.title = quiz_data['title']
        self.subject = quiz_data['subject']
        self.topic = quiz_data['topic']
        self.difficulty = quiz_data['difficulty']
        self.questions = quiz_data['questions']
        self.time_limit = quiz_data.get('time_limit', 30)  # minutes
        self.passing_score = quiz_data.get('passing_score', 70)
        self.created_at = quiz_data['created_at']
        self.created_by = quiz_data.get('created_by', 'system')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'questions': self.questions,
            'time_limit': self.time_limit,
            'passing_score': self.passing_score,
            'created_at': self.created_at,
            'created_by': self.created_by
        }

class QuizAttempt:
    def __init__(self, attempt_data):
        self.id = attempt_data['_id']
        self.user_id = attempt_data['user_id']
        self.quiz_id = attempt_data['quiz_id']
        self.answers = attempt_data['answers']
        self.score = attempt_data['score']
        self.total_questions = attempt_data['total_questions']
        self.correct_answers = attempt_data['correct_answers']
        self.time_taken = attempt_data.get('time_taken', 0)  # in seconds
        self.completed = attempt_data.get('completed', False)
        self.started_at = attempt_data['started_at']
        self.completed_at = attempt_data.get('completed_at')
        self.passed = attempt_data.get('passed', False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'answers': self.answers,
            'score': self.score,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'time_taken': self.time_taken,
            'completed': self.completed,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'passed': self.passed
        }

class QuizQuestion:
    def __init__(self, question_data):
        self.id = question_data.get('id', str(ObjectId()))
        self.question = question_data['question']
        self.options = question_data['options']
        self.correct_answer = question_data['correct_answer']
        self.explanation = question_data.get('explanation', '')
        self.difficulty = question_data.get('difficulty', 'medium')
        self.topic = question_data.get('topic', '')
    
    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'topic': self.topic
        } 