import os
from typing import Dict, List, Optional
import google.generativeai as genai
import re

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class AITutorService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_explanation(self, subject: str, topic: str, question: str, grade_level: Optional[str] = None) -> str:
        """Generate AI-powered explanation for student questions"""
        
        # Create context-aware prompt
        prompt = self._create_explanation_prompt(subject, topic, question, grade_level)
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Remove asterisks only at the start/end of lines and markdown headers
            text_clean = re.sub(r'^\*+|\*+$', '', text, flags=re.MULTILINE)
            text_clean = re.sub(r'^#+', '', text_clean, flags=re.MULTILINE)
            text_clean = text_clean.strip()
            # If cleaning removed everything, fall back to original
            if not text_clean:
                text_clean = text
            return text_clean
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_practice_questions(self, subject: str, topic: str, difficulty: str = "medium", exam_type: Optional[str] = None) -> List[Dict]:
        """Generate practice questions for a given topic"""
        
        if exam_type:
            prompt = f"""
            Generate 3 practice questions based on {exam_type} standards for a Nigerian student studying {subject}, specifically on the topic of {topic}.
            Difficulty level: {difficulty}
            
            Format each question as:
            Question: [question text]
            Answer: [correct answer]
            Explanation: [brief explanation]
            
            Make questions relevant to Nigerian context where possible.
            """
        else:
            prompt = f"""
            Generate 3 practice questions for a Nigerian student studying {subject}, specifically on the topic of {topic}.
            Difficulty level: {difficulty}
            
            Format each question as:
            Question: [question text]
            Answer: [correct answer]
            Explanation: [brief explanation]
            
            Make questions relevant to Nigerian context where possible.
            """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse response into structured format
            questions = self._parse_questions_response(response.text)
            return questions
        
        except Exception as e:
            return [{"error": f"Unable to generate questions: {str(e)}"}]
    
    def _create_explanation_prompt(self, subject: str, topic: str, question: str, grade_level: Optional[str]) -> str:
        """Create a context-aware prompt for explanations"""
        
        grade_context = f"for a {grade_level} student" if grade_level else "for a secondary school student"
        
        return f"""
        Subject: {subject}
        Topic: {topic}
        Student's Question: {question}
        
        Please provide a clear, step-by-step explanation {grade_context}. 
        Use simple language. Focus on the calculation and final answer. Answer concisely in 2-4 sentences. Do not include extra examples or encouragement.
        """
    
    def _parse_questions_response(self, response: str) -> List[Dict]:
        """Parse AI response into structured question format"""
        questions = []
        # Simple parsing logic - in production, you'd want more robust parsing
        sections = response.split('\n\n')
        
        for section in sections:
            if 'Question:' in section:
                question_dict = {}
                lines = section.split('\n')
                for line in lines:
                    if line.startswith('Question:'):
                        question_dict['question'] = line.replace('Question:', '').strip()
                    elif line.startswith('Answer:'):
                        question_dict['answer'] = line.replace('Answer:', '').strip()
                    elif line.startswith('Explanation:'):
                        question_dict['explanation'] = line.replace('Explanation:', '').strip()
                
                if question_dict:
                    questions.append(question_dict)
        
        return questions
