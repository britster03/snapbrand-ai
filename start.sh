#!/bin/bash

# SnapBrand.ai Production Startup Script
# This script handles the complete startup process for both development and production environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="backend"
FRONTEND_DIR="."
DOCKER_COMPOSE_FILE="docker-compose.yml"
BACKEND_PORT=8000
FRONTEND_PORT=3000
HEALTH_CHECK_TIMEOUT=60

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

# Function to wait for service to be healthy
wait_for_service() {
    local url=$1
    local timeout=${2:-30}
    local counter=0
    
    print_status "Waiting for service at $url to be healthy..."
    
    while [ $counter -lt $timeout ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            print_success "Service is healthy!"
            return 0
        fi
        
        echo -n "."
        sleep 1
        counter=$((counter + 1))
    done
    
    print_error "Service failed to become healthy within $timeout seconds"
    return 1
}

# Function to check environment variables
check_env_vars() {
    print_status "Checking environment variables..."
    
    local required_vars=("AWS_REGION")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_warning "Missing optional environment variables: ${missing_vars[*]}"
        print_warning "These will use default values. For production, consider setting them explicitly."
    fi
    
    # Check for AWS credentials
    if [ -z "$AWS_ACCESS_KEY_ID" ] && [ -z "$AWS_PROFILE" ]; then
        print_warning "No AWS credentials found. Make sure you have:"
        print_warning "1. AWS CLI configured with 'aws configure'"
        print_warning "2. IAM role attached (for EC2/ECS deployment)"
        print_warning "3. Environment variables set (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)"
    fi
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        return 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    cd ..
    print_success "Backend setup complete"
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    if [ ! -f "package.json" ]; then
        print_error "Frontend package.json not found"
        return 1
    fi
    
    # Install dependencies
    if command_exists pnpm; then
        print_status "Installing frontend dependencies with pnpm..."
        pnpm install
    elif command_exists npm; then
        print_status "Installing frontend dependencies with npm..."
        npm install
    else
        print_error "Neither pnpm nor npm found. Please install Node.js and pnpm/npm."
        return 1
    fi
    
    print_success "Frontend setup complete"
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    
    if ! check_port $BACKEND_PORT; then
        print_error "Port $BACKEND_PORT is already in use"
        return 1
    fi
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Start the backend server in background
    nohup uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    cd ..
    
    # Wait for backend to be healthy
    if wait_for_service "http://localhost:$BACKEND_PORT/health" $HEALTH_CHECK_TIMEOUT; then
        print_success "Backend server started successfully (PID: $BACKEND_PID)"
        return 0
    else
        print_error "Backend server failed to start"
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    if ! check_port $FRONTEND_PORT; then
        print_error "Port $FRONTEND_PORT is already in use"
        return 1
    fi
    
    # Start the frontend server in background
    if command_exists pnpm; then
        nohup pnpm dev > frontend.log 2>&1 &
    else
        nohup npm run dev > frontend.log 2>&1 &
    fi
    
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid
    
    # Wait for frontend to be ready
    if wait_for_service "http://localhost:$FRONTEND_PORT" $HEALTH_CHECK_TIMEOUT; then
        print_success "Frontend server started successfully (PID: $FRONTEND_PID)"
        return 0
    else
        print_error "Frontend server failed to start"
        return 1
    fi
}

# Function to start with Docker Compose
start_docker() {
    print_status "Starting services with Docker Compose..."
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        print_error "Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        return 1
    fi
    
    if ! command_exists docker; then
        print_error "Docker is not installed"
        return 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed"
        return 1
    fi
    
    # Build and start services
    docker-compose up --build -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    sleep 10
    
    if wait_for_service "http://localhost:$BACKEND_PORT/health" $HEALTH_CHECK_TIMEOUT; then
        print_success "Backend service is healthy"
    else
        print_error "Backend service failed to start"
        return 1
    fi
    
    if wait_for_service "http://localhost:$FRONTEND_PORT" $HEALTH_CHECK_TIMEOUT; then
        print_success "Frontend service is healthy"
    else
        print_warning "Frontend service may not be ready yet"
    fi
    
    print_success "Services started successfully with Docker Compose"
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    # Stop Docker Compose services
    if [ -f "$DOCKER_COMPOSE_FILE" ] && command_exists docker-compose; then
        docker-compose down
    fi
    
    # Stop backend
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_success "Backend server stopped"
        fi
        rm -f backend.pid
    fi
    
    # Stop frontend
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_success "Frontend server stopped"
        fi
        rm -f frontend.pid
    fi
}

# Function to show status
show_status() {
    print_status "Service Status:"
    
    # Check backend
    if curl -s -f "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1; then
        print_success "Backend: Running (http://localhost:$BACKEND_PORT)"
    else
        print_error "Backend: Not running"
    fi
    
    # Check frontend
    if curl -s -f "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
        print_success "Frontend: Running (http://localhost:$FRONTEND_PORT)"
    else
        print_error "Frontend: Not running"
    fi
    
    # Show logs
    echo -e "\n${BLUE}Recent Backend Logs:${NC}"
    if [ -f "backend.log" ]; then
        tail -n 5 backend.log
    else
        echo "No backend logs found"
    fi
    
    echo -e "\n${BLUE}Recent Frontend Logs:${NC}"
    if [ -f "frontend.log" ]; then
        tail -n 5 frontend.log
    else
        echo "No frontend logs found"
    fi
}

# Function to show help
show_help() {
    echo "SnapBrand.ai Startup Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start          Start both backend and frontend (default)"
    echo "  start-backend  Start only the backend"
    echo "  start-frontend Start only the frontend"
    echo "  docker         Start with Docker Compose"
    echo "  stop           Stop all services"
    echo "  status         Show service status"
    echo "  setup          Setup dependencies only"
    echo "  help           Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  AWS_REGION              AWS region (default: us-east-1)"
    echo "  AWS_ACCESS_KEY_ID       AWS access key"
    echo "  AWS_SECRET_ACCESS_KEY   AWS secret key"
    echo "  BEDROCK_MODEL_ID        Bedrock model ID"
    echo "  S3_BUCKET_NAME          S3 bucket name"
    echo "  API_KEYS                Comma-separated API keys"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 docker"
    echo "  AWS_REGION=us-west-2 $0 start"
}

# Main script logic
main() {
    local command=${1:-start}
    
    case $command in
        start)
            print_status "Starting SnapBrand.ai application..."
            check_env_vars
            setup_backend
            setup_frontend
            start_backend
            start_frontend
            show_status
            ;;
        start-backend)
            print_status "Starting backend only..."
            check_env_vars
            setup_backend
            start_backend
            ;;
        start-frontend)
            print_status "Starting frontend only..."
            setup_frontend
            start_frontend
            ;;
        docker)
            print_status "Starting with Docker Compose..."
            check_env_vars
            start_docker
            ;;
        stop)
            stop_services
            ;;
        status)
            show_status
            ;;
        setup)
            print_status "Setting up dependencies..."
            check_env_vars
            setup_backend
            setup_frontend
            print_success "Setup complete"
            ;;
        help)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Trap to cleanup on exit
trap 'stop_services' EXIT

# Run main function
main "$@" 