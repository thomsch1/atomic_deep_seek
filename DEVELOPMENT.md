# Development Guide

This guide covers the complete development workflow, environment setup, coding standards, and best practices for the AI-powered web research application.

## 🛠️ Development Environment Setup

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 20+** with npm  
- **Git** for version control
- **Google Gemini API key** (required)
- **Code Editor**: VS Code recommended with extensions:
  - Python
  - TypeScript and JavaScript
  - Tailwind CSS IntelliSense
  - ESLint
  - Prettier

### Initial Setup

#### 1. Clone and Setup

```bash
git clone <repository-url>
cd atomic_deep_seek

# Automated setup (recommended)
make setup
```

#### 2. Environment Configuration

Create `backend/.env`:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
LANGSMITH_API_KEY=your_langsmith_key_for_observability
GOOGLE_CSE_ID=your_custom_search_engine_id
GOOGLE_API_KEY=your_google_api_key  
SEARCHAPI_KEY=your_searchapi_io_key
```

#### 3. Manual Setup (Alternative)

```bash
# Backend setup
cd backend
pip install -e .
pip install -e ".[dev]"  # Development dependencies

# Frontend setup  
cd ../frontend
npm install

# Return to root
cd ..
```

## 🚀 Development Workflow

### Development Servers

#### Option 1: Unified Development (Recommended)

```bash
# Start both services with proper synchronization
make dev

# Access application at http://localhost:5173
# Backend API at http://localhost:2024
```

#### Option 2: Individual Services

```bash
# Terminal 1: Backend
make dev-backend
# Serves on http://localhost:2024

# Terminal 2: Frontend  
make dev-frontend
# Serves on http://localhost:5173 with API proxy
```

### Development Commands

```bash
# Environment and configuration
make setup                    # Initial setup
make config                   # Show current configuration
make help                     # List all available commands

# Development servers
make dev                      # Both frontend and backend
make dev-backend              # Backend only (FastAPI + Uvicorn)
make dev-frontend             # Frontend only (Vite dev server)

# Frontend management (multiple instances)
make dev-frontend-multi       # Start 3 frontend instances
make stop-frontend           # Stop all frontend instances
make frontend-status         # Show running instances
make frontend-list           # List frontend processes
```

## 🏗️ Project Structure Deep Dive

```
atomic_deep_seek/
├── 📁 backend/                     # FastAPI backend
│   ├── 📁 src/agent/              # Core application logic
│   │   ├── 📁 agents/             # Individual atomic agents
│   │   │   ├── query_generation_agent.py
│   │   │   ├── web_search_agent.py
│   │   │   ├── reflection_agent.py
│   │   │   ├── finalization_agent.py
│   │   │   └── compatibility.py    # LangGraph compatibility
│   │   ├── 📁 base/               # Base classes and utilities
│   │   │   ├── base_research_agent.py
│   │   │   └── error_handling.py
│   │   ├── 📁 search/             # Search provider implementations
│   │   │   ├── base_provider.py
│   │   │   ├── google_custom_search.py
│   │   │   ├── duckduckgo_search.py
│   │   │   ├── searchapi_provider.py
│   │   │   ├── gemini_search.py
│   │   │   ├── fallback_provider.py
│   │   │   └── search_manager.py
│   │   ├── 📁 citation/           # Citation and grounding
│   │   │   ├── citation_formatter.py
│   │   │   ├── grounding_processor.py
│   │   │   └── validation.py
│   │   ├── 📁 test/               # Unit tests
│   │   ├── orchestrator.py        # Main research orchestrator
│   │   ├── app.py                # FastAPI application
│   │   ├── state.py              # Pydantic models and state
│   │   ├── configuration.py       # Configuration management
│   │   ├── prompts.py            # AI prompt templates
│   │   └── utils.py              # Helper utilities
│   ├── 📁 tests/                  # Integration tests
│   ├── 📁 examples/               # CLI examples and utilities
│   ├── pyproject.toml            # Python dependencies and config
│   └── run_server.py             # Development server entry point
├── 📁 frontend/                   # React frontend
│   ├── 📁 src/                   # Source code
│   │   ├── 📁 components/        # React components
│   │   │   ├── 📁 ui/            # shadcn/ui components
│   │   │   ├── ActivityTimeline.tsx
│   │   │   ├── ChatMessagesView.tsx
│   │   │   ├── InputForm.tsx
│   │   │   ├── WelcomeScreen.tsx
│   │   │   └── MessageDisplay.tsx
│   │   ├── 📁 services/          # API and utilities
│   │   │   ├── api.ts           # API client
│   │   │   └── performance-profiler.ts
│   │   ├── App.tsx              # Root component
│   │   └── main.tsx             # Entry point
│   ├── 📁 public/               # Static assets
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.ts          # Vite configuration
│   ├── tailwind.config.js      # Tailwind CSS config
│   └── tsconfig.json           # TypeScript configuration
├── 📁 architecture/             # Architecture documentation
├── 📁 docs/                    # Additional documentation
├── Makefile                    # Development commands
├── config.env                 # Development configuration
├── docker-compose.yml         # Docker deployment
├── Dockerfile                 # Multi-stage build
└── requirements.txt           # Top-level dependencies
```

## 💻 Backend Development

### Code Structure and Patterns

#### Agent Development Pattern

```python
# Example: Creating a new agent
from agent.base.base_research_agent import BaseResearchAgent
from pydantic import BaseModel, Field

