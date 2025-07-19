# AI Learning Assistant - Kubernetes Deployment Guide

This guide will help you deploy the AI Learning Assistant to Kubernetes.

## Prerequisites

1. **Kubernetes Cluster**: A running Kubernetes cluster (local or cloud)
2. **kubectl**: Kubernetes command-line tool
3. **Docker**: For building and pushing images
4. **NGINX Ingress Controller**: For external access
5. **Metrics Server**: For HPA (Horizontal Pod Autoscaler)

## Setting Up Kubernetes on Windows

If you don't have a Kubernetes cluster running, you can set up a local one:

### Option 1: Docker Desktop (Recommended)

1. **Install Docker Desktop** from https://www.docker.com/products/docker-desktop
2. **Enable Kubernetes** in Docker Desktop:
   - Open Docker Desktop
   - Go to Settings > Kubernetes
   - Check "Enable Kubernetes"
   - Click "Apply & Restart"
3. **Run the setup script**:
   ```powershell
   .\setup-k8s.ps1 -ClusterType DockerDesktop
   ```

### Option 2: Minikube

1. **Run the setup script**:
   ```powershell
   .\setup-k8s.ps1 -ClusterType Minikube
   ```

### Option 3: Kind

1. **Run the setup script**:
   ```powershell
   .\setup-k8s.ps1 -ClusterType Kind
   ```

### Manual Setup

If you prefer to set up manually:

```powershell
# Check if kubectl is installed
kubectl version --client

# If not installed, download from:
# https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/

# For Docker Desktop, just enable Kubernetes in settings
# For Minikube:
# choco install minikube
# minikube start --driver=docker

# For Kind:
# choco install kind
# kind create cluster --name ai-learning-assistant
```

## Configuration

The Kubernetes manifests have been pre-configured with your actual values:

- **JWT_SECRET_KEY**: `I5rQ%*MAXXXuuhV^s7*PhD@Kdowz3sz6blZuHZDZ%yyTthMCt^4`
- **GEMINI_API_KEY**: `AIzaSyCSOMOijw-uy8Jw69Sn2rR37bPzPPkWazs`
- **MAIL_USERNAME**: `skytechaiconsulting@gmail.com`
- **MAIL_PASSWORD**: `iozl ofod rhiy hghy`
- **FLASK_ENV**: `development`
- **FLASK_DEBUG**: `True`

## Quick Start

### 1. Build and Push Docker Images

```bash
# Build the backend image
cd ai-learning-assistant/backend
docker build -t ai-learning-assistant-backend:latest .

# Tag for your registry (replace with your registry)
docker tag ai-learning-assistant-backend:latest your-registry/ai-learning-assistant-backend:latest

# Push to registry
docker push your-registry/ai-learning-assistant-backend:latest
```

### 2. Deploy to Kubernetes

#### Using PowerShell (Windows):
```powershell
# Navigate to the k8s directory
cd ai-learning-assistant/k8s

# Run the deployment script
.\deploy.ps1 -BuildImages

# Or without building images
.\deploy.ps1
```

#### Using kubectl directly:
```bash
# Apply all resources
kubectl apply -k k8s/

# Or apply individually
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/mongodb-persistent-volume.yaml
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

### 3. Verify Deployment

```bash
# Check all resources
kubectl get all -n ai-learning-assistant

# Check pods status
kubectl get pods -n ai-learning-assistant

# Check services
kubectl get svc -n ai-learning-assistant

# Check ingress
kubectl get ingress -n ai-learning-assistant
```

### 4. Access the Application

```bash
# Get the external IP
kubectl get svc frontend-service -n ai-learning-assistant

# Or if using ingress
kubectl get ingress -n ai-learning-assistant
```

## Configuration

### Environment Variables

The application uses the following environment variables:

- `MONGO_URI`: MongoDB connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `GEMINI_API_KEY`: Google Gemini API key
- `MAIL_USERNAME`: Gmail username for email verification
- `MAIL_PASSWORD`: Gmail app password
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Flask debug mode

### Scaling

The application includes Horizontal Pod Autoscalers:

- **Backend**: 2-10 replicas based on CPU (70%) and Memory (80%)
- **Frontend**: 2-5 replicas based on CPU (70%) and Memory (80%)

### Storage

MongoDB uses persistent storage with:
- 10Gi persistent volume
- Local storage class (modify for cloud providers)

## Monitoring and Logs

```bash
# View logs
kubectl logs -f deployment/backend -n ai-learning-assistant
kubectl logs -f deployment/frontend -n ai-learning-assistant
kubectl logs -f deployment/mongodb -n ai-learning-assistant

# Check resource usage
kubectl top pods -n ai-learning-assistant
```

## Troubleshooting

### Common Issues

1. **Image Pull Errors**: Ensure images are pushed to your registry
2. **Secret Issues**: Verify all secrets are properly base64 encoded
3. **Storage Issues**: Check if persistent volumes are available
4. **Ingress Issues**: Ensure NGINX Ingress Controller is installed

### Debug Commands

```bash
# Describe resources
kubectl describe pod <pod-name> -n ai-learning-assistant
kubectl describe service <service-name> -n ai-learning-assistant

# Port forward for debugging
kubectl port-forward svc/backend-service 5000:5000 -n ai-learning-assistant
kubectl port-forward svc/frontend-service 8080:80 -n ai-learning-assistant
```

## Production Considerations

1. **SSL/TLS**: Configure SSL certificates for ingress
2. **Backup**: Set up MongoDB backups
3. **Monitoring**: Install monitoring tools (Prometheus, Grafana)
4. **Logging**: Configure centralized logging
5. **Security**: Use network policies and RBAC
6. **Resource Limits**: Adjust based on your cluster capacity

## Cleanup

```bash
# Delete all resources
kubectl delete -k k8s/

# Or delete namespace (deletes everything in namespace)
kubectl delete namespace ai-learning-assistant
```

## Customization

### For Different Cloud Providers

- **AWS**: Use EBS storage class
- **GCP**: Use GCE persistent disk
- **Azure**: Use Azure disk storage
- **Minikube**: Use hostPath storage (as configured)

### For Different Domains

Update the ingress host in `k8s/ingress.yaml`:
```yaml
host: your-domain.com
```

### For Different Image Registries

Update the image references in deployment files:
```yaml
image: your-registry/ai-learning-assistant-backend:latest
``` 