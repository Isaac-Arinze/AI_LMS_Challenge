import os
from typing import Dict, List, Optional
import google.generativeai as genai  # type: ignore
import re
import json
import logging

# Removed genai.configure to avoid linter error

# Set up logging
logger = logging.getLogger("gemini")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class AITutorService:
    def __init__(self):
        # type: ignore is used to suppress linter errors for generativeai
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # type: ignore

    def generate_explanation(self, subject: str, topic: str, question: str, grade_level: Optional[str] = None) -> str:
        """Generate AI-powered explanation for student questions"""
        prompt = self._create_explanation_prompt(subject, topic, question, grade_level)
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            text_clean = re.sub(r'^\*+|\*+$', '', text, flags=re.MULTILINE)
            text_clean = re.sub(r'^#+', '', text_clean, flags=re.MULTILINE)
            text_clean = text_clean.strip()
            if not text_clean:
                text_clean = text
            return text_clean
        except Exception as e:
            logger.error(f"Gemini explanation error: {e}")
            return f"Error: {str(e)}"

    def _validate_questions(self, questions, num_questions):
        # Flexible validation for practice questions (explanation-based)
        seen = set()
        valid_questions = []
        for q in questions:
            q_text = q.get('question', '').strip()
            # Accept if both 'question' and 'explanation' fields are present
            if q_text and q_text.lower() not in seen and q.get('explanation'):
                valid_questions.append(q)
                seen.add(q_text.lower())
            else:
                logger.warning(f"Rejected question: {q}")
            if len(valid_questions) == num_questions:
                break
        return valid_questions

    def generate_questions(self, subject: str, topic: str, difficulty: str = "medium", num_questions: int = 5, exam_type: Optional[str] = None, exclude_questions: Optional[list] = None) -> List[Dict]:
        """Unified Gemini-powered question generator for quizzes and practice, with subject/topic enforcement and separation."""
        exam_context = {
            "WAEC": "West African Examinations Council (WAEC) style questions",
            "JAMB": "Joint Admissions and Matriculation Board (JAMB) style questions",
            "NECO": "National Examinations Council (NECO) style questions",
            "IGCSE": "International General Certificate of Secondary Education style questions"
        }
        exclude_text = ''
        if exclude_questions:
            exclude_text = '\nDo NOT repeat or reuse any of these questions:'
            for q in exclude_questions:
                exclude_text += f"\n- {q}"
        if not exam_type or exam_type.lower() == 'practice':
            prompt_template = f'''
Generate {num_questions} practice questions for the subject: {subject}, topic: {topic}.
Requirements:
- Each question must be open-ended and require a written explanation.
- Each question must be unique, not repeated, and strictly related to the subject and topic provided.
- Do NOT use multiple choice, options, or correct answer letters.
- Do NOT include questions from other subjects or topics.
- For each question, provide a clear, step-by-step explanation as the answer.
{exclude_text}
Return as a JSON array:
{{
  "questions": [
    {{
      "question": "...",
      "explanation": "..."
    }}
  ]
}}
Make sure the JSON is valid and properly formatted.
'''
        else:
            style = exam_context.get(exam_type, exam_context["WAEC"])
            prompt_template = f'''
Generate {num_questions} unique multiple choice questions for the subject: {subject}, topic: {topic}.
Requirements:
- Each question must be different, not repeated, and strictly related to the subject and topic provided.
- Each question must be unique and not similar to any other in the set.
- Style: {style}
- Difficulty: {difficulty}
- Format: Each question should have 4 options (A, B, C, D)
- Include explanations for correct answers
- Questions should be objective and test understanding
- Use Nigerian context where appropriate
- For each question, specify the exam type (e.g., 'WAEC', 'JAMB', 'NECO') and the year (e.g., '2019', '2021') the question is drafted from. Use realistic years between 2015 and 2023. If the question is not from a real past exam, make a plausible year and type.
- Do NOT include any questions from other subjects or topics.
{exclude_text}
You must return exactly {num_questions} unique questions in a valid JSON array as shown below. Do not repeat any question. Do not return only one question. Each question must have exam_type and exam_year fields.
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
            "topic": "{topic}",
            "exam_type": "{exam_type}",
            "exam_year": "2019"
        }}
    ]
}}
Make sure the JSON is valid and properly formatted.
'''
        max_attempts = 3
        attempts = 0
        last_error = None
        logger.info(f"Gemini subject: {subject}, topic: {topic}, exam_type: {exam_type}, num_questions: {num_questions}")
        while attempts < max_attempts:
            prompt = prompt_template
            logger.info(f"Gemini prompt: {prompt}")
            try:
                response = self.model.generate_content(prompt)
                response_text = response.text.strip()
                logger.info(f"Gemini raw response: {response_text}")
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif '```' in response_text:
                    json_start = response_text.find('```') + 3
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                response_text = self._repair_json(response_text)
                questions_data = json.loads(response_text)
                logger.info(f"Parsed questions: {questions_data.get('questions', [])}")
                questions = questions_data.get('questions', [])
                valid_questions = self._validate_questions(questions, num_questions)
                if valid_questions:
                    return valid_questions
                else:
                    logger.warning(f"Gemini did not return any valid questions.")
            except Exception as e:
                logger.error(f"Error generating questions: {e}")
                last_error = str(e)
            attempts += 1
        logger.warning(f"Falling back to static questions after {attempts} attempts. Last error: {last_error}")
        fallback = self._get_fallback_questions(subject, topic, num_questions, exam_type)
        return fallback

    def _create_explanation_prompt(self, subject: str, topic: str, question: str, grade_level: Optional[str]) -> str:
        grade_context = f"for a {grade_level} student" if grade_level else "for a secondary school student"
        return f'''
Subject: {subject}
Topic: {topic}
Student's Question: {question}

Please provide a clear, step-by-step explanation {grade_context}. 
Use simple language. Focus on the calculation and final answer. Answer concisely in 2-4 sentences. Do not include extra examples or encouragement.
'''

    def _repair_json(self, text: str) -> str:
        text = re.sub(r',([ \t\r\n]*[}}\]])', r'\1', text)
        text = text.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
        return text

    def _get_fallback_questions(self, subject, topic, num_questions, exam_type):
        # Subject-specific, explanation-based fallback questions
        fallback_questions = {
            "Mathematics": [
                {
                    "question": f"What is the value of x in the equation 2x + 5 = 13?",
                    "explanation": "2x + 5 = 13 → 2x = 8 → x = 4."
                },
                {
                    "question": f"What is the square root of 81?",
                    "explanation": "The square root of 81 is 9."
                }
            ],
            "Physics": [
                {
                    "question": "What is the SI unit of force?",
                    "explanation": "The SI unit of force is the Newton (N)."
                },
                {
                    "question": "What is the acceleration due to gravity on Earth?",
                    "explanation": "The standard acceleration due to gravity is 9.8 m/s²."
                }
            ],
            "Chemistry": [
                {
                    "question": "What is the chemical symbol for gold?",
                    "explanation": "The chemical symbol for gold is Au."
                },
                {
                    "question": "What is the pH of a neutral solution?",
                    "explanation": "A neutral solution has a pH of 7."
                }
            ],
            "Economics": [
                {
                    "question": "What is opportunity cost?",
                    "explanation": "Opportunity cost is the value of the next best alternative forgone when a choice is made."
                },
                {
                    "question": "Define demand in economics.",
                    "explanation": "Demand is the quantity of a good or service that consumers are willing and able to buy at a given price over a period of time."
                }
            ],
            "Government": [
                {
                    "question": "What is separation of powers?",
                    "explanation": "Separation of powers is the division of government responsibilities into distinct branches to prevent any one branch from exercising the core functions of another."
                },
                {
                    "question": "Define democracy.",
                    "explanation": "Democracy is a system of government where the citizens exercise power by voting."
                }
            ],
            "Literature": [
                {
                    "question": "What is a metaphor in literature?",
                    "explanation": "A metaphor is a figure of speech that describes an object or action in a way that isn’t literally true, but helps explain an idea or make a comparison."
                },
                {
                    "question": "Define protagonist.",
                    "explanation": "The protagonist is the main character in a story, often considered the hero or the central figure."
                }
            ],
            "Biology": [
                {
                    "question": "What is photosynthesis?",
                    "explanation": "Photosynthesis is the process by which green plants use sunlight to synthesize food from carbon dioxide and water."
                },
                {
                    "question": "Define osmosis.",
                    "explanation": "Osmosis is the movement of water molecules from a region of lower solute concentration to a region of higher solute concentration through a semi-permeable membrane."
                }
            ],
            "English": [
                {
                    "question": "What is a noun?",
                    "explanation": "A noun is a word that names a person, place, thing, or idea."
                },
                {
                    "question": "Define a simile.",
                    "explanation": "A simile is a figure of speech that compares two different things using the words 'like' or 'as'."
                }
            ]
        }
        # Use subject-specific fallback, or generic if not found
        fallback = fallback_questions.get(subject, [
            {
                "question": f"Provide a key concept in {subject} on the topic '{topic}'.",
                "explanation": f"This is a general explanation for a key concept in {subject} on the topic '{topic}'."
            }
        ])
        # Repeat and slice to get the required number of questions
        result = (fallback * ((num_questions // len(fallback)) + 1))[:num_questions]
        return result
