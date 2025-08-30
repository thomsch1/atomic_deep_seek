# File Structure Guide

This guide provides a comprehensive, file-by-file breakdown of the entire project structure with detailed creation instructions, templates, and relationships for recreating every component of the AI-powered web research application.

## 📁 Project Root Structure

```
atomic_deep_seek/
├── 📁 backend/                     # FastAPI backend with Atomic Agents
├── 📁 frontend/                    # React frontend with TypeScript
├── 📁 architecture/                # Architecture documentation
├── 📁 docs/                       # Additional documentation  
├── 🐳 Dockerfile                  # Multi-stage production build
├── 🐳 docker-compose.yml          # Full-stack deployment
├── 🔧 Makefile                   # Development commands
├── ⚙️ config.env                 # Development configuration
├── 📋 requirements.txt           # Top-level Python requirements
├── 📖 README.md                  # Main project documentation
├── 🏗️ ARCHITECTURE.md           # Technical architecture guide
├── 💻 DEVELOPMENT.md             # Development workflow guide
├── 📡 API.md                     # API documentation
├── 🚀 DEPLOYMENT.md              # Deployment guide
├── 🛠️ IMPLEMENTATION_GUIDE.md    # Implementation patterns
├── 📦 DEPENDENCY_GUIDE.md        # Dependency specifications
├── 📋 FILE_STRUCTURE_GUIDE.md    # This file
├── ⚙️ CONFIGURATION_GUIDE.md      # Configuration templates
├── 🧪 TESTING_IMPLEMENTATION_GUIDE.md # Testing patterns
├── ✅ CLAUDE_CODE_RECREATION_CHECKLIST.md # Recreation checklist
└── 📄 CLAUDE.md                  # Claude Code instructions
```

## 🐍 Backend File Structure (`backend/`)

### Root Backend Files

#### `backend/pyproject.toml`
**Purpose**: Python project configuration and dependencies  
**Template**:
```toml
[project]
name = "agent"
version = "0.0.1"
description = "Backend for the Atomic Agent research system"
authors = [{ name = "Your Name", email = "your.email@example.com" }]
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11,<4.0"
dependencies = [
    "atomic-agents>=1.0.24",
    "instructor>=1.3.7",
    "google-genai>=0.1.0",
    "python-dotenv>=1.0.1",
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.0.0",
    "httpx>=0.25.0",
    "jsonref>=1.1.0",
]

[project.optional-dependencies]
dev = ["mypy>=1.11.1", "ruff>=0.6.1"]

[build-system]
requires = ["setuptools>=73.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
lint.select = ["E", "F", "I", "D", "D401", "T201", "UP"]
lint.ignore = ["UP006", "UP007", "UP035", "D417", "E501"]
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D", "UP"]
[tool.ruff.lint.pydocstyle]
convention = "google"

[dependency-groups]
dev = ["pytest>=8.3.5", "pytest-asyncio>=0.23.0", "pytest-mock>=3.12.0"]
```

#### `backend/run_server.py`
**Purpose**: Development server entry point  
**Template**:
```python
"""Development server for the research backend."""

import uvicorn
import argparse
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run the research backend server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=2024, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()
    
    # Set Python path for imports
    src_path = Path(__file__).parent / "src"
    if str(src_path) not in os.environ.get("PYTHONPATH", ""):
        os.environ["PYTHONPATH"] = f"{src_path}:{os.environ.get('PYTHONPATH', '')}"
    
    uvicorn.run(
        "agent.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        access_log=True,
    )

if __name__ == "__main__":
    main()
```

#### `backend/.env.example`
**Purpose**: Environment variables template  
**Template**:
```bash
# Required Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Optional AI Observability
LANGSMITH_API_KEY=your_langsmith_key_for_tracing

# Search Provider Keys (Optional but Recommended)
GOOGLE_CSE_ID=your_custom_search_engine_id
GOOGLE_API_KEY=your_google_api_key
SEARCHAPI_KEY=your_searchapi_io_key

# Server Configuration
SERVER_HOST=localhost
SERVER_PORT=2024
PYTHONPATH=./backend/src

# Development Settings
NODE_ENV=development
LOG_LEVEL=INFO
```

### Core Application Files (`backend/src/agent/`)

#### `backend/src/agent/__init__.py`
**Purpose**: Package initialization  
**Template**:
```python
"""AI-powered web research backend using Atomic Agents."""

__version__ = "0.0.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"
```

