#!/bin/bash

# Script to start frontend with automatic port detection
# Usage: ./start-frontend.sh [instance_name] [starting_port]

# Load configuration
if [ -f "config.env" ]; then
    source config.env
fi

INSTANCE_NAME=${1:-"dev"}
STARTING_PORT=${2:-${FRONTEND_PORT:-5173}}
HOST=${FRONTEND_HOST:-"localhost"}

# Function to check if port is in use
is_port_in_use() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Find available port in range
find_available_port() {
    local start_port=$1
    local max_attempts=20
    
    for ((i=0; i<$max_attempts; i++)); do
        local test_port=$((start_port + i))
        if ! is_port_in_use $test_port; then
            echo $test_port
            return 0
        fi
    done
    
    echo "No available port found in range $start_port-$((start_port + max_attempts))" >&2
    return 1
}

echo "🚀 Starting frontend instance: $INSTANCE_NAME"
echo "🔍 Looking for available port starting from $STARTING_PORT..."

AVAILABLE_PORT=$(find_available_port $STARTING_PORT)

if [ $? -eq 0 ]; then
    echo "✅ Using port: $AVAILABLE_PORT"
    echo "🌐 Frontend will be available at: http://$HOST:$AVAILABLE_PORT/app/"
    echo "📡 API proxy target: ${VITE_API_TARGET:-http://localhost:8000}"
    echo ""
    
    # Set environment variables for this instance
    export FRONTEND_HOST="$HOST"
    export FRONTEND_PORT="$AVAILABLE_PORT"
    export VITE_INSTANCE_NAME="$INSTANCE_NAME"
    
    # Start the frontend
    cd frontend && npm run dev
else
    echo "❌ Failed to find available port"
    exit 1
fi