#!/bin/bash

# imagifyy.ai Development Setup Script

set -e

echo "🚀 Setting up imagifyy.ai development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. Backend containerization will not work."
    fi
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_warning "AWS CLI is not installed. AWS deployment will not work."
    fi
    
    print_success "Requirements check completed"
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d ".venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please edit backend/.env with your AWS credentials and settings"
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    # Install Node.js dependencies
    if [ ! -d "node_modules" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    fi
    
    # Create environment file if it doesn't exist
    if [ ! -f ".env.local" ]; then
        print_status "Creating .env.local file..."
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    fi
    
    print_success "Frontend setup completed"
}

# Setup infrastructure (optional)
setup_infrastructure() {
    print_status "Setting up infrastructure..."
    
    cd infra
    
    # Create virtual environment
    if [ ! -d ".venv" ]; then
        print_status "Creating Python virtual environment for infrastructure..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install dependencies
    print_status "Installing CDK dependencies..."
    pip install -r requirements.txt
    
    cd ..
    print_success "Infrastructure setup completed"
}

# Start development servers
start_dev_servers() {
    print_status "Starting development servers..."
    
    # Start backend in background
    cd backend
    source .venv/bin/activate
    print_status "Starting FastAPI backend on http://localhost:8000"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    print_status "Starting Next.js frontend on http://localhost:3000"
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait for servers to start
    sleep 5
    
    print_success "Development servers started!"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all servers"
    
    # Function to cleanup on exit
    cleanup() {
        print_status "Stopping development servers..."
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        exit 0
    }
    
    # Set trap to cleanup on script exit
    trap cleanup SIGINT SIGTERM
    
    # Wait for background processes
    wait
}

# Main execution
main() {
    case "${1:-setup}" in
        "setup")
            check_requirements
            setup_backend
            setup_frontend
            setup_infrastructure
            print_success "Development environment setup completed!"
            echo ""
            echo "Next steps:"
            echo "1. Edit backend/.env with your AWS credentials"
            echo "2. Run './scripts/dev-setup.sh start' to start development servers"
            echo "3. Visit http://localhost:3000 to see the application"
            ;;
        "start")
            start_dev_servers
            ;;
        "backend")
            cd backend
            source .venv/bin/activate
            uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
            ;;
        "frontend")
            npm run dev
            ;;
        "test")
            print_status "Running tests..."
            cd backend
            source .venv/bin/activate
            python -m pytest tests/ -v
            cd ..
            ;;
        "build")
            print_status "Building for production..."
            npm run build
            ;;
        "docker")
            print_status "Building Docker image..."
            docker build -t snapbrand-backend -f backend/Dockerfile .
            print_success "Docker image built successfully!"
            ;;
        *)
            echo "Usage: $0 {setup|start|backend|frontend|test|build|docker}"
            echo ""
            echo "Commands:"
            echo "  setup    - Setup development environment (default)"
            echo "  start    - Start both frontend and backend servers"
            echo "  backend  - Start only backend server"
            echo "  frontend - Start only frontend server"
            echo "  test     - Run backend tests"
            echo "  build    - Build frontend for production"
            echo "  docker   - Build Docker image"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 