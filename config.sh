# Shell-compatible Configuration File for Development Environment
# This file defines default values that can be overridden by environment variables

# Server Configuration
export SERVER_HOST=${SERVER_HOST:-"0.0.0.0"}
export SERVER_PORT=${SERVER_PORT:-"8000"}

# Frontend Configuration  
export FRONTEND_HOST=${FRONTEND_HOST:-"localhost"}
export FRONTEND_PORT=${FRONTEND_PORT:-"5173"}
export FRONTEND_PORT_RANGE=${FRONTEND_PORT_RANGE:-"5173-5183"}

# Frontend Proxy Target
export VITE_API_TARGET=${VITE_API_TARGET:-"http://localhost:$SERVER_PORT"}

# Development Settings
export DEV_TIMEOUT=${DEV_TIMEOUT:-"60"}