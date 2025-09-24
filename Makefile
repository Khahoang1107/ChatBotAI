# Makefile for Invoice Management System
# Compatible with Windows PowerShell

.PHONY: help start stop logs health clean build test dev prod

# Default target
help:
	@echo "Invoice Management System - Docker Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make start     - Start all services in development mode"
	@echo "  make prod      - Start all services in production mode"
	@echo "  make dev       - Start with development tools"
	@echo "  make stop      - Stop all services"
	@echo "  make logs      - Show logs from all services"
	@echo "  make health    - Check health of all services"
	@echo "  make build     - Build all Docker images"
	@echo "  make clean     - Remove all containers and volumes"
	@echo "  make test      - Run tests in Docker environment"
	@echo "  make rasa      - Start with Rasa NLP service"
	@echo ""

# Start services
start:
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
	@echo "Services started! Access URLs:"
	@echo "  Frontend:    http://localhost:5174"
	@echo "  Backend:     http://localhost:5000"
	@echo "  Chatbot:     http://localhost:5001"
	@echo "  PgAdmin:     http://localhost:5050"
	@echo "  MongoDB:     http://localhost:8081"

prod:
	docker-compose -f docker-compose.yml up -d
	@echo "Production services started!"

dev:
	docker-compose --profile dev-tools -f docker-compose.yml -f docker-compose.override.yml up -d
	@echo "Development services with tools started!"

rasa:
	docker-compose --profile rasa -f docker-compose.yml -f docker-compose.override.yml up -d
	@echo "Services with Rasa started!"

# Stop services
stop:
	docker-compose -f docker-compose.yml -f docker-compose.override.yml down
	@echo "Services stopped!"

# Logs
logs:
	docker-compose -f docker-compose.yml -f docker-compose.override.yml logs -f

# Health check
health:
	@echo "Checking service health..."
	@docker-compose ps
	@echo ""
	@echo "Service Status:"
	@curl -s http://localhost:5000/api/health > /dev/null 2>&1 && echo "✓ Backend: Healthy" || echo "✗ Backend: Unhealthy"
	@curl -s http://localhost:5001/health > /dev/null 2>&1 && echo "✓ Chatbot: Healthy" || echo "✗ Chatbot: Unhealthy"
	@curl -s http://localhost:5174 > /dev/null 2>&1 && echo "✓ Frontend: Healthy" || echo "✗ Frontend: Unhealthy"

# Build images
build:
	docker-compose build --no-cache
	@echo "Images built successfully!"

# Clean up
clean:
	docker-compose -f docker-compose.yml -f docker-compose.override.yml down -v --rmi all
	docker system prune -f
	@echo "Cleanup completed!"

# Test
test:
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend_test
	@echo "Tests completed!"

# Database operations
db-init:
	docker-compose exec backend python -m flask db init
	docker-compose exec backend python -m flask db migrate -m "Initial migration"
	docker-compose exec backend python -m flask db upgrade
	@echo "Database initialized!"

db-migrate:
	docker-compose exec backend python -m flask db migrate -m "Auto migration"
	docker-compose exec backend python -m flask db upgrade
	@echo "Database migrated!"

# Development helpers
shell-backend:
	docker-compose exec backend bash

shell-chatbot:
	docker-compose exec chatbot bash

shell-db:
	docker-compose exec postgres psql -U invoice_user -d invoice_app

shell-mongo:
	docker-compose exec mongodb mongo invoice_ai_training -u admin -p password123

# Quick setup for new environment
setup:
	@echo "Setting up Invoice Management System..."
	@make build
	@make start
	@sleep 10
	@make db-init
	@echo "Setup completed! Services are running."

# Status
status:
	@echo "=== Container Status ==="
	@docker-compose ps
	@echo ""
	@echo "=== Docker Images ==="
	@docker images | grep invoice
	@echo ""
	@echo "=== Docker Volumes ==="
	@docker volume ls | grep invoice