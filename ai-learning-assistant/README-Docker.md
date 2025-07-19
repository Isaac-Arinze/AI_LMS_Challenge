# AI Learning Assistant - Docker Setup Guide

This guide will help you set up and run the AI Learning Assistant using Docker and Docker Compose.

## 🐳 Prerequisites

- Docker Desktop installed and running
- Docker Compose (usually comes with Docker Desktop)
- Git (to clone the repository)

## 📋 Quick Start

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd AI_Challenge/ai-learning-assistant
```

### 2. Set Up Environment Variables
```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your actual values
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
- `GEMINI_API_KEY`: Your Google Gemini AI API key
- `MAIL_USERNAME`: Your Gmail address (for email verification)
- `MAIL_PASSWORD`: Your Gmail app password
- `JWT_SECRET_KEY`: A secure secret key for JWT tokens

### 3. Build and Run
```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 4. Access the Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **MongoDB**: localhost:27017

## 🏗️ Architecture

The Docker setup includes:

### Services
1. **MongoDB** (Database)
   - Port: 27017
   - Persistent data storage
   - Authentication enabled

2. **Backend** (Flask API)
   - Port: 5000
   - Python 3.11
   - Gunicorn WSGI server
   - Health checks enabled

3. **Frontend** (Nginx)
   - Port: 80
   - Static file serving
   - API proxy to backend
   - CORS handling

### Networks
- `ai_lms_network`: Internal network for service communication

### Volumes
- `mongodb_data`: Persistent MongoDB data

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# MongoDB Configuration
MONGO_URI=mongodb://admin:password123@mongodb:27017/learning_assistant?authSource=admin

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Google Gemini AI API
GEMINI_API_KEY=your-gemini-api-key-here

# Email Configuration (Gmail)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Flask Configuration
FLASK_ENV=production
FLASK_APP=app.py
```

### Docker Compose Services

The `docker-compose.yml` file defines three services:

1. **mongodb**: MongoDB database with authentication
2. **backend**: Flask API with Gunicorn
3. **frontend**: Nginx serving static files and proxying API

## 🚀 Deployment Commands

### Development
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production
```bash
# Build and start in production mode
docker-compose -f docker-compose.yml up -d --build

# Scale backend service
docker-compose up -d --scale backend=3

# Update services
docker-compose pull
docker-compose up -d
```

## 🔍 Monitoring and Debugging

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs mongodb
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f backend
```

### Health Checks
```bash
# Check service health
docker-compose ps

# Test API health
curl http://localhost:5000/health

# Test frontend
curl http://localhost
```

### Database Access
```bash
# Connect to MongoDB
docker-compose exec mongodb mongosh -u admin -p password123

# Backup database
docker-compose exec mongodb mongodump --out /backup
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :5000
   
   # Change ports in docker-compose.yml
   ports:
     - "5001:5000"  # Use different host port
   ```

2. **MongoDB Connection Issues**
   ```bash
   # Check MongoDB logs
   docker-compose logs mongodb
   
   # Restart MongoDB
   docker-compose restart mongodb
   ```

3. **Backend Build Failures**
   ```bash
   # Clean build
   docker-compose build --no-cache backend
   
   # Check requirements
   docker-compose exec backend pip list
   ```

4. **Environment Variables Not Loading**
   ```bash
   # Check environment
   docker-compose exec backend env
   
   # Restart with new env
   docker-compose down
   docker-compose up -d
   ```

### Performance Optimization

1. **Resource Limits**
   ```yaml
   # Add to docker-compose.yml
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 1G
             cpus: '0.5'
   ```

2. **Caching**
   ```bash
   # Use Docker layer caching
   docker-compose build --parallel
   ```

## 🔒 Security Considerations

1. **Change Default Passwords**
   - Update MongoDB credentials
   - Use strong JWT secret
   - Secure environment variables

2. **Network Security**
   - Use internal networks
   - Limit exposed ports
   - Enable SSL/TLS in production

3. **Container Security**
   - Run as non-root user
   - Regular security updates
   - Image vulnerability scanning

## 📊 Production Deployment

### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml ai_lms

# Scale services
docker service scale ai_lms_backend=3
```

### Using Kubernetes
```bash
# Convert to Kubernetes manifests
kompose convert -f docker-compose.yml

# Apply to cluster
kubectl apply -f k8s/
```

## 🧪 Testing

### API Testing
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test AI endpoint
curl -X POST http://localhost:5000/api/ai/demo/ask \
  -H "Content-Type: application/json" \
  -d '{"subject":"Mathematics","topic":"Algebra","question":"What is 2x + 3 = 7?"}'
```

### Load Testing
```bash
# Install Apache Bench
apt-get install apache2-utils

# Test API performance
ab -n 1000 -c 10 http://localhost:5000/health
```

## 📝 Maintenance

### Regular Tasks
1. **Update Dependencies**
   ```bash
   docker-compose pull
   docker-compose build --no-cache
   ```

2. **Database Backups**
   ```bash
   docker-compose exec mongodb mongodump --out /backup
   ```

3. **Log Rotation**
   ```bash
   # Configure log rotation in nginx.conf
   ```

4. **Security Updates**
   ```bash
   # Update base images
   docker-compose build --pull
   ```

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify environment variables: `docker-compose exec backend env`
3. Test individual services: `docker-compose exec backend python app.py`
4. Check network connectivity: `docker network ls`

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Nginx Documentation](https://nginx.org/en/docs/) 