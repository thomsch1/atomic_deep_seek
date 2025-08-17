#!/bin/bash

# Frontend Instance Manager
# Usage: ./frontend-manager.sh [start|stop|list|status] [instance_count]

# Load configuration
if [ -f "config.sh" ]; then
    source config.sh
elif [ -f "config.env" ]; then
    # Try to source config.env but ignore Make syntax
    eval $(grep -v '?=' config.env | grep -v '^#' | sed 's/^/export /')
fi

PIDS_FILE=".frontend_instances.pids"
LOGS_DIR="logs/frontend"

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

# Function to check if port is in use
is_port_in_use() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to find available port
find_available_port() {
    local start_port=${FRONTEND_PORT:-5173}
    local max_attempts=50
    
    for ((i=0; i<$max_attempts; i++)); do
        local test_port=$((start_port + i))
        if ! is_port_in_use $test_port; then
            echo $test_port
            return 0
        fi
    done
    
    return 1
}

# Start frontend instances
start_instances() {
    local count=${1:-3}
    echo "🚀 Starting $count frontend instances..."
    
    # Clean up old PIDs file
    > "$PIDS_FILE"
    
    for ((i=1; i<=count; i++)); do
        local port=$(find_available_port)
        
        if [ $? -eq 0 ]; then
            echo "📱 Starting instance $i on port $port..."
            
            # Start frontend in background
            cd frontend
            FRONTEND_HOST="${FRONTEND_HOST:-localhost}" \
            FRONTEND_PORT="$port" \
            VITE_API_TARGET="${VITE_API_TARGET:-http://localhost:8000}" \
            VITE_INSTANCE_NAME="instance-$i" \
            npm run dev > "../$LOGS_DIR/instance-$i.log" 2>&1 &
            
            local pid=$!
            echo "$pid:$port:instance-$i" >> "../$PIDS_FILE"
            echo "✅ Instance $i started on http://localhost:$port/app/ (PID: $pid)"
            cd ..
            
            # Small delay to avoid port conflicts
            sleep 2
        else
            echo "❌ Failed to find available port for instance $i"
        fi
    done
    
    echo ""
    echo "🎯 Summary:"
    list_instances
}

# Stop all instances
stop_instances() {
    if [ ! -f "$PIDS_FILE" ]; then
        echo "📭 No running instances found"
        return
    fi
    
    echo "🛑 Stopping all frontend instances..."
    
    while IFS=':' read -r pid port name; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔸 Stopping $name (PID: $pid, Port: $port)"
            kill "$pid"
        else
            echo "🔸 Process $name (PID: $pid) already stopped"
        fi
    done < "$PIDS_FILE"
    
    rm -f "$PIDS_FILE"
    echo "✅ All instances stopped"
}

# List running instances
list_instances() {
    if [ ! -f "$PIDS_FILE" ]; then
        echo "📭 No running instances found"
        return
    fi
    
    echo "📋 Running frontend instances:"
    echo "----------------------------------------"
    
    while IFS=':' read -r pid port name; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "✅ $name - http://localhost:$port/app/ (PID: $pid)"
        else
            echo "❌ $name - Process not running (PID: $pid)"
        fi
    done < "$PIDS_FILE"
}

# Show status
show_status() {
    echo "🔍 Frontend Instance Status:"
    echo "================================="
    
    if [ ! -f "$PIDS_FILE" ]; then
        echo "📭 No instances registered"
        return
    fi
    
    local running=0
    local stopped=0
    
    while IFS=':' read -r pid port name; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "🟢 $name (Port: $port, PID: $pid) - RUNNING"
            ((running++))
        else
            echo "🔴 $name (Port: $port, PID: $pid) - STOPPED"
            ((stopped++))
        fi
    done < "$PIDS_FILE"
    
    echo ""
    echo "📊 Total: $((running + stopped)) instances ($running running, $stopped stopped)"
}

# Main command handling
case "$1" in
    start)
        start_instances $2
        ;;
    stop)
        stop_instances
        ;;
    list)
        list_instances
        ;;
    status)
        show_status
        ;;
    restart)
        stop_instances
        sleep 2
        start_instances $2
        ;;
    *)
        echo "Frontend Instance Manager"
        echo "========================="
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  start [count]  - Start frontend instances (default: 3)"
        echo "  stop           - Stop all running instances"
        echo "  list           - List running instances"
        echo "  status         - Show detailed status"
        echo "  restart [count] - Restart all instances"
        echo ""
        echo "Examples:"
        echo "  $0 start 5     - Start 5 frontend instances"
        echo "  $0 stop        - Stop all instances"
        echo "  $0 status      - Show current status"
        ;;
esac