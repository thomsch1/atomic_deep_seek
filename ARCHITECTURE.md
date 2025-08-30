# Technical Architecture

This document provides a comprehensive overview of the AI-powered web research application's technical architecture, design patterns, and implementation details.

## 🏗️ System Architecture Overview

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  External APIs │  
│   React + TS    │◄──►│  FastAPI + AA   │◄──►│  Gemini, Search │
│   Port: 5173    │    │   Port: 2024    │    │   Providers     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │ Infrastructure  │              │
         └─────────────►│ Docker + Redis  │◄─────────────┘
                        │ + PostgreSQL    │
                        └─────────────────┘
```

### Architectural Principles

- **Separation of Concerns**: Clear distinction between presentation, business logic, and data layers
- **Event-Driven Design**: Asynchronous processing with real-time updates
- **Modular Architecture**: Loosely coupled components for maintainability
- **Performance Optimization**: Parallel processing and caching strategies
- **Error Resilience**: Graceful degradation and fallback mechanisms

## 🔧 Backend Architecture

### Core Components

#### 1. ResearchOrchestrator (`backend/src/agent/orchestrator.py`)

The central component that coordinates the entire research workflow:

```python
class ResearchOrchestrator:
    """Orchestrates the complete research workflow using Atomic Agents."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Lazy-initialized agents for performance
        # Persistent thread pool for concurrent operations
        # Request-scoped caching for expensive operations
```

**Key Features**:
- **Lazy Agent Loading**: Agents are created only when first accessed
- **Thread Pool Management**: Optimal thread sizing based on CPU cores
- **Request-Scoped Caching**: Avoids redundant operations within a single research session
- **Resource Cleanup**: Automatic thread pool cleanup on exit

#### 2. Atomic Agents Architecture

##### Query Generation Agent (`backend/src/agent/agents/query_generation_agent.py`)
```python
class QueryGenerationAgent(BaseResearchAgent):
    """Generates targeted search queries from research topics."""
    
    def run(self, query_input: QueryGenerationInput) -> QueryGenerationOutput:
        # Analyzes research topic
        # Generates diverse, specific queries
        # Considers temporal context and current date
```

##### Web Search Agent (`backend/src/agent/agents/web_search_agent.py`)
```python  
class WebSearchAgent(BaseResearchAgent):
    """Performs web searches using multiple providers with fallback."""
    
    def run(self, search_input: WebSearchInput) -> WebSearchOutput:
        # Multi-provider search with automatic fallback
        # Quality scoring and source classification
        # Content extraction and summarization
```

##### Reflection Agent (`backend/src/agent/agents/reflection_agent.py`)
```python
class ReflectionAgent(BaseResearchAgent):
    """Analyzes research results and identifies knowledge gaps."""
    
    def run(self, reflection_input: ReflectionInput) -> ReflectionOutput:
        # Evaluates research completeness
        # Identifies missing information
        # Generates follow-up queries
```

##### Finalization Agent (`backend/src/agent/agents/finalization_agent.py`)
```python
class FinalizationAgent(BaseResearchAgent):
    """Synthesizes final answers with proper citations."""
    
    def run(self, finalization_input: FinalizationInput) -> FinalizationOutput:
        # Synthesizes information from multiple sources
        # Generates comprehensive answers
        # Formats citations properly
```

### Search Provider Architecture

#### Multi-Provider Search System

```python
# Base Provider Interface
class BaseSearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform search and return structured results."""

# Implemented Providers:
- GoogleCustomSearchProvider    # Primary, high-quality results
- SearchAPIProvider            # Commercial alternative  
- DuckDuckGoSearchProvider     # Privacy-focused
- GeminiSearchProvider         # AI-powered search
- FallbackSearchProvider       # Ensures continuity
```

#### Search Manager (`backend/src/agent/search/search_manager.py`)

```python
class SearchManager:
    """Manages multiple search providers with automatic fallback."""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        
    async def search_with_fallback(self, query: str) -> List[SearchResult]:
        # Try providers in priority order
        # Automatic fallback on failures
        # Result deduplication and ranking
