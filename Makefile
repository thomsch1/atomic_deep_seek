.PHONY: help dev-frontend dev-frontend-multi stop-frontend frontend-status frontend-list dev-backend dev setup config

# Load configuration
include config.env

help:
	@echo "Available commands:"
	@echo "  make setup              - Setup development environment (run this first)"
	@echo "  make dev-frontend       - Starts a single frontend development server"
	@echo "  make dev-frontend-multi - Starts 3 frontend instances (automatic ports)"
	@echo "  make stop-frontend      - Stop all frontend instances"
	@echo "  make frontend-status    - Show frontend instances status"
	@echo "  make frontend-list      - List running frontend instances"
	@echo "  make dev-backend        - Starts the backend development server"
	@echo "  make dev                - Starts both frontend and backend development servers"
	@echo "  make config             - Show current configuration"
	@echo ""
	@echo "Configuration (override in config.env or environment):"
	@echo "  SERVER_HOST:     $(SERVER_HOST)"
	@echo "  SERVER_PORT:     $(SERVER_PORT)"  
	@echo "  VITE_API_TARGET: $(VITE_API_TARGET)"

config:
	@echo "📋 Current Configuration:"
	@echo "  SERVER_HOST:     $(SERVER_HOST)"
	@echo "  SERVER_PORT:     $(SERVER_PORT)"
	@echo "  VITE_API_TARGET: $(VITE_API_TARGET)"
	@echo "  DEV_TIMEOUT:     $(DEV_TIMEOUT)s"
	@echo ""
	@echo "💡 To change these values:"
	@echo "  1. Edit config.env file"
	@echo "  2. Or set environment variables:"
	@echo "     export SERVER_PORT=3000"
	@echo "     make dev"

dev-frontend:
	@echo "Starting frontend development server..."
	@echo "📡 Frontend will proxy API calls to: $(VITE_API_TARGET)"
	@./start-frontend.sh dev $(FRONTEND_PORT)

dev-frontend-multi:
	@echo "🚀 Starting multiple frontend instances..."
	@./frontend-manager.sh start 3

stop-frontend:
	@./frontend-manager.sh stop

frontend-status:
	@./frontend-manager.sh status

frontend-list:
	@./frontend-manager.sh list

dev-backend:
	@echo "Starting backend development server..."
	@echo "🌐 Backend starting on: $(SERVER_HOST):$(SERVER_PORT)"
	@cd backend && PYTHONPATH=$(PWD)/backend/src python3 run_server.py --reload --host $(SERVER_HOST) --port $(SERVER_PORT)

setup:
	@echo "Setting up development environment..."
	@./setup-dev.sh

# Run frontend and backend with proper startup synchronization
dev:
	@echo "Starting both frontend and backend development servers..."
	@echo "🚀 Starting backend first..."
	@make dev-backend & \
	echo "⏳ Waiting for backend to be ready..." && \
	./wait-for-backend.sh && \
	echo "🎨 Starting frontend..." && \
	make dev-frontend 