class CustomAgentInput(BaseModel):
    """Input schema for custom agent."""
    data: str = Field(description="Input data description")

class CustomAgentOutput(BaseModel):  
    """Output schema for custom agent."""
    result: str = Field(description="Output result description")

class CustomAgent(BaseResearchAgent):
    """Custom agent for specific research tasks."""
    
    def __init__(self, config):
        super().__init__(config)
        
    def run(self, agent_input: CustomAgentInput) -> CustomAgentOutput:
        """Execute the agent's main logic."""
        try:
            # Agent implementation
            result = self._process_data(agent_input.data)
            return CustomAgentOutput(result=result)
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}")
            raise
    
    def _process_data(self, data: str) -> str:
        """Private method for data processing."""
        # Implementation details
        pass
```

#### Search Provider Implementation

```python
from agent.search.base_provider import BaseSearchProvider, SearchResult

class CustomSearchProvider(BaseSearchProvider):
    """Custom search provider implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Implement search functionality."""
        try:
            # Search implementation
            raw_results = await self._make_api_call(query, num_results)
            return [self._parse_result(result) for result in raw_results]
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def _parse_result(self, raw_result: dict) -> SearchResult:
        """Parse raw API response to SearchResult."""
        return SearchResult(
            title=raw_result.get('title', ''),
            url=raw_result.get('url', ''),
            snippet=raw_result.get('snippet', ''),
            # ... other fields
        )
```

### Backend Testing

#### Unit Tests

```python
# backend/src/agent/test/test_custom_agent.py
import pytest
from agent.agents.custom_agent import CustomAgent, CustomAgentInput
from agent.configuration import Configuration

class TestCustomAgent:
    
    @pytest.fixture
    def agent(self):
        config = Configuration()
        return CustomAgent(config)
    
    @pytest.fixture  
    def sample_input(self):
        return CustomAgentInput(data="test data")
    
    def test_agent_execution(self, agent, sample_input):
        """Test agent execution with valid input."""
        result = agent.run(sample_input)
        assert result.result is not None
        assert isinstance(result.result, str)
    
    def test_agent_error_handling(self, agent):
        """Test agent error handling."""
        invalid_input = CustomAgentInput(data="")
        with pytest.raises(ValueError):
            agent.run(invalid_input)
