#!/bin/bash
set -e

echo "🚀 Setting up development environment..."

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "📁 Project root: $PROJECT_ROOT"
echo "📁 Backend directory: $BACKEND_DIR"

# Check if we're in the right directory
if [ ! -f "$BACKEND_DIR/pyproject.toml" ]; then
    echo "❌ Error: Cannot find backend/pyproject.toml. Please run this script from the project root."
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed or not in PATH"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip is not installed or not in PATH"
    exit 1
fi

# Determine pip command
PIP_CMD="pip3"
if command -v pip &> /dev/null; then
    PIP_CMD="pip"
fi

echo "🔧 Using pip command: $PIP_CMD"

# Install the agent package in editable mode
echo "📦 Installing agent package and dependencies..."
cd "$BACKEND_DIR"

# Try different installation methods
echo "🔄 Attempting pip install with --user flag..."
if $PIP_CMD install -e . --user --break-system-packages 2>/dev/null; then
    echo "✅ Installed with --user and --break-system-packages"
elif $PIP_CMD install -e . --user 2>/dev/null; then
    echo "✅ Installed with --user flag"
elif $PIP_CMD install -e . 2>/dev/null; then
    echo "✅ Installed globally"
else
    echo "❌ Failed to install with pip. Trying alternative approaches..."
    
    # Try installing just the dependencies first
    echo "🔄 Installing dependencies from requirements..."
    if [ -f "requirements.txt" ]; then
        $PIP_CMD install -r requirements.txt --user 2>/dev/null || $PIP_CMD install -r requirements.txt
    fi
    
    # Install dependencies manually
    echo "🔄 Installing core dependencies manually..."
    $PIP_CMD install --user fastapi uvicorn pydantic python-dotenv atomic-agents instructor google-generativeai httpx 2>/dev/null || \
    $PIP_CMD install fastapi uvicorn pydantic python-dotenv atomic-agents instructor google-generativeai httpx
    
    # Try installing the package again
    $PIP_CMD install -e . --user 2>/dev/null || $PIP_CMD install -e .
fi

# Check if installation was successful
echo "✅ Testing dependencies and agent import..."

# Test critical dependencies first
MISSING_DEPS=""
for dep in "fastapi" "uvicorn" "pydantic" "dotenv" "atomic_agents"; do
    if ! python3 -c "import $dep" 2>/dev/null; then
        MISSING_DEPS="$MISSING_DEPS $dep"
    fi
done

if [ ! -z "$MISSING_DEPS" ]; then
    echo "❌ Missing dependencies:$MISSING_DEPS"
    echo "🔄 Installing missing dependencies..."
    for dep in $MISSING_DEPS; do
        case $dep in
            "dotenv") dep_name="python-dotenv" ;;
            *) dep_name="$dep" ;;
        esac
        $PIP_CMD install --user "$dep_name" 2>/dev/null || $PIP_CMD install "$dep_name"
    done
fi

# Test agent module
if python3 -c "import agent; print('✅ Agent module imported successfully')" 2>/dev/null; then
    echo "✅ Package installation successful!"
else
    echo "❌ Package installation failed. Trying alternative method..."
    
    # Alternative: add to PYTHONPATH
    echo "🔧 Adding to PYTHONPATH as fallback..."
    export PYTHONPATH="$BACKEND_DIR/src:$PYTHONPATH"
    
    if python3 -c "import agent; print('✅ Agent module imported successfully')" 2>/dev/null; then
        echo "✅ PYTHONPATH method works!"
        echo ""
        echo "⚠️  Note: You may need to set PYTHONPATH in your shell:"
        echo "   export PYTHONPATH=\"$BACKEND_DIR/src:\$PYTHONPATH\""
    else
        echo "❌ Both methods failed. Please check your Python environment."
        echo ""
        echo "🔍 Debugging info:"
        echo "   Python path: $(which python3)"
        echo "   Python version: $(python3 --version)"
        echo "   Pip version: $($PIP_CMD --version)"
        exit 1
    fi
fi

# Check environment file
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    if [ -f "$BACKEND_DIR/.env" ]; then
        echo "📄 Copying .env file to project root..."
        cp "$BACKEND_DIR/.env" "$PROJECT_ROOT/.env"
    else
        echo "⚠️  Warning: No .env file found. You may need to create one with GEMINI_API_KEY"
    fi
fi

# Check if frontend dependencies are installed
if [ -d "$PROJECT_ROOT/frontend" ]; then
    cd "$PROJECT_ROOT/frontend"
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    fi
fi

cd "$PROJECT_ROOT"

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🚀 You can now run:"
echo "   make dev          - Start both frontend and backend"
echo "   make dev-backend  - Start only backend"
echo "   make dev-frontend - Start only frontend"
echo ""