#### `backend/src/agent/app.py`
**Purpose**: FastAPI application and API endpoints  
**Key Features**: Health check, research endpoint, static file serving  
**Template**:
```python
"""FastAPI application for the AI research backend."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import logging
import os

from agent.orchestrator import ResearchOrchestrator
from agent.state import ResearchRequest, ResearchResponse
from agent.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Research Agent API",
    description="AI-powered web research with Atomic Agents and Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize research orchestrator
try:
    orchestrator = ResearchOrchestrator()
    logger.info("Research orchestrator initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize orchestrator: {e}")
    orchestrator = None

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "atomic-research-agent",
        "orchestrator_ready": orchestrator is not None
    }

@app.post("/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest) -> ResearchResponse:
    """Conduct AI-powered research on a given question."""
    if orchestrator is None:
        raise HTTPException(
            status_code=503, 
            detail="Research orchestrator not available"
        )
    
    try:
        logger.info(f"Starting research for question: {request.question[:100]}...")
        result = await orchestrator.run_research_async(request)
        logger.info(f"Research completed with {len(result.sources)} sources")
        return result
    except Exception as e:
        logger.error(f"Research failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for production frontend serving
frontend_dist_path = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
if frontend_dist_path.exists():
    app.mount("/app", StaticFiles(directory=frontend_dist_path, html=True), name="frontend")
    logger.info(f"Frontend static files mounted from: {frontend_dist_path}")
else:
    logger.warning(f"Frontend dist directory not found at: {frontend_dist_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2024)
```

#### `backend/src/agent/state.py`
**Purpose**: Pydantic models for request/response schemas and state management  
**Template**:
```python
"""Pydantic models for research state management and API schemas."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

# API Request/Response Models
class ResearchRequest(BaseModel):
    """Request schema for research endpoint."""
    question: str = Field(description="The research question to investigate", min_length=1)
    initial_search_query_count: int = Field(default=3, ge=1, le=10, description="Number of initial search queries")
    max_research_loops: int = Field(default=2, ge=1, le=10, description="Maximum research loops to perform")
    reasoning_model: Optional[str] = Field(default=None, description="Gemini model for reasoning tasks")
    source_quality_filter: Optional[str] = Field(default=None, regex="^(high|medium|low)$", description="Minimum source quality")

class QualityBreakdown(BaseModel):
    """Detailed quality metrics for sources."""
    credibility: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    relevance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    completeness: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    recency: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    authority: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class Source(BaseModel):
    """Source information with quality metrics."""
    title: str = Field(description="Title of the source")
    url: str = Field(description="URL of the source")
    label: Optional[str] = Field(default=None, description="Citation label")
    source_credibility: Optional[str] = Field(default=None, regex="^(high|medium|low)$")
    domain_type: Optional[str] = Field(default=None, regex="^(academic|news|official|commercial|other)$")
    quality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    quality_breakdown: Optional[QualityBreakdown] = Field(default=None)

class ResearchResponse(BaseModel):
    """Response schema for research endpoint."""
    final_answer: str = Field(description="The synthesized research answer with citations")
    sources: List[Source] = Field(description="Sources used in the research")
    research_loops_executed: int = Field(description="Number of research loops performed")
    total_queries: int = Field(description="Total number of search queries executed")

# Internal State Models
class Message(BaseModel):
    """Message in the research conversation."""
    role: str = Field(description="Message role: user, assistant, or system")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)

class ResearchState(BaseModel):
    """Complete state for the research workflow."""
    original_question: str = Field(description="The original research question")
    messages: List[Message] = Field(default_factory=list)
    search_queries: List[str] = Field(default_factory=list)
    web_research_results: List[str] = Field(default_factory=list)
    sources_gathered: List[Source] = Field(default_factory=list)
    research_loop_count: int = Field(default=0)
    is_complete: bool = Field(default=False)
    
    # Configuration
    initial_query_count: int = Field(default=3)
    max_loops: int = Field(default=2)
    quality_filter: Optional[str] = Field(default=None)
    reasoning_model: Optional[str] = Field(default=None)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Agent Input/Output Models
class QueryGenerationInput(BaseModel):
    """Input schema for query generation agent."""
    research_topic: str = Field(description="The research topic or question")
    query_count: int = Field(default=3, description="Number of queries to generate")
    context: Optional[str] = Field(default=None, description="Additional context")

class QueryGenerationOutput(BaseModel):
    """Output schema for query generation agent."""
    search_queries: List[str] = Field(description="Generated search queries")
    reasoning: Optional[List[str]] = Field(default=None, description="Query reasoning")

class WebSearchInput(BaseModel):
    """Input schema for web search agent."""
    search_query: str = Field(description="The search query to execute")
    max_results: int = Field(default=10, description="Maximum number of results")
    quality_filter: Optional[str] = Field(default=None)

class WebSearchOutput(BaseModel):
    """Output schema for web search agent."""
    search_results: List[Dict[str, Any]] = Field(description="Raw search results")
    processed_sources: List[Source] = Field(description="Processed and scored sources")
    total_results: int = Field(description="Total number of results found")

class ReflectionInput(BaseModel):
    """Input schema for reflection agent."""
    original_question: str = Field(description="Original research question")
    current_sources: List[Source] = Field(description="Sources gathered so far")
    research_progress: str = Field(description="Summary of research progress")

class ReflectionOutput(BaseModel):
    """Output schema for reflection agent."""
    is_complete: bool = Field(description="Whether research is complete")
    missing_aspects: List[str] = Field(description="Missing information aspects")
    additional_queries: List[str] = Field(description="Additional queries needed")
    completeness_score: float = Field(ge=0.0, le=1.0)

class FinalizationInput(BaseModel):
    """Input schema for finalization agent."""
    original_question: str = Field(description="Original research question")
    all_sources: List[Source] = Field(description="All gathered sources")
    research_summary: str = Field(description="Summary of research findings")

class FinalizationOutput(BaseModel):
    """Output schema for finalization agent."""
    final_answer: str = Field(description="Synthesized final answer")
    citations_used: List[str] = Field(description="Citations included in answer")
    confidence_score: float = Field(ge=0.0, le=1.0)
```

