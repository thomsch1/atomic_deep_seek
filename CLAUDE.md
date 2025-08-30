# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack AI-powered web research application that combines intelligent search capabilities with real-time streaming interfaces. The system uses Google Gemini models to perform comprehensive research by dynamically generating search queries, analyzing results, and synthesizing well-sourced answers.

The project has migrated from LangGraph to Atomic Agents for better performance and simpler orchestration, while maintaining backward compatibility.

## Architecture

**Backend**: FastAPI + Atomic Agents (Python) - Provides research orchestration and API endpoints  
**Frontend**: React + TypeScript + Vite - Real-time streaming UI with shadcn/ui components  
**Infrastructure**: Docker containerization with PostgreSQL and Redis support  

The backend serves both API endpoints and static frontend files for production deployment.

## Common Development Commands

### Setup and Dependencies
```bash
# Setup development environment (run this first)
make setup

# Install backend dependencies
cd backend && pip install .

# Install frontend dependencies  
cd frontend && npm install
```

### Development Servers
```bash
# Start both frontend and backend (recommended)
make dev

# Start backend only (FastAPI + Atomic Agents)
make dev-backend
# Serves on: http://localhost:2024 (configurable via SERVER_PORT)

# Start frontend only (Vite dev server)
make dev-frontend  
# Serves on: http://localhost:5173 (configurable via FRONTEND_PORT)
```

### Testing and Quality
```bash
# Backend linting (ruff configured in pyproject.toml)
cd backend && ruff check .

# Frontend linting (ESLint configured)
cd frontend && npm run lint

# Frontend type checking
cd frontend && npm run build  # includes tsc -b

# Run backend tests (when available)
cd backend && pytest

# CLI research test
cd backend && python examples/cli_research.py "test query"
```

### Production Deployment  
```bash
# Build Docker image
docker build -t gemini-fullstack-langgraph -f Dockerfile .

# Run with Docker Compose (requires GEMINI_API_KEY)
GEMINI_API_KEY=<key> docker-compose up
# Access at: http://localhost:8123/app
```

## Code Architecture

### Backend Structure (`backend/src/agent/`)

**Core Orchestration:**
- `orchestrator.py` - Main `ResearchOrchestrator` class that manages the complete research workflow
- `graph.py` - Backward compatibility layer that wraps the orchestrator to maintain LangGraph-style interface
- `app.py` - FastAPI application with `/research` endpoint and frontend static file serving

**Agent Components:**  
- `agents.py` - Individual atomic agents: QueryGenerationAgent, WebSearchAgent, ReflectionAgent, FinalizationAgent
- `state.py` - Pydantic models for research state management and agent I/O schemas
- `configuration.py` - Agent configuration management with model selection
- `prompts.py` - AI prompt templates for each research phase
- `tools_and_schemas.py` - Google Search integration and data schemas

**Research Workflow:**
1. **Query Generation** - Generates multiple search queries from user input using Gemini
2. **Web Research** - Parallel web searches using Google Search API  
3. **Reflection & Analysis** - Analyzes results for knowledge gaps and quality
4. **Iterative Refinement** - Generates follow-up queries if needed (max loops configurable)
5. **Answer Synthesis** - Combines information into coherent response with citations

### Frontend Structure (`frontend/src/`)

**Main Components:**
- `App.tsx` - Main application with routing and API integration
- `components/ChatMessagesView.tsx` - Real-time chat interface with message streaming
- `components/ActivityTimeline.tsx` - Visual progress tracking of research phases
- `components/InputForm.tsx` - Query input with effort level and model selection
- `components/WelcomeScreen.tsx` - Landing page with example queries

**Supporting Infrastructure:**
- `services/api.ts` - API client for backend communication
- `services/performance-profiler.ts` - Client-side performance monitoring
- `components/ui/` - Reusable shadcn/ui components (Button, Input, Card, etc.)

### Key Configuration Files

**Backend Configuration:**
- `backend/pyproject.toml` - Dependencies, ruff linting rules, project metadata
- `backend/.env` - Environment variables (GEMINI_API_KEY required)
- `config.env` - Development server configuration (SERVER_HOST, SERVER_PORT, VITE_API_TARGET)

**Frontend Configuration:**  
- `frontend/package.json` - React 19, TypeScript 5.7, Vite 6.3, Tailwind 4.1
- `frontend/vite.config.ts` - Vite build configuration with React SWC
- `frontend/tsconfig.json` - TypeScript configuration

**Containerization:**
- `Dockerfile` - Multi-stage build for production deployment
- `docker-compose.yml` - Full stack with PostgreSQL and Redis
- `Makefile` - Development command shortcuts

## Environment Variables

**Required:**
- `GEMINI_API_KEY` - Google Gemini API key for AI functionality

**Optional:**  
- `LANGSMITH_API_KEY` - For AI observability and monitoring
- `SERVER_HOST` - Backend host (default: localhost)
- `SERVER_PORT` - Backend port (default: 2024)  
- `FRONTEND_PORT` - Frontend port (default: 5173)
- `VITE_API_TARGET` - API proxy target for frontend dev server

## Development Notes

### Technology Stack
- **Backend**: Python 3.11+, FastAPI, Atomic Agents 1.0.24+, Google Generative AI, Pydantic 2.0+
- **Frontend**: React 19, TypeScript 5.7, Vite 6.3, Tailwind 4.1, Radix UI components
- **Infrastructure**: Docker, PostgreSQL 16, Redis 6

### Code Quality Standards
- **Backend**: ruff linting with Google docstring convention, mypy type checking
- **Frontend**: ESLint with React hooks rules, TypeScript strict mode
- **Both**: Modern async/await patterns, comprehensive error handling

### API Integration
- Backend exposes `/research` POST endpoint with ResearchRequest/ResearchResponse schemas
- Frontend uses streaming for real-time progress updates during research
- Health check available at `/health` endpoint
- Static frontend served at `/app` path in production

### Testing Strategy
- Unit tests for individual agents and utilities (tests/unit/)
- Integration tests for complete workflows (tests/integration/)
- CLI testing available via `backend/examples/cli_research.py`
- Frontend testing with React Testing Library (when implemented)

### Performance Considerations
- Parallel web searches using ThreadPoolExecutor for optimal I/O concurrency
- Request-scoped caching for expensive operations like date parsing
- Lazy initialization of agents to reduce startup time  
- Thread-safe orchestrator design for concurrent requests