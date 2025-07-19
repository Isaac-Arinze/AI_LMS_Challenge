# Kubernetes Setup Script for Windows

param(
    [ValidateSet("DockerDesktop", "Minikube", "Kind")]
    [string]$ClusterType = "DockerDesktop"
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"

Write-Host "🚀 Setting up Kubernetes cluster on Windows" -ForegroundColor $Green

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

function Test-DockerDesktop {
    Write-Status "Checking Docker Desktop..."
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        Write-Host "Download from: https://www.docker.com/products/docker-desktop"
        return $false
    }
    
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker is not running. Please start Docker Desktop."
        return $false
    }
    
    Write-Status "Docker Desktop is running"
    return $true
}

function Setup-DockerDesktopK8s {
    Write-Status "Setting up Kubernetes with Docker Desktop..."
    
    # Check if Kubernetes is enabled in Docker Desktop
    $k8sEnabled = docker context ls --format "table {{.Name}}\t{{.DockerEndpoint}}" | Select-String "docker-desktop"
    
    if (-not $k8sEnabled) {
        Write-Warning "Kubernetes is not enabled in Docker Desktop"
        Write-Host "Please enable Kubernetes in Docker Desktop:"
        Write-Host "1. Open Docker Desktop"
        Write-Host "2. Go to Settings > Kubernetes"
        Write-Host "3. Check 'Enable Kubernetes'"
        Write-Host "4. Click 'Apply & Restart'"
        Write-Host ""
        Read-Host "Press Enter after enabling Kubernetes in Docker Desktop"
    }
    
    # Set context to docker-desktop
    kubectl config use-context docker-desktop
    
    Write-Status "Kubernetes cluster is ready"
}

function Setup-Minikube {
    Write-Status "Setting up Minikube..."
    
    # Check if minikube is installed
    if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
        Write-Status "Installing Minikube..."
        
        # Download minikube
        $minikubeUrl = "https://github.com/kubernetes/minikube/releases/latest/download/minikube-windows-amd64.exe"
        $minikubePath = "$env:USERPROFILE\.minikube\bin\minikube.exe"
        
        # Create directory
        New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.minikube\bin" | Out-Null
        
        # Download minikube
        Invoke-WebRequest -Uri $minikubeUrl -OutFile $minikubePath
        
        # Add to PATH
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*\.minikube\bin*") {
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$env:USERPROFILE\.minikube\bin", "User")
            $env:PATH = "$env:PATH;$env:USERPROFILE\.minikube\bin"
        }
    }
    
    # Start minikube
    Write-Status "Starting Minikube cluster..."
    minikube start --driver=docker
    
    Write-Status "Minikube cluster is ready"
}

function Setup-Kind {
    Write-Status "Setting up Kind..."
    
    # Check if kind is installed
    if (-not (Get-Command kind -ErrorAction SilentlyContinue)) {
        Write-Status "Installing Kind..."
        
        # Download kind
        $kindUrl = "https://kind.sigs.k8s.io/dl/v0.20.0/kind-windows-amd64"
        $kindPath = "$env:USERPROFILE\.kind\bin\kind.exe"
        
        # Create directory
        New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.kind\bin" | Out-Null
        
        # Download kind
        Invoke-WebRequest -Uri $kindUrl -OutFile $kindPath
        
        # Add to PATH
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*\.kind\bin*") {
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$env:USERPROFILE\.kind\bin", "User")
            $env:PATH = "$env:PATH;$env:USERPROFILE\.kind\bin"
        }
    }
    
    # Create kind cluster
    Write-Status "Creating Kind cluster..."
    kind create cluster --name ai-learning-assistant
    
    Write-Status "Kind cluster is ready"
}

function Test-Kubernetes {
    Write-Status "Testing Kubernetes connection..."
    
    try {
        $nodes = kubectl get nodes
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Kubernetes cluster is working!"
            Write-Host $nodes
            return $true
        } else {
            Write-Error "Failed to connect to Kubernetes cluster"
            return $false
        }
    }
    catch {
        Write-Error "Error testing Kubernetes: $_"
        return $false
    }
}

function Install-NginxIngress {
    Write-Status "Installing NGINX Ingress Controller..."
    
    # Install NGINX Ingress Controller
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
    
    # Wait for ingress controller to be ready
    Write-Status "Waiting for NGINX Ingress Controller to be ready..."
    kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s
    
    Write-Status "NGINX Ingress Controller is ready"
}

function Install-MetricsServer {
    Write-Status "Installing Metrics Server..."
    
    # Install metrics server
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    
    # Patch metrics server to work with self-signed certificates
    kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
    
    Write-Status "Metrics Server is ready"
}

# Main execution
function Main {
    Write-Status "Starting Kubernetes setup..."
    
    switch ($ClusterType) {
        "DockerDesktop" {
            if (Test-DockerDesktop) {
                Setup-DockerDesktopK8s
            } else {
                return
            }
        }
        "Minikube" {
            Setup-Minikube
        }
        "Kind" {
            Setup-Kind
        }
    }
    
    if (Test-Kubernetes) {
        Write-Status "Installing additional components..."
        Install-NginxIngress
        Install-MetricsServer
        
        Write-Status "🎉 Kubernetes setup completed successfully!"
        Write-Host ""
        Write-Warning "Next steps:"
        Write-Host "1. Run the deployment script: .\deploy.ps1"
        Write-Host "2. Or deploy manually: kubectl apply -k k8s/"
    } else {
        Write-Error "Kubernetes setup failed"
    }
}

# Run main function
Main 