#### `backend/src/agent/configuration.py`
**Purpose**: Configuration management  
**Template**: *(See IMPLEMENTATION_GUIDE.md for full template)*

#### `backend/src/agent/orchestrator.py`
**Purpose**: Main research orchestrator coordinating all agents  
**Template**: *(See IMPLEMENTATION_GUIDE.md for orchestrator pattern)*

### Agent Files (`backend/src/agent/agents/`)

#### `backend/src/agent/agents/__init__.py`
**Template**:
```python
"""Research agents for the AI-powered web research system."""

from .query_generation_agent import QueryGenerationAgent
from .web_search_agent import WebSearchAgent
from .reflection_agent import ReflectionAgent
from .finalization_agent import FinalizationAgent

__all__ = [
    "QueryGenerationAgent",
    "WebSearchAgent", 
    "ReflectionAgent",
    "FinalizationAgent"
]
```

#### Individual Agent Files
Each agent follows the pattern from IMPLEMENTATION_GUIDE.md:
- `query_generation_agent.py` - Query generation from research topics
- `web_search_agent.py` - Web search execution with multiple providers
- `reflection_agent.py` - Research gap analysis and reflection  
- `finalization_agent.py` - Answer synthesis and citation formatting
- `compatibility.py` - LangGraph compatibility layer

### Base Classes (`backend/src/agent/base/`)

#### `backend/src/agent/base/__init__.py`
**Template**:
```python
"""Base classes and utilities for research agents."""

from .base_research_agent import BaseResearchAgent
from .error_handling import ResearchError, ErrorHandler, ErrorType

__all__ = ["BaseResearchAgent", "ResearchError", "ErrorHandler", "ErrorType"]
```

#### `backend/src/agent/base/base_research_agent.py`
**Purpose**: Base class for all research agents  
**Template**: *(See IMPLEMENTATION_GUIDE.md for complete base class)*

#### `backend/src/agent/base/error_handling.py`
**Purpose**: Centralized error handling  
**Template**: *(See IMPLEMENTATION_GUIDE.md for error handling patterns)*

### Search Providers (`backend/src/agent/search/`)

