#!/bin/bash

# Invoice Management System - Docker Startup Script
# Usage: ./start.sh [dev|prod|stop|logs|clean]

set -e

COMPOSE_FILE="docker-compose.yml"
OVERRIDE_FILE="docker-compose.override.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  Invoice Management System - Docker Setup${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

wait_for_services() {
    echo -e "${BLUE}Waiting for services to be healthy...${NC}"

    # Wait for databases
    echo "Waiting for PostgreSQL..."
    docker-compose exec -T postgres sh -c 'while ! pg_isready -U invoice_user -d invoice_app; do sleep 1; done' 2>/dev/null || true

    echo "Waiting for MongoDB..."
    docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" 2>/dev/null || true

    echo "Waiting for Redis..."
    docker-compose exec -T redis redis-cli ping 2>/dev/null || true

    sleep 5
}

start_services() {
    local profile=${1:-dev}

    print_header
    echo -e "${BLUE}Starting services in $profile mode...${NC}"

    if [ "$profile" = "dev" ]; then
        docker-compose -f $COMPOSE_FILE -f $OVERRIDE_FILE up -d
    elif [ "$profile" = "prod" ]; then
        docker-compose -f $COMPOSE_FILE up -d
    else
        docker-compose --profile $profile up -d
    fi

    wait_for_services

    print_success "Services started successfully!"
    echo ""
    echo -e "${GREEN}Access URLs:${NC}"
    echo -e "  Frontend:    http://localhost:5174"
    echo -e "  Backend:     http://localhost:5000"
    echo -e "  Chatbot:     http://localhost:5001"
    echo -e "  PgAdmin:     http://localhost:5050 (admin@invoice.com / admin123)"
    echo -e "  MongoDB:     http://localhost:8081 (admin / admin123)"
    echo ""
    echo -e "${YELLOW}To view logs: ./start.sh logs${NC}"
    echo -e "${YELLOW}To stop: ./start.sh stop${NC}"
}

stop_services() {
    print_header
    echo -e "${BLUE}Stopping all services...${NC}"

    docker-compose -f $COMPOSE_FILE -f $OVERRIDE_FILE down
    print_success "Services stopped successfully!"
}

show_logs() {
    print_header
    echo -e "${BLUE}Showing logs (Ctrl+C to exit)...${NC}"
    echo ""

    docker-compose -f $COMPOSE_FILE -f $OVERRIDE_FILE logs -f
}

clean_up() {
    print_header
    echo -e "${YELLOW}This will remove all containers, volumes, and images!${NC}"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Cleaning up...${NC}"
        docker-compose -f $COMPOSE_FILE -f $OVERRIDE_FILE down -v --rmi all
        docker system prune -f
        print_success "Cleanup completed!"
    else
        echo "Cleanup cancelled."
    fi
}

check_health() {
    print_header
    echo -e "${BLUE}Checking service health...${NC}"
    echo ""

    # Check container status
    echo "Container Status:"
    docker-compose ps
    echo ""

    # Check service health
    echo "Service Health:"

    # Backend health
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        print_success "Backend API: Healthy"
    else
        print_error "Backend API: Unhealthy"
    fi

    # Chatbot health
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        print_success "Chatbot API: Healthy"
    else
        print_error "Chatbot API: Unhealthy"
    fi

    # Frontend (basic check)
    if curl -s http://localhost:5174 > /dev/null 2>&1; then
        print_success "Frontend: Healthy"
    else
        print_error "Frontend: Unhealthy"
    fi

    # Database connectivity
    if docker-compose exec -T postgres pg_isready -U invoice_user -d invoice_app > /dev/null 2>&1; then
        print_success "PostgreSQL: Connected"
    else
        print_error "PostgreSQL: Not connected"
    fi

    if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        print_success "MongoDB: Connected"
    else
        print_error "MongoDB: Not connected"
    fi
}

show_help() {
    print_header
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     Start all services in development mode (default)"
    echo "  prod      Start all services in production mode"
    echo "  rasa      Start with Rasa NLP service"
    echo "  tools     Start with development tools (PgAdmin, Mongo Express)"
    echo "  stop      Stop all services"
    echo "  logs      Show logs from all services"
    echo "  health    Check health of all services"
    echo "  clean     Remove all containers, volumes, and images"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start in development mode"
    echo "  $0 prod           # Start in production mode"
    echo "  $0 tools          # Start with dev tools"
    echo "  $0 logs           # View logs"
    echo "  $0 stop           # Stop all services"
}

# Main script
check_docker

case "${1:-start}" in
    "start"|"dev")
        start_services "dev"
        ;;
    "prod")
        start_services "prod"
        ;;
    "rasa")
        start_services "rasa"
        ;;
    "tools")
        start_services "dev-tools"
        ;;
    "stop")
        stop_services
        ;;
    "logs")
        show_logs
        ;;
    "health")
        check_health
        ;;
    "clean")
        clean_up
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac