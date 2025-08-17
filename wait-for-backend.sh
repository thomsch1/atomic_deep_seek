#!/bin/bash

# Script to wait for backend health check before starting frontend
# Usage: ./wait-for-backend.sh [timeout] [host:port]
# Environment variables: SERVER_HOST, SERVER_PORT

# Load environment variables from .env if available
if [ -f "backend/.env" ]; then
    export $(grep -v '^#' backend/.env | xargs)
fi

TIMEOUT=${1:-60}  # Default timeout: 60 seconds
DEFAULT_HOST=${SERVER_HOST:-"localhost"}
DEFAULT_PORT=${SERVER_PORT:-"2024"}
HOST_PORT=${2:-"${DEFAULT_HOST}:${DEFAULT_PORT}"}  # Use env vars or defaults
HEALTH_URL="http://${HOST_PORT}/health"

echo "🔍 Waiting for backend to be ready at ${HEALTH_URL}..."
echo "⏱️  Timeout: ${TIMEOUT} seconds"

start_time=$(date +%s)
end_time=$((start_time + TIMEOUT))

while [ $(date +%s) -lt $end_time ]; do
    # Try to curl the health endpoint
    if curl -s -f "${HEALTH_URL}" > /dev/null 2>&1; then
        echo "✅ Backend is ready! Health check passed."
        
        # Double check with actual response
        response=$(curl -s "${HEALTH_URL}" 2>/dev/null)
        if echo "$response" | grep -q "healthy"; then
            echo "🟢 Backend health status confirmed: healthy"
            exit 0
        else
            echo "⚠️  Backend responded but status unclear: $response"
        fi
    fi
    
    echo "⏳ Backend not ready yet, waiting... ($(( $(date +%s) - start_time ))s elapsed)"
    sleep 2
done

echo "❌ Backend failed to become ready within ${TIMEOUT} seconds"
echo "💡 Please check:"
echo "   - Is the backend server running?"
echo "   - Are there any startup errors?"
echo "   - Is port 8000 accessible?"
exit 1