#### `backend/src/agent/search/__init__.py`
**Template**:
```python
"""Search providers for web research."""

from .base_provider import BaseSearchProvider, SearchResult
from .google_custom_search import GoogleCustomSearchProvider
from .duckduckgo_search import DuckDuckGoSearchProvider
from .searchapi_provider import SearchAPIProvider
from .gemini_search import GeminiSearchProvider
from .fallback_provider import FallbackSearchProvider
from .search_manager import SearchManager

__all__ = [
    "BaseSearchProvider", "SearchResult",
    "GoogleCustomSearchProvider", "DuckDuckGoSearchProvider", 
    "SearchAPIProvider", "GeminiSearchProvider", "FallbackSearchProvider",
    "SearchManager"
]
```

#### Search Provider Files
- `base_provider.py` - Abstract base class for search providers
- `google_custom_search.py` - Google Custom Search implementation
- `duckduckgo_search.py` - DuckDuckGo search implementation  
- `searchapi_provider.py` - SearchAPI.io provider
- `gemini_search.py` - Gemini-powered search
- `fallback_provider.py` - Fallback search implementation
- `search_manager.py` - Multi-provider search manager with failover

### Citation System (`backend/src/agent/citation/`)

#### `backend/src/agent/citation/__init__.py`
**Template**:
```python
"""Citation and grounding system for research sources."""

from .citation_formatter import CitationFormatter
from .grounding_processor import GroundingProcessor  
from .validation import CitationValidator

__all__ = ["CitationFormatter", "GroundingProcessor", "CitationValidator"]
```

#### Citation Files
- `citation_formatter.py` - Format citations in various styles
- `grounding_processor.py` - Process and validate source grounding
- `validation.py` - Validate citation accuracy and completeness

### Utility Files (`backend/src/agent/`)

#### `backend/src/agent/prompts.py`
**Purpose**: AI prompt templates  
**Template**:
```python
"""Prompt templates for AI agents."""

class PromptTemplates:
    """Central repository for all AI prompt templates."""
    
    QUERY_GENERATION = """You are an expert research query generator.
    Generate {count} diverse, specific search queries for this research topic: {topic}
    
    Focus on:
    - Different angles and perspectives
    - Specific aspects and details
    - Current and recent information
    - Authoritative sources
    
    Context: {context}
    
    Return only the queries as a JSON array of strings."""
    
    WEB_SEARCH_ANALYSIS = """Analyze these search results for the query: {query}
    
    Evaluate each result for:
    - Relevance to the research question
    - Source credibility and authority
    - Information quality and completeness
    - Publication date and recency
    
    Search Results: {results}
    
    Return analysis in JSON format with quality scores."""
    
    # Add more prompt templates as needed...
```

#### `backend/src/agent/utils.py`
**Purpose**: Utility functions  
**Template**:
```python
"""Utility functions for research agents."""

import re
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might interfere
    text = re.sub(r'[^\w\s\-.,;:!?()]', '', text)
    
    return text

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse various date formats to datetime object."""
    if not date_str:
        return None
    
    # Common date formats
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d/%m/%Y",
        "%m/%d/%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    
    return None

def calculate_recency_score(published_date: Optional[datetime]) -> float:
    """Calculate recency score based on publication date."""
    if not published_date:
        return 0.5  # Default for unknown dates
    
    now = datetime.now(timezone.utc)
    days_old = (now - published_date).days
    
    # Scoring curve: newer is better
    if days_old <= 7:
        return 1.0
    elif days_old <= 30:
        return 0.9
    elif days_old <= 90:
        return 0.8
    elif days_old <= 180:
        return 0.6
    elif days_old <= 365:
        return 0.4
    else:
        return 0.2

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    
    # Try to break at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If we can break reasonably close
        return truncated[:last_space] + "..."
    else:
        return truncated + "..."

def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
```

### Testing Files (`backend/src/agent/test/` and `backend/tests/`)

#### Unit Tests Structure (`backend/src/agent/test/`)
- `conftest.py` - Test configuration and fixtures
- `test_base_research_agent.py` - Base agent tests
- `test_configuration.py` - Configuration tests
- `test_query_generation_agent.py` - Query generation tests
- `test_web_search_agent.py` - Web search tests
- `test_reflection_agent.py` - Reflection tests
- `test_finalization_agent.py` - Finalization tests
- `test_error_handling.py` - Error handling tests

#### Integration Tests Structure (`backend/tests/`)
- `conftest.py` - Integration test fixtures
- `test_api_simple.py` - Basic API tests
- `test_comprehensive_api.py` - Full API integration tests
- `test_e2e_integration.py` - End-to-end workflow tests
- `test_performance_profiling.py` - Performance tests

