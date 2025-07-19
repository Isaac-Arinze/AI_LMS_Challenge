#!/bin/bash

# AI Learning Assistant Kubernetes Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="ai-learning-assistant"
REGISTRY="your-registry"  # Change this to your registry
IMAGE_TAG="latest"

echo -e "${GREEN}🚀 Starting AI Learning Assistant Kubernetes Deployment${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "docker is not installed"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Build and push Docker images
build_images() {
    print_status "Building Docker images..."
    
    cd backend
    docker build -t ${REGISTRY}/ai-learning-assistant-backend:${IMAGE_TAG} .
    docker push ${REGISTRY}/ai-learning-assistant-backend:${IMAGE_TAG}
    cd ..
    
    print_status "Docker images built and pushed"
}

# Update image references in deployment files
update_image_references() {
    print_status "Updating image references..."
    
    # Update backend deployment
    sed -i "s|image: ai-learning-assistant-backend:latest|image: ${REGISTRY}/ai-learning-assistant-backend:${IMAGE_TAG}|g" k8s/backend-deployment.yaml
    
    print_status "Image references updated"
}

# Deploy to Kubernetes
deploy_to_k8s() {
    print_status "Deploying to Kubernetes..."
    
    # Create namespace
    kubectl apply -f k8s/namespace.yaml
    
    # Apply all resources
    kubectl apply -k k8s/
    
    print_status "Kubernetes resources deployed"
}

# Wait for deployment
wait_for_deployment() {
    print_status "Waiting for deployment to be ready..."
    
    # Wait for MongoDB
    kubectl wait --for=condition=available --timeout=300s deployment/mongodb -n ${NAMESPACE}
    
    # Wait for Backend
    kubectl wait --for=condition=available --timeout=300s deployment/backend -n ${NAMESPACE}
    
    # Wait for Frontend
    kubectl wait --for=condition=available --timeout=300s deployment/frontend -n ${NAMESPACE}
    
    print_status "All deployments are ready"
}

# Show deployment status
show_status() {
    print_status "Deployment Status:"
    
    echo ""
    echo "Pods:"
    kubectl get pods -n ${NAMESPACE}
    
    echo ""
    echo "Services:"
    kubectl get svc -n ${NAMESPACE}
    
    echo ""
    echo "Ingress:"
    kubectl get ingress -n ${NAMESPACE}
    
    echo ""
    echo "Horizontal Pod Autoscalers:"
    kubectl get hpa -n ${NAMESPACE}
}

# Get access information
show_access_info() {
    print_status "Access Information:"
    
    echo ""
    echo "Frontend Service:"
    kubectl get svc frontend-service -n ${NAMESPACE} -o wide
    
    echo ""
    echo "Backend Service:"
    kubectl get svc backend-service -n ${NAMESPACE} -o wide
    
    echo ""
    print_warning "Remember to update your domain in the ingress configuration"
    print_warning "Update k8s/ingress.yaml with your actual domain"
}

# Main deployment function
main() {
    check_prerequisites
    
    read -p "Do you want to build and push Docker images? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_images
        update_image_references
    fi
    
    deploy_to_k8s
    wait_for_deployment
    show_status
    show_access_info
    
    print_status "🎉 Deployment completed successfully!"
    echo ""
    print_warning "Next steps:"
    echo "1. Update your domain in k8s/ingress.yaml"
    echo "2. Configure SSL certificates if needed"
    echo "3. Set up monitoring and logging"
    echo "4. Configure backups for MongoDB"
}

# Run main function
main "$@" 