```

### State Management

#### Pydantic Models (`backend/src/agent/state.py`)

```python
class ResearchState(BaseModel):
    """Complete state for the research workflow."""
    messages: List[Message]
    search_queries: List[str] 
    web_research_results: List[str]
    sources_gathered: List[Source]
    research_loop_count: int
    # ... configuration and metadata

class Source(BaseModel):
    """Source information with quality metrics."""
    title: str
    url: str
    source_credibility: Optional[str]  # high, medium, low
    domain_type: Optional[str]         # academic, news, official, etc.
    quality_score: Optional[float]     # 0.0-1.0
    quality_breakdown: Optional[QualityBreakdown]
```

### Quality Assessment System

#### Source Classification (`backend/src/agent/source_classifier.py`)

```python
class SourceClassifier:
    """Classifies sources by type, credibility, and quality."""
    
    ACADEMIC_DOMAINS = {'.edu', '.ac.', 'arxiv.org', 'pubmed.ncbi.nlm.nih.gov'}
    NEWS_DOMAINS = {'reuters.com', 'ap.org', 'bbc.com', 'npr.org'}
    OFFICIAL_DOMAINS = {'.gov', '.mil', 'europa.eu', 'who.int'}
    
    def classify_domain(self, url: str) -> Tuple[str, str]:
        # Domain type classification
        # Credibility assessment
        # Quality scoring
```

#### Quality Validation (`backend/src/agent/quality_validator.py`)

```python
class QualityValidator:
    """Validates and scores source quality based on multiple metrics."""
    
    def calculate_quality_score(self, source: Source, content: str) -> float:
        # Credibility: Domain authority and reputation
        # Relevance: Content alignment with query
        # Completeness: Information depth and detail
        # Recency: Publication date and freshness
        # Authority: Author expertise and citations
```

### Configuration Management

#### Configuration System (`backend/src/agent/configuration.py`)

```python
class Configuration:
    """Centralized configuration management for all agents."""
    
    def __init__(self):
        self.gemini_model = "gemini-1.5-flash"  # Default model
        self.search_timeout = 30                # Search timeout
        self.max_sources = 20                   # Maximum sources per query
        self.quality_threshold = 0.5            # Minimum quality score
        
    @classmethod
    def from_config_dict(cls, config: Optional[Dict[str, Any]]) -> 'Configuration':
        # Load from dictionary with defaults
        # Environment variable overrides
        # Validation and type checking
```

## 🎨 Frontend Architecture

### Component Hierarchy

```
App.tsx (Root)
├── WelcomeScreen.tsx (Landing)
├── ChatMessagesView.tsx (Main Interface)
│   ├── ActivityTimeline.tsx (Progress Tracking)
│   ├── InputForm.tsx (Query Input)
│   ├── MessageDisplay.tsx (Message Rendering)
│   └── QualityIndicator.tsx (Source Quality)
└── components/ui/ (shadcn/ui components)
    ├── Button.tsx
    ├── Input.tsx
    ├── Card.tsx
    └── ScrollArea.tsx
```

### Key Frontend Components

#### 1. App Component (`frontend/src/App.tsx`)

```typescript
export default function App() {
  // State management for messages and research progress
  const [messages, setMessages] = useState<Message[]>([]);
  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<ProcessedEvent[]>([]);
  const [messageQualityData, setMessageQualityData] = useState<Record<string, QualityData>>({});
  
  // Effort level to research parameter mapping
  const mapEffortToParams = (effort: string) => {
    switch (effort) {
      case "low": return { initial_search_query_count: 1, max_research_loops: 1 };
      case "medium": return { initial_search_query_count: 3, max_research_loops: 3 };
      case "high": return { initial_search_query_count: 5, max_research_loops: 10 };
    }
  };
}
```

#### 2. API Service (`frontend/src/services/api.ts`)

```typescript
export class AtomicAgentAPI {
  private baseUrl: string;
  
  constructor() {
    // Dynamic base URL detection for development and production
    if (import.meta.env.VITE_API_URL) {
      this.baseUrl = import.meta.env.VITE_API_URL;
    } else if (import.meta.env.DEV) {
      this.baseUrl = '/api';  // Development proxy
    } else if (window.location.pathname.startsWith('/app')) {
      this.baseUrl = '';      // Production relative URLs
    } else {
      this.baseUrl = `${window.location.protocol}//${window.location.host}`;
    }
  }
  