### Examples (`backend/examples/`)

#### `backend/examples/cli_research.py`
**Purpose**: Command-line interface for testing  
**Template**:
```python
"""Command-line interface for testing research functionality."""

import asyncio
import argparse
import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent.orchestrator import ResearchOrchestrator
from agent.state import ResearchRequest

async def main():
    parser = argparse.ArgumentParser(description="CLI Research Tool")
    parser.add_argument("question", help="Research question")
    parser.add_argument("--queries", type=int, default=3, help="Number of initial queries")
    parser.add_argument("--loops", type=int, default=2, help="Maximum research loops")
    parser.add_argument("--model", help="Reasoning model to use")
    parser.add_argument("--quality", choices=["high", "medium", "low"], help="Quality filter")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    try:
        # Initialize orchestrator
        orchestrator = ResearchOrchestrator()
        
        # Create request
        request = ResearchRequest(
            question=args.question,
            initial_search_query_count=args.queries,
            max_research_loops=args.loops,
            reasoning_model=args.model,
            source_quality_filter=args.quality
        )
        
        print(f"🔍 Researching: {args.question}")
        print(f"📊 Config: {args.queries} queries, {args.loops} loops")
        
        # Execute research
        result = await orchestrator.run_research_async(request)
        
        if args.json:
            print(json.dumps(result.dict(), indent=2, default=str))
        else:
            print(f"\n📝 **Answer:**\n{result.final_answer}")
            print(f"\n📚 **Sources ({len(result.sources)}):**")
            for i, source in enumerate(result.sources, 1):
                print(f"{i}. {source.title}")
                print(f"   {source.url}")
                if source.quality_score:
                    print(f"   Quality: {source.quality_score:.2f}")
                print()
            
            print(f"🔄 Research loops: {result.research_loops_executed}")
            print(f"🔎 Total queries: {result.total_queries}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

## ⚛️ Frontend File Structure (`frontend/`)

### Root Frontend Files

#### `frontend/package.json`
**Purpose**: Node.js project configuration  
**Template**: *(See DEPENDENCY_GUIDE.md for complete package.json)*

#### `frontend/vite.config.ts`
**Purpose**: Vite build configuration  
**Template**:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  base: "/app/",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    }
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
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['@radix-ui/react-select', '@radix-ui/react-collapsible'],
        }
      }
    }
  }
})
```

#### `frontend/tsconfig.json`
**Purpose**: TypeScript configuration  
**Template**:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"]
}
```

#### `frontend/tailwind.config.js`
**Purpose**: Tailwind CSS configuration  
**Template**:
```javascript
import animate from 'tailwindcss/plugin'

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      },
    },
  },
  plugins: [animate],
}
```

### Source Files (`frontend/src/`)

#### `frontend/src/main.tsx`
**Purpose**: Application entry point  
**Template**:
```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './global.css'
import App from './App.tsx'

const root = document.getElementById('root')!

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

#### `frontend/src/App.tsx`
**Purpose**: Main application component  
**Template**: *(See IMPLEMENTATION_GUIDE.md for complete App component)*

#### `frontend/src/global.css`
**Purpose**: Global styles and CSS variables  
**Template**:
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 220 13% 9%;
    --foreground: 220 9% 89%;
    --card: 220 13% 9%;
    --card-foreground: 220 9% 89%;
    --popover: 220 13% 9%;
    --popover-foreground: 220 9% 89%;
    --primary: 220 91% 56%;
    --primary-foreground: 220 9% 9%;
    --secondary: 220 6% 15%;
    --secondary-foreground: 220 9% 89%;
    --muted: 220 6% 15%;
    --muted-foreground: 220 6% 64%;
    --accent: 220 6% 15%;
    --accent-foreground: 220 9% 89%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 220 9% 89%;
    --border: 220 6% 18%;
    --input: 220 6% 18%;
    --ring: 220 91% 56%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground font-sans;
  }
}

/* Custom scrollbar styles */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  @apply bg-muted;
}

