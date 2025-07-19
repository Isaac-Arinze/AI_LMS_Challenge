# AI Learning Assistant Kubernetes Deployment Script (PowerShell)

param(
    [string]$Registry = "your-registry",
    [string]$ImageTag = "latest",
    [switch]$BuildImages,
    [switch]$SkipPrerequisites
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"

# Configuration
$Namespace = "ai-learning-assistant"

Write-Host "🚀 Starting AI Learning Assistant Kubernetes Deployment" -ForegroundColor $Green

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

# Check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        Write-Error "kubectl is not installed"
        exit 1
    }
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "docker is not installed"
        exit 1
    }
    
    Write-Status "Prerequisites check passed"
}

# Build and push Docker images
function Build-Images {
    Write-Status "Building Docker images..."
    
    Set-Location backend
    docker build -t ${Registry}/ai-learning-assistant-backend:${ImageTag} .
    docker push ${Registry}/ai-learning-assistant-backend:${ImageTag}
    Set-Location ..
    
    Write-Status "Docker images built and pushed"
}

# Update image references in deployment files
function Update-ImageReferences {
    Write-Status "Updating image references..."
    
    # Update backend deployment
    $content = Get-Content k8s/backend-deployment.yaml -Raw
    $content = $content -replace "image: ai-learning-assistant-backend:latest", "image: ${Registry}/ai-learning-assistant-backend:${ImageTag}"
    Set-Content k8s/backend-deployment.yaml $content
    
    Write-Status "Image references updated"
}

# Deploy to Kubernetes
function Deploy-ToK8s {
    Write-Status "Deploying to Kubernetes..."
    
    # Create namespace
    kubectl apply -f k8s/namespace.yaml
    
    # Apply all resources
    kubectl apply -k k8s/
    
    Write-Status "Kubernetes resources deployed"
}

# Wait for deployment
function Wait-ForDeployment {
    Write-Status "Waiting for deployment to be ready..."
    
    # Wait for MongoDB
    kubectl wait --for=condition=available --timeout=300s deployment/mongodb -n ${Namespace}
    
    # Wait for Backend
    kubectl wait --for=condition=available --timeout=300s deployment/backend -n ${Namespace}
    
    # Wait for Frontend
    kubectl wait --for=condition=available --timeout=300s deployment/frontend -n ${Namespace}
    
    Write-Status "All deployments are ready"
}

# Show deployment status
function Show-Status {
    Write-Status "Deployment Status:"
    
    Write-Host ""
    Write-Host "Pods:"
    kubectl get pods -n ${Namespace}
    
    Write-Host ""
    Write-Host "Services:"
    kubectl get svc -n ${Namespace}
    
    Write-Host ""
    Write-Host "Ingress:"
    kubectl get ingress -n ${Namespace}
    
    Write-Host ""
    Write-Host "Horizontal Pod Autoscalers:"
    kubectl get hpa -n ${Namespace}
}

# Get access information
function Show-AccessInfo {
    Write-Status "Access Information:"
    
    Write-Host ""
    Write-Host "Frontend Service:"
    kubectl get svc frontend-service -n ${Namespace} -o wide
    
    Write-Host ""
    Write-Host "Backend Service:"
    kubectl get svc backend-service -n ${Namespace} -o wide
    
    Write-Host ""
    Write-Warning "Remember to update your domain in the ingress configuration"
    Write-Warning "Update k8s/ingress.yaml with your actual domain"
}

# Main deployment function
function Main {
    if (-not $SkipPrerequisites) {
        Test-Prerequisites
    }
    
    if ($BuildImages) {
        Build-Images
        Update-ImageReferences
    }
    
    Deploy-ToK8s
    Wait-ForDeployment
    Show-Status
    Show-AccessInfo
    
    Write-Status "🎉 Deployment completed successfully!"
    Write-Host ""
    Write-Warning "Next steps:"
    Write-Host "1. Update your domain in k8s/ingress.yaml"
    Write-Host "2. Configure SSL certificates if needed"
    Write-Host "3. Set up monitoring and logging"
    Write-Host "4. Configure backups for MongoDB"
}

# Run main function
Main 