  async conductResearch(request: ResearchRequest): Promise<ResearchResponse> {
    // Performance timing integration
    // Error handling and retry logic
    // Request/response logging
  }
}
```

#### 3. Performance Profiler (`frontend/src/services/performance-profiler.ts`)

```typescript
class PerformanceProfiler {
  private sessions: Map<string, PerformanceSession> = new Map();
  
  startTiming(question: string): string {
    // Generate unique session ID
    // Track request lifecycle timing
    // Memory usage monitoring
  }
  
  markRequestPreparation(sessionId: string): void { /* ... */ }
  markNetworkRequest(sessionId: string): void { /* ... */ }
  markResponseProcessing(sessionId: string, result: any): void { /* ... */ }
  markUIRendering(sessionId: string): void { /* ... */ }
}
```

### UI Component System

#### shadcn/ui Integration

The application uses shadcn/ui for consistent, accessible components:

```typescript
// components/ui/button.tsx
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
}

// Tailwind CSS classes with variant support
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium",
  {
    variants: { /* ... */ }
  }
);
```

#### Responsive Design System

```css
/* Tailwind CSS utility classes for responsive design */
.responsive-container {
  @apply w-full max-w-4xl mx-auto px-4 sm:px-6 lg:px-8;
}

/* Dark theme with neutral color palette */
:root {
  --background: 220 13% 9%;    /* neutral-800 */
  --foreground: 220 9% 89%;    /* neutral-100 */
  --primary: 220 91% 56%;      /* blue-500 */
}
```

## 🔄 Data Flow Architecture

### Research Workflow Data Flow

```
1. User Input → Frontend State
   ├── Question validation
   ├── Effort level mapping
   └── API request preparation

2. API Request → Backend Orchestrator  
   ├── ResearchOrchestrator.run_research_async()
   ├── State initialization
   └── Agent orchestration

3. Query Generation → Search Execution
   ├── QueryGenerationAgent.run()
   ├── Multiple search queries generated
   └── WebSearchAgent.run() (parallel execution)

4. Source Processing → Quality Assessment
   ├── Content extraction and summarization
   ├── Source classification and quality scoring
   └── Filtering based on quality thresholds

5. Reflection → Iterative Refinement  
   ├── ReflectionAgent.run()
   ├── Knowledge gap identification
   └── Additional research loops (if needed)

6. Finalization → Response Generation
   ├── FinalizationAgent.run()
   ├── Answer synthesis with citations
   └── Final response formatting

7. Response → Frontend Display
   ├── Activity timeline updates
   ├── Message state updates
   └── UI re-rendering
```

### Concurrency and Threading

#### Backend Concurrency

```python
class ResearchOrchestrator:
    def _init_thread_pool(self):
        # Optimal thread count: CPU cores + I/O factor
        max_workers = min(max(os.cpu_count() * 2, 4), 10)
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
    
    async def _parallel_web_research(self, queries: List[str]) -> List[WebSearchOutput]:
        # Submit all search tasks to thread pool
        futures = []
        for query in queries:
            future = self._thread_pool.submit(
                self.search_agent.run,
                WebSearchInput(search_query=query, ...)
            )
            futures.append(future)
        
        # Collect results as they complete
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
        
        return results
```

#### Frontend Async Handling

```typescript
const handleSubmit = useCallback(async (question: string, params: ResearchParams) => {
  setIsLoading(true);
  setProcessedEventsTimeline([]);
  
  try {
    // Non-blocking API call
    const response = await api.conductResearch({
      question,
      ...params
    });
    
    // Update state with response
    setMessages(prev => [...prev, aiMessage]);
    setProcessedEventsTimeline(convertResponseToEvents(response));
    
  } catch (error) {
    setError(error.message);
  } finally {
    setIsLoading(false);
  }
}, [api, messages]);
```

## 🔧 Configuration Architecture

### Environment-Based Configuration

#### Backend Configuration

```python
# backend/.env
GEMINI_API_KEY=your_api_key              # Required
LANGSMITH_API_KEY=your_langsmith_key     # Optional
SERVER_HOST=localhost                    # Server binding
SERVER_PORT=2024                         # Server port