::-webkit-scrollbar-thumb {
  @apply bg-muted-foreground/50 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-muted-foreground/70;
}
```

### Component Files (`frontend/src/components/`)

#### Main Components
- `App.tsx` - Root application component
- `WelcomeScreen.tsx` - Landing page component
- `ChatMessagesView.tsx` - Main chat interface
- `InputForm.tsx` - Research query input form
- `ActivityTimeline.tsx` - Research progress visualization
- `QualityIndicator.tsx` - Source quality visualization

#### UI Components (`frontend/src/components/ui/`)
All UI components follow shadcn/ui patterns:
- `button.tsx` - Button component with variants
- `input.tsx` - Input field component
- `card.tsx` - Card container component
- `select.tsx` - Select dropdown component
- `tabs.tsx` - Tab navigation component
- `badge.tsx` - Badge/label component
- `scroll-area.tsx` - Custom scroll area
- `collapsible.tsx` - Collapsible content
- `tooltip.tsx` - Tooltip component
- `textarea.tsx` - Textarea component

### Service Files (`frontend/src/services/`)

#### `frontend/src/services/api.ts`
**Purpose**: API client for backend communication  
**Template**: *(See IMPLEMENTATION_GUIDE.md for API service pattern)*

#### `frontend/src/services/performance-profiler.ts`
**Purpose**: Client-side performance monitoring  
**Template**:
```typescript
interface PerformanceSession {
  id: string;
  question: string;
  startTime: number;
  phases: Record<string, number>;
  endTime?: number;
}

class PerformanceProfiler {
  private sessions: Map<string, PerformanceSession> = new Map();
  
  startTiming(question: string): string {
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const session: PerformanceSession = {
      id: sessionId,
      question,
      startTime: performance.now(),
      phases: {}
    };
    
    this.sessions.set(sessionId, session);
    return sessionId;
  }
  
  markPhase(sessionId: string, phaseName: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.phases[phaseName] = performance.now();
    }
  }
  
  endTiming(sessionId: string): PerformanceSession | null {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.endTime = performance.now();
      return session;
    }
    return null;
  }
  
  getSessionMetrics(sessionId: string) {
    const session = this.sessions.get(sessionId);
    if (!session || !session.endTime) return null;
    
    const totalTime = session.endTime - session.startTime;
    const phaseMetrics = Object.entries(session.phases).map(([phase, time]) => ({
      phase,
      duration: time - session.startTime,
      percentage: ((time - session.startTime) / totalTime) * 100
    }));
    
    return {
      sessionId,
      question: session.question,
      totalTime,
      phases: phaseMetrics
    };
  }
}

export const performanceProfiler = new PerformanceProfiler();
```

### Utility Files (`frontend/src/lib/`)

#### `frontend/src/lib/utils.ts`
**Purpose**: Utility functions  
**Template**:
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

export function isValidUrl(string: string): boolean {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
}
```

### Configuration Files

#### `frontend/eslint.config.js`
**Template**: *(See DEPENDENCY_GUIDE.md for ESLint configuration)*

#### `frontend/vitest.config.ts`
**Purpose**: Vitest testing configuration  
**Template**:
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test-setup.ts',
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    }
  },
})
```

#### `frontend/src/test-setup.ts`
**Purpose**: Test environment setup  
**Template**:
```typescript
import '@testing-library/jest-dom'

// Mock performance API
global.performance = global.performance || {
  now: () => Date.now(),
  mark: () => {},
  measure: () => {},
  getEntriesByName: () => [],
  getEntriesByType: () => [],
}

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
})
```

## 🔧 Configuration Files (Project Root)

### `Makefile`
**Purpose**: Development commands  
**Template**: *(See existing Makefile for complete implementation)*

### `config.env`
**Purpose**: Development environment configuration  
**Template**:
```bash
# Main Configuration File for Development Environment

# Server Configuration
SERVER_HOST := 0.0.0.0
SERVER_PORT := 2024

# Frontend Configuration  
FRONTEND_HOST := localhost
FRONTEND_PORT := 5173

# API Configuration
VITE_API_TARGET := http://localhost:$(SERVER_PORT)

# Timeouts
DEV_TIMEOUT := 120
```

### `docker-compose.yml`
**Purpose**: Multi-service deployment  
**Template**: *(Complete template in DEPLOYMENT.md)*

### `Dockerfile`
**Purpose**: Production container build  
**Template**: *(Complete template in DEPLOYMENT.md)*

This comprehensive file structure guide provides the exact blueprint needed to recreate every file in the AI-powered web research application, with templates, relationships, and creation instructions for each component.