```

#### Integration Tests

```python  
# backend/tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from agent.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_research_endpoint(client):
    """Test the main research endpoint."""
    response = client.post(
        "/research",
        json={
            "question": "What is artificial intelligence?",
            "initial_search_query_count": 2,
            "max_research_loops": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "final_answer" in data
    assert "sources" in data
    assert len(data["sources"]) > 0
```

### Running Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_integration.py

# Run with coverage  
pytest --cov=src/agent

# Run with verbose output
pytest -v

# Run only unit tests
pytest src/agent/test/

# Run only integration tests  
pytest tests/
```

## 🎨 Frontend Development

### Component Development Patterns

#### Component Structure

```typescript
// components/CustomComponent.tsx
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';

interface CustomComponentProps {
  data: string;
  onUpdate: (value: string) => void;
  className?: string;
}

export function CustomComponent({ 
  data, 
  onUpdate, 
  className = '' 
}: CustomComponentProps) {
  const [internalState, setInternalState] = useState<string>(data);
  
  useEffect(() => {
    setInternalState(data);
  }, [data]);
  
  const handleUpdate = () => {
    onUpdate(internalState);
  };
  
  return (
    <div className={`custom-component ${className}`}>
      <input 
        value={internalState}
        onChange={(e) => setInternalState(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <Button onClick={handleUpdate}>Update</Button>
    </div>
  );
}
```

#### Service Integration

```typescript
// services/custom-service.ts
import { AtomicAgentAPI } from './api';

export class CustomService {
  private api: AtomicAgentAPI;
  
  constructor() {
    this.api = new AtomicAgentAPI();
  }
  
  async processData(input: string): Promise<string> {
    try {
      // Service implementation
      const result = await this.api.conductResearch({
        question: input,
        initial_search_query_count: 1,
        max_research_loops: 1
      });
      return result.final_answer;
    } catch (error) {
      console.error('Service error:', error);
      throw error;
    }
  }
}
```

### State Management Patterns

#### Hook-Based State Management

```typescript
// hooks/useResearchState.ts
import { useState, useCallback } from 'react';
import { Message, ResearchResponse } from '@/services/api';

export function useResearchState() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const addMessage = useCallback((message: Message) => {
    setMessages(prev => [...prev, message]);
  }, []);
  
  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);
  
  const setLoadingState = useCallback((loading: boolean) => {
    setIsLoading(loading);
    if (loading) {
      setError(null);
    }
  }, []);
  
  return {
    messages,
    isLoading,
    error,
    addMessage,
    clearMessages,
    setLoadingState,
    setError
  };
}
```

### Frontend Testing

#### Component Tests

```typescript
// components/__tests__/CustomComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { CustomComponent } from '../CustomComponent';

describe('CustomComponent', () => {
  const mockOnUpdate = jest.fn();
  
  beforeEach(() => {
    mockOnUpdate.mockClear();
  });
  
  it('renders with initial data', () => {
    render(
      <CustomComponent 
        data="test data" 
        onUpdate={mockOnUpdate} 
      />
    );
    
    expect(screen.getByDisplayValue('test data')).toBeInTheDocument();
  });
  
  it('calls onUpdate when button is clicked', () => {
    render(
      <CustomComponent 
        data="test data" 
        onUpdate={mockOnUpdate} 
      />
    );
    
    fireEvent.click(screen.getByText('Update'));
    expect(mockOnUpdate).toHaveBeenCalledWith('test data');
  });
});
```

### Running Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests with coverage
npm run test:coverage  

# Run tests with UI
npm run test:ui

# Linting and type checking
npm run lint
npm run build  # Includes TypeScript checking
```

## 🔧 Code Quality and Standards

### Python Code Standards

#### Linting with Ruff

Configuration in `backend/pyproject.toml`:

```toml
[tool.ruff]
lint.select = [
    "E",     # pycodestyle errors
    "F",     # pyflakes
    "I",     # isort
    "D",     # pydocstyle
    "D401",  # First line should be in imperative mood
    "T201",  # print statements
    "UP",    # pyupgrade
]

lint.ignore = [
    "UP006", "UP007", "UP035",  # typing compatibility
    "D417",  # Missing argument descriptions
    "E501",  # Line too long
]

[tool.ruff.lint.pydocstyle]
convention = "google"  # Google docstring style
```

#### Running Code Quality Checks

```bash
cd backend

# Linting  
ruff check .
ruff check . --fix  # Auto-fix issues

# Type checking
mypy src/agent

# Format code
ruff format .
```

#### Documentation Standards

```python
def research_function(query: str, max_loops: int = 2) -> ResearchResponse:
    """Conduct comprehensive research on a given query.
    
    This function orchestrates the complete research workflow including
    query generation, web searching, reflection, and answer synthesis.
    
    Args:
        query: The research question or topic to investigate.
        max_loops: Maximum number of research loops to perform.
        
    Returns:
        A ResearchResponse containing the final answer and sources.
        
    Raises:
        ValueError: If query is empty or invalid.
        APIError: If external API calls fail.
        
    Example:
        >>> response = research_function("What is machine learning?")
        >>> print(response.final_answer)
        "Machine learning is..."
    """
```

### TypeScript/React Code Standards

#### ESLint Configuration

Configuration in `frontend/eslint.config.js`:

```javascript
export default [
  {
    extends: [
      'eslint:recommended',
      '@typescript-eslint/recommended',
      'plugin:react-hooks/recommended'
    ],
    rules: {
      'react-hooks/exhaustive-deps': 'warn',
      '@typescript-eslint/no-unused-vars': 'error',
      'prefer-const': 'error'
    }
  }
];
```

#### TypeScript Standards

```typescript
// Use explicit return types for functions
export function processResearchData(
  data: ResearchResponse
): ProcessedResearchData {
  // Implementation
}

// Use proper interface definitions
export interface ComponentProps {
  readonly data: ResearchData;
  readonly onUpdate: (data: ResearchData) => void;
  readonly className?: string;
}

// Use proper error handling
async function fetchData(): Promise<ApiResponse> {
  try {
    const response = await api.getData();
    return response;
  } catch (error) {
    console.error('Failed to fetch data:', error);
    throw new Error('Data fetch failed');
  }
}
```

### Commit Standards

#### Conventional Commits

```bash
# Format: type(scope): description

# Types:
feat: add new research quality filtering
fix: resolve search provider timeout issue
docs: update API documentation
style: format code with prettier
refactor: extract search logic to separate module
test: add integration tests for research flow
chore: update dependencies

# Examples:
feat(backend): add support for multiple Gemini models
fix(frontend): resolve activity timeline rendering bug
docs: add comprehensive development guide
test(agents): add unit tests for query generation
```

## 🔄 Development Workflow

### Feature Development Process

#### 1. Branch Creation

```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

#### 2. Development Cycle

```bash
# Make changes
# Run tests frequently
make test-backend   # Backend tests
make test-frontend  # Frontend tests (when available)

# Check code quality
cd backend && ruff check .
cd frontend && npm run lint
```

#### 3. Pre-commit Checks

```bash
# Backend checks
cd backend
ruff check . --fix
mypy src/agent
pytest

# Frontend checks  
cd frontend
npm run lint
npm run build  # Type checking included
npm test
```

#### 4. Commit and Push

```bash
git add .
git commit -m "feat(scope): descriptive commit message"
git push origin feature/your-feature-name
```

### Debugging and Development Tools

#### Backend Debugging

```python
# Add logging to agents
import logging

class CustomAgent(BaseResearchAgent):
    def run(self, input_data):
        self.logger.info(f"Processing input: {input_data}")
        
        # Debug breakpoint
        import pdb; pdb.set_trace()  # Remove before commit
        
        result = self._process(input_data)
        self.logger.debug(f"Processing result: {result}")
        return result
```

#### FastAPI Development Features

```bash
# Access interactive API docs
# Start backend and visit:
http://localhost:2024/docs       # Swagger UI
http://localhost:2024/redoc      # ReDoc

# Use the interactive interface to test endpoints
```

#### Frontend Debugging

```typescript
// React DevTools integration
import { useEffect } from 'react';

function DebugComponent({ data }) {
  useEffect(() => {
    console.log('Component state:', data);
    
    // Performance timing
    console.time('render-time');
    return () => {
      console.timeEnd('render-time');
    };
  }, [data]);
  
  // Browser debugger
  debugger; // Remove before commit
  
  return <div>{data}</div>;
}
```

### Performance Monitoring

#### Backend Performance

```python
import time
from functools import wraps

def time_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} executed in {end - start:.2f}s")
        return result
    return wrapper

@time_execution  
def research_function(query):
    # Function implementation
    pass
```

#### Frontend Performance

```typescript
// Use the built-in performance profiler
import { performanceProfiler } from '@/services/performance-profiler';

function ComponentWithProfiling() {
  const sessionId = performanceProfiler.startTiming("component-render");
  
  useEffect(() => {
    performanceProfiler.markUIRendering(sessionId);
  });
  
  // Component implementation
}
```

## 🧪 Testing Strategy

### Test Categories

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Measure execution times and resource usage

### Backend Testing

```bash
# Run all backend tests
cd backend && pytest

# Run specific test categories
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest tests/e2e/           # End-to-end tests

# Generate coverage report
pytest --cov=src/agent --cov-report=html
```

### Frontend Testing

```bash
# Run all frontend tests
cd frontend && npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm test -- --watch
```

## 🚀 Production Considerations

### Environment Variables

```bash
# Production environment variables
GEMINI_API_KEY=prod_api_key
LANGSMITH_API_KEY=prod_langsmith_key
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
NODE_ENV=production
```

### Build Process

```bash
# Frontend production build
cd frontend
npm run build

# Backend production setup
cd backend  
pip install -e .  # Install in production mode
```

### Docker Development

```bash
# Build development image
docker build -t research-app-dev .

# Run development container
docker run -p 8123:8000 --env-file .env research-app-dev
```

---

This development guide provides a comprehensive foundation for working with the AI research application. Follow these patterns and practices to maintain code quality and development velocity.