// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the learning_assistant database
db = db.getSiblingDB('learning_assistant');

// Create collections with validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["username", "email", "password_hash", "full_name"],
      properties: {
        username: {
          bsonType: "string",
          description: "Username must be a string and is required"
        },
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
          description: "Email must be a valid email format"
        },
        password_hash: {
          bsonType: "string",
          description: "Password hash must be a string"
        },
        full_name: {
          bsonType: "string",
          description: "Full name must be a string"
        },
        grade_level: {
          bsonType: "string",
          description: "Grade level must be a string"
        },
        subjects: {
          bsonType: "array",
          description: "Subjects must be an array"
        },
        created_at: {
          bsonType: "date",
          description: "Created at must be a date"
        },
        email_verified: {
          bsonType: "bool",
          description: "Email verified must be a boolean"
        }
      }
    }
  }
});

db.createCollection('study_sessions', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "subject", "topic", "question", "ai_response"],
      properties: {
        user_id: {
          bsonType: "objectId",
          description: "User ID must be an ObjectId"
        },
        subject: {
          bsonType: "string",
          description: "Subject must be a string"
        },
        topic: {
          bsonType: "string",
          description: "Topic must be a string"
        },
        question: {
          bsonType: "string",
          description: "Question must be a string"
        },
        ai_response: {
          bsonType: "string",
          description: "AI response must be a string"
        },
        satisfaction_rating: {
          bsonType: "int",
          minimum: 1,
          maximum: 5,
          description: "Satisfaction rating must be an integer between 1 and 5"
        },
        created_at: {
          bsonType: "date",
          description: "Created at must be a date"
        }
      }
    }
  }
});

db.createCollection('quizzes', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "subject", "topic", "questions"],
      properties: {
        title: {
          bsonType: "string",
          description: "Quiz title must be a string"
        },
        subject: {
          bsonType: "string",
          description: "Subject must be a string"
        },
        topic: {
          bsonType: "string",
          description: "Topic must be a string"
        },
        difficulty: {
          bsonType: "string",
          enum: ["easy", "medium", "hard"],
          description: "Difficulty must be one of: easy, medium, hard"
        },
        questions: {
          bsonType: "array",
          description: "Questions must be an array"
        },
        created_at: {
          bsonType: "date",
          description: "Created at must be a date"
        }
      }
    }
  }
});

db.createCollection('quiz_attempts', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "quiz_id", "answers"],
      properties: {
        user_id: {
          bsonType: "objectId",
          description: "User ID must be an ObjectId"
        },
        quiz_id: {
          bsonType: "objectId",
          description: "Quiz ID must be an ObjectId"
        },
        answers: {
          bsonType: "object",
          description: "Answers must be an object"
        },
        score: {
          bsonType: "int",
          minimum: 0,
          description: "Score must be a non-negative integer"
        },
        completed_at: {
          bsonType: "date",
          description: "Completed at must be a date"
        }
      }
    }
  }
});

// Create indexes for better performance
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });
db.study_sessions.createIndex({ "user_id": 1, "created_at": -1 });
db.quizzes.createIndex({ "subject": 1, "topic": 1 });
db.quiz_attempts.createIndex({ "user_id": 1, "quiz_id": 1 });

print("MongoDB initialization completed successfully!");
print("Collections created: users, study_sessions, quizzes, quiz_attempts");
print("Indexes created for better performance"); 