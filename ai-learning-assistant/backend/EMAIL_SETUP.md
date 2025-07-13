# Email Setup Guide for AI Tutor Pro

## Gmail Setup (Recommended)

### 1. Enable 2-Factor Authentication
- Go to your Google Account settings
- Enable 2-Factor Authentication

### 2. Generate App Password
- Go to Google Account → Security → App passwords
- Generate a new app password for "Mail"
- Copy the 16-character password

### 3. Update Your .env File
Add these lines to your `.env` file:

```
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
```

### 4. Install Dependencies
```bash
pip install flask-mail
```

## Alternative: Use a Test Email Service

For development, you can use services like:
- **Mailtrap** (for testing)
- **SendGrid** (free tier available)
- **Mailgun** (free tier available)

## Testing Email Functionality

1. Start your backend server
2. Register a new account
3. Check your email for verification link
4. Click the verification link
5. Try logging in

## Troubleshooting

### Common Issues:
- **"Authentication failed"**: Check your app password
- **"Connection refused"**: Check your internet connection
- **"Email not received"**: Check spam folder

### For Development:
If you don't want to set up real email, you can temporarily disable email verification by commenting out the email check in the login route. 