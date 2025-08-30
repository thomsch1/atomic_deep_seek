# AI-Powered Web Research Application

A full-stack AI research application that combines intelligent search capabilities with real-time streaming interfaces. The system uses Google Gemini models to perform comprehensive research by dynamically generating search queries, analyzing results, and synthesizing well-sourced answers.

## 🏗️ Architecture Overview

**Backend**: FastAPI + Atomic Agents (Python) - Provides research orchestration and API endpoints  
**Frontend**: React + TypeScript + Vite - Real-time streaming UI with shadcn/ui components  
**Infrastructure**: Docker containerization with PostgreSQL and Redis support  

The project has migrated from LangGraph to Atomic Agents for better performance and simpler orchestration while maintaining backward compatibility.

## ✨ Key Features

- **Intelligent Query Generation**: Automatically generates multiple targeted search queries from user questions
- **Parallel Web Research**: Conducts simultaneous searches across multiple search providers
- **Quality-Based Source Filtering**: Filters sources by credibility, relevance, authority, and recency
- **Iterative Research Refinement**: Performs multiple research loops to fill knowledge gaps
- **Real-time Activity Timeline**: Visual progress tracking of research phases
- **Citation Management**: Comprehensive source tracking and citation formatting
- **Model Selection**: Support for different Gemini model variants
- **Effort Level Controls**: Configurable research depth (low/medium/high effort)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ with pip
- Node.js 20+ with npm
- Google Gemini API key
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd atomic_deep_seek
```

### 2. Environment Setup

Create a `.env` file in the `backend/` directory:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
LANGSMITH_API_KEY=your_langsmith_key  # For AI observability
```

### 3. Automated Setup

```bash
# Setup both backend and frontend dependencies
make setup
```

### 4. Development Servers

```bash
# Start both frontend and backend (recommended)
make dev

# Or start individually:
make dev-backend  # Backend on http://localhost:2024
make dev-frontend # Frontend on http://localhost:5173
```

### 5. Access Application

- **Development**: http://localhost:5173
- **Production**: http://localhost:8123/app (with Docker)

## 📖 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture and system design
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development workflow and environment setup
- **[API.md](API.md)** - REST API documentation and schemas  
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide

## 🛠️ Technology Stack

### Backend
- **Python 3.11+**: Core language
- **FastAPI**: Modern web framework with automatic OpenAPI docs
- **Atomic Agents 1.0.24+**: AI agent orchestration framework
- **Google Generative AI**: LLM integration for research tasks
- **Pydantic 2.0+**: Data validation and serialization
- **Uvicorn**: ASGI server for production deployment

### Frontend  
- **React 19**: Modern UI library with concurrent features
- **TypeScript 5.7**: Type-safe JavaScript development
- **Vite 6.3**: Fast build tool and dev server
- **Tailwind CSS 4.1**: Utility-first CSS framework
- **Radix UI**: Accessible component primitives
- **Lucide React**: Beautiful icon library

### Infrastructure
- **Docker**: Containerization for consistent deployments
- **PostgreSQL 16**: Relational database for data persistence
- **Redis 6**: Caching and session management
- **Multi-stage builds**: Optimized production images

## 🔧 Common Commands

```bash
# Development
make setup                # Initial environment setup
make dev                  # Start both services
make dev-backend          # Backend only (port 2024)
make dev-frontend         # Frontend only (port 5173)
make config               # Show current configuration

# Code Quality
cd backend && ruff check .    # Python linting
cd frontend && npm run lint   # TypeScript/React linting
cd frontend && npm run build  # Type checking + build

# Testing
cd backend && pytest                      # Backend tests
cd backend && python examples/cli_research.py "test query"  # CLI test

# Production
docker build -t gemini-fullstack-langgraph -f Dockerfile .
GEMINI_API_KEY=<key> docker-compose up
```

## 🔄 Research Workflow

1. **Query Generation** - AI generates multiple targeted search queries from user input
2. **Web Research** - Parallel searches across multiple providers (Google, DuckDuckGo, etc.)
3. **Quality Analysis** - Sources evaluated for credibility, relevance, authority, and recency  
4. **Reflection & Gaps** - AI identifies missing information and generates follow-up queries
5. **Iterative Refinement** - Additional research loops (configurable max loops)
6. **Answer Synthesis** - Final answer generation with proper citations

## 🎯 Effort Levels

- **Low**: 1 initial query, 1 research loop - Quick answers
- **Medium**: 3 initial queries, 3 research loops - Balanced depth  
- **High**: 5 initial queries, 10 research loops - Comprehensive research

## 🗂️ Project Structure

```
atomic_deep_seek/
├── backend/                 # FastAPI backend application
│   ├── src/agent/          # Core research agents and logic
│   ├── tests/              # Backend test suite
│   ├── examples/           # CLI examples and utilities
│   └── pyproject.toml      # Python dependencies and config
├── frontend/               # React frontend application  
│   ├── src/                # React components and services
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── architecture/           # Architecture documentation
├── docs/                   # Additional documentation
├── Dockerfile              # Multi-stage production build
├── docker-compose.yml      # Full-stack deployment
├── Makefile               # Development commands
└── config.env             # Development configuration
```

## 🔧 Configuration

Key environment variables:

- `GEMINI_API_KEY` - Google Gemini API key (required)
- `SERVER_PORT` - Backend port (default: 2024)
- `FRONTEND_PORT` - Frontend port (default: 5173)
- `VITE_API_TARGET` - API proxy target for frontend
- `LANGSMITH_API_KEY` - AI observability (optional)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔍 Search Providers

The system supports multiple search providers with automatic fallback:

- **Google Custom Search** - Primary provider with high-quality results
- **SearchAPI** - Alternative commercial search API
- **DuckDuckGo** - Privacy-focused search with instant answers  
- **Gemini Search** - AI-powered search integration
- **Fallback Provider** - Ensures research continuity

## 🎨 UI Features

- **Real-time Activity Timeline** - Visual progress during research
- **Quality Indicators** - Source credibility and quality scores
- **Citation Management** - Proper academic-style citations
- **Responsive Design** - Works on desktop and mobile devices
- **Dark Theme** - Easy on the eyes for extended research sessions
- **Mathematical Rendering** - KaTeX support for equations and formulas

## 🚦 Health Monitoring

- Backend health check: `GET /health`
- Performance profiling built-in
- Request/response timing metrics
- Error tracking and logging
- Thread pool monitoring

---

**Ready to start researching?** Run `make setup && make dev` and visit http://localhost:5173 to begin!