# Search Provider Configuration  
GOOGLE_CSE_ID=your_custom_search_id      # Google Custom Search
GOOGLE_API_KEY=your_google_api_key       # Google API
SEARCHAPI_KEY=your_searchapi_key         # SearchAPI.io
```

#### Frontend Configuration

```typescript
// frontend/.env
VITE_API_URL=http://localhost:2024       # API endpoint override
VITE_API_TARGET=http://localhost:2024    # Development proxy target
```

#### Development Configuration (`config.env`)

```bash
# Main Configuration File for Development Environment
SERVER_HOST := 0.0.0.0
SERVER_PORT := 2024
FRONTEND_HOST := localhost  
FRONTEND_PORT := 5173
VITE_API_TARGET := http://localhost:$(SERVER_PORT)
DEV_TIMEOUT := 120
```

### Build-Time Configuration

#### Vite Configuration (`frontend/vite.config.ts`)

```typescript
export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "/app/",  // Production base path
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") }
  },
  server: {
    host: process.env.FRONTEND_HOST || "localhost",
    port: parseInt(process.env.FRONTEND_PORT || "5173"),
    strictPort: false,
    proxy: {
      "/api": {
        target: process.env.VITE_API_TARGET || "http://localhost:2024",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      }
    }
  }
});
```

## 🐳 Deployment Architecture

### Docker Multi-Stage Build

#### Stage 1: Frontend Build

```dockerfile
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json ./
COPY frontend/package-lock.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build
```

#### Stage 2: Python Backend

```dockerfile  
FROM docker.io/langchain/langgraph-api:3.11

# Install UV for fast Python package management
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist /deps/frontend/dist

# Install Python dependencies with UV
ADD backend/ /deps/backend
RUN cd /deps/backend && \
    uv pip install --system -c /api/constraints.txt -e .
```

### Docker Compose Architecture

```yaml
services:
  langgraph-redis:
    image: docker.io/redis:6
    healthcheck:
      test: redis-cli ping
      
  langgraph-postgres:  
    image: docker.io/postgres:16
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      
  langgraph-api:
    image: gemini-fullstack-langgraph
    ports: ["8123:8000"]
    depends_on:
      - langgraph-redis
      - langgraph-postgres
    environment:
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      REDIS_URI: redis://langgraph-redis:6379
      POSTGRES_URI: postgres://postgres:postgres@langgraph-postgres:5432/postgres
```

## 📊 Performance Architecture

### Backend Performance Optimizations

1. **Lazy Agent Initialization**: Agents created only when needed
2. **Persistent Thread Pools**: Avoid thread creation overhead
3. **Request-Scoped Caching**: Cache expensive operations within requests
4. **Parallel Search Execution**: Concurrent web searches
5. **Connection Pooling**: Efficient HTTP client management

### Frontend Performance Optimizations

1. **Component Lazy Loading**: Dynamic imports for large components
2. **State Management**: Efficient React state updates
3. **Virtual Scrolling**: Handle large message lists efficiently
4. **Request Deduplication**: Prevent duplicate API calls
5. **Performance Profiling**: Built-in timing and metrics

### Monitoring and Observability

```python
# Performance metrics collection
class PerformanceProfiler:
    def track_research_session(self, question: str, start_time: datetime):
        # Track timing for each research phase
        # Memory usage monitoring
        # Search provider performance metrics
        # Quality score distributions
```

## 🔒 Security Architecture

### API Security

1. **CORS Configuration**: Controlled cross-origin access
2. **Request Validation**: Pydantic model validation
3. **Error Handling**: Secure error responses without sensitive data
4. **Rate Limiting**: (Configurable via middleware)

### Environment Security

1. **Secret Management**: Environment variables for API keys
2. **Container Security**: Non-root user in Docker containers  
3. **Network Security**: Internal service communication
4. **Input Sanitization**: User input validation and filtering

---

This architecture supports scalable, maintainable, and high-performance AI research applications with clear separation of concerns and modern development practices.