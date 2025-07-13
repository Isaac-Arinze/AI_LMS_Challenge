#!/usr/bin/env python3
"""
Script to set up the .env file with email credentials
"""

import os

def create_env_file():
    """Create or update the .env file with the correct configuration"""
    
    env_content = """JWT_SECRET_KEY=I5rQ%*MAXXXuuhV^s7*PhD@Kdowz3sz6blZuHZDZ%yyTthMCt^4
MONGO_URI=mongodb://localhost:27017/
GEMINI_API_KEY=AIzaSyCSOMOijw-uy8Jw69Sn2rR37bPzPPkWazs
FLASK_ENV=development
FLASK_DEBUG=True
MAIL_USERNAME=skytechaiconsulting@gmail.com
MAIL_PASSWORD=iozl ofod rhiy hghy
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file has been created/updated successfully!")
    print("\n📧 Email Configuration:")
    print("   Username: skytechaiconsulting@gmail.com")
    print("   App Password: iozl ofod rhiy hghy")
    print("\n🚀 Next steps:")
    print("   1. Start your backend: python app.py")
    print("   2. Register a new account on your frontend")
    print("   3. Check your email for verification link")
    print("   4. Click the verification link to activate your account")

if __name__ == "__main__":
    create_env_file() 