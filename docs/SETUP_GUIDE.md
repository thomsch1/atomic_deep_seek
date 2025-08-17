# Deep Search AI System - Setup Guide

## 🎯 Overview

The Deep Search AI System is a fullstack research agent powered by LangGraph and Google's Gemini models. This guide provides complete setup instructions for development, testing, and production deployment.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 10GB free disk space
- **Network**: Internet connectivity for API calls

### Required Software
- **Python**: 3.11+ 
- **Node.js**: 18.0+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: Latest version

### Required API Keys
- **Gemini API Key**: Required for AI functionality
- **LangSmith API Key**: Optional for monitoring

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd real_deep_ai_dev
```

### 2. Environment Setup
```bash
# Create backend environment file
cd backend
cp .env.example .env
```

Edit `backend/.env` and add your API keys:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here  # Optional
```

### 3. Install Dependencies
```bash
# Backend dependencies
cd backend
pip install .

# Frontend dependencies  
cd ../frontend
npm install
```

### 4. Start Development Environment
From the project root:
```bash
make dev
```

This starts both backend and frontend services. Access the application at:
- **Frontend**: http://localhost:5173
- **LangGraph UI**: http://localhost:2024  
- **API**: http://localhost:2024

## 📁 Project Structure

```
real_deep_ai_dev/
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── lib/          # Utilities  
│   │   └── App.tsx       # Main application
│   ├── package.json
│   └── vite.config.ts
├── backend/            # LangGraph backend
│   ├── src/
│   │   └── agent/        # AI agent logic
│   │       ├── graph.py     # Main agent graph
│   │       ├── prompts.py   # AI prompts
│   │       ├── state.py     # Agent state management
│   │       └── tools_and_schemas.py  # Tools & schemas
│   ├── examples/
│   │   └── cli_research.py  # CLI interface
│   ├── pyproject.toml
│   └── langgraph.json
├── architecture/       # System architecture docs
├── docker-compose.yml  # Production deployment
├── Dockerfile         # Container build
└── Makefile          # Build automation
```

## 🔧 Detailed Setup Instructions

### Step 1: Get API Keys

#### Gemini API Key (Required)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

#### LangSmith API Key (Optional)
1. Visit [LangSmith](https://smith.langchain.com/settings)
2. Sign in or create an account
3. Navigate to Settings > API Keys
4. Generate a new API key

### Step 2: Environment Configuration

Create `backend/.env`:
```bash
# Required
GEMINI_API_KEY=your_actual_api_key_here

# Optional - for monitoring and observability
LANGSMITH_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=deep-search-ai

# Development settings
PYTHONPATH=./src
LOG_LEVEL=INFO
```

### Step 3: Development Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .

# Verify installation
python -c "import agent; print('Backend setup complete')"
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm run build
```

### Step 4: Database Setup (Development)

For development, the system uses SQLite. No additional setup required.

For production with PostgreSQL:
```bash
# Database will be created automatically by Docker Compose
# No manual setup needed
```

## 🏃 Running the Application

### Development Mode

#### Option 1: Use Make (Recommended)
```bash
# Start both frontend and backend
make dev

# Or start individually
make backend-dev  # Start backend only
make frontend-dev # Start frontend only
```

#### Option 2: Manual Start
```bash
# Terminal 1: Start backend
cd backend
langgraph dev

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Production Mode

#### Using Docker Compose
```bash
# Build and start production services
GEMINI_API_KEY=your_key LANGSMITH_API_KEY=your_key docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Manual Production Build
```bash
# Build frontend
cd frontend
npm run build

# Build backend
cd backend
pip install .

# Start production server
python -m uvicorn agent.app:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing the Installation

### Quick Test
```bash
# Test backend API
curl http://localhost:2024/health

# Test frontend
curl http://localhost:5173
```

### CLI Test
```bash
cd backend
python examples/cli_research.py "What are the latest developments in renewable energy?"
```

### Web Interface Test
1. Open http://localhost:5173
2. Enter a research question
3. Verify the AI agent responds with researched information

## 🐳 Docker Deployment

### Build Custom Image
```bash
# Build the application image
docker build -t deep-search-ai .

# Run with Docker Compose
docker-compose up -d
```

### Environment Variables for Docker
Create `.env` file in project root:
```bash
GEMINI_API_KEY=your_gemini_key
LANGSMITH_API_KEY=your_langsmith_key
POSTGRES_PASSWORD=secure_password
REDIS_PASSWORD=secure_redis_password
```

## 🔍 Verification Steps

### 1. Service Health Checks
```bash
# Check all services are running
make health-check

# Or manually check each service
curl http://localhost:2024/health
curl http://localhost:5173
```

### 2. Database Connectivity
```bash
# In development (SQLite)
ls backend/database.sqlite

# In production (PostgreSQL)
docker-compose exec postgres psql -U postgres -c "\l"
```

### 3. AI Agent Functionality
```bash
# Test via CLI
cd backend
python examples/cli_research.py "Test query"

# Test via API
curl -X POST http://localhost:2024/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Test research question"}'
```

## 🚨 Common Setup Issues

### Port Conflicts
```bash
# Check port usage
lsof -i :2024
lsof -i :5173

# Kill processes using ports
kill -9 $(lsof -t -i:2024)
```

### Permission Issues
```bash
# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
chmod -R 755 .
```

### API Key Issues
```bash
# Verify API key format
echo $GEMINI_API_KEY | wc -c  # Should be ~40 characters

# Test API connectivity
python -c "import os; from agent.configuration import Configuration; print('API key valid' if Configuration().gemini_api_key else 'API key missing')"
```

## 🔄 Development Workflow

### Making Changes

#### Backend Changes
```bash
cd backend
# Make your changes to src/agent/
# No restart needed - hot reloading enabled
```

#### Frontend Changes
```bash
cd frontend
# Make your changes to src/
# Hot reloading automatically applies changes
```

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests  
cd frontend
npm test
```

### Linting and Formatting
```bash
# Backend
cd backend
black src/
ruff check src/

# Frontend
cd frontend
npm run lint
npm run format
```

## 📝 Next Steps

After successful setup:

1. **Read the API Documentation**: `docs/API_REFERENCE.md`
2. **Review Troubleshooting Guide**: `docs/TROUBLESHOOTING.md`
3. **Check Security Hardening**: `docs/SECURITY_CHECKLIST.md`
4. **Explore Developer Docs**: `docs/DEVELOPER.md`

## 🆘 Getting Help

- **Issues**: Check `docs/TROUBLESHOOTING.md`
- **API Reference**: See `docs/API_REFERENCE.md`
- **Architecture**: Review `architecture/system-overview.md`
- **Community**: Create an issue in the repository

## 📄 License

This project is licensed under the Apache License 2.0. See [LICENSE](../LICENSE) file for details.