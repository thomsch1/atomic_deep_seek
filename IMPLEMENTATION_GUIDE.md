# Implementation Guide

This guide provides detailed, step-by-step implementation patterns and code templates for recreating the AI-powered web research application. Each section includes exact code patterns, import statements, and implementation details that Claude Code can follow to rebuild the entire system.

## 🏗️ Backend Implementation Patterns

### 1. Base Research Agent Pattern

All research agents inherit from a common base class. Here's the exact implementation pattern:

#### `backend/src/agent/base/base_research_agent.py`

```python
"""Base class for all research agents in the Atomic Agents framework."""

import logging
from typing import Any, Dict, Optional, TypeVar, Generic
from abc import ABC, abstractmethod

from atomic_agents.lib.base.base_agent import BaseAgent
from agent.configuration import Configuration

T = TypeVar('T')
U = TypeVar('U')

class BaseResearchAgent(BaseAgent, Generic[T, U], ABC):
    """Base class for all research agents providing common functionality.
    
    This class provides:
    - Logging configuration
    - Configuration management
    - Error handling patterns
    - Common utilities for research tasks
    """
    
    def __init__(self, config: Optional[Configuration] = None):
        """Initialize the base research agent.
        
        Args:
            config: Configuration object with agent settings
        """
        self.config = config or Configuration()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize base agent with configuration
        super().__init__(
            agent_id=self.__class__.__name__,
            name=self.__class__.__name__.replace("Agent", " Agent"),
            instruction="Research agent for AI-powered information gathering",
        )
        
    @abstractmethod
    def run(self, agent_input: T) -> U:
        """Execute the agent's main functionality.
        
        Args:
            agent_input: Input data for the agent
            
        Returns:
            Processed output from the agent
        """
        pass
    
    def _log_execution_start(self, input_data: Any) -> None:
        """Log the start of agent execution."""
        self.logger.info(f"Starting execution with input: {type(input_data).__name__}")
        
    def _log_execution_end(self, output_data: Any) -> None:
        """Log the end of agent execution."""
        self.logger.info(f"Completed execution with output: {type(output_data).__name__}")
        
    def _handle_error(self, error: Exception, context: str) -> None:
        """Handle and log errors consistently."""
        self.logger.error(f"Error in {context}: {str(error)}")
        raise error
```

### 2. Agent Implementation Pattern

Each specific agent follows this exact pattern:

#### Query Generation Agent Template

```python
"""Query Generation Agent for creating targeted search queries."""

from typing import List, Optional
from pydantic import BaseModel, Field

from agent.base.base_research_agent import BaseResearchAgent
from agent.configuration import Configuration

# Input Schema
class QueryGenerationInput(BaseModel):
    """Input schema for query generation agent."""
    research_topic: str = Field(description="The main research topic or question")
    query_count: int = Field(default=3, description="Number of queries to generate")
    context: Optional[str] = Field(default=None, description="Additional context for query generation")

# Output Schema  
class QueryGenerationOutput(BaseModel):
    """Output schema for query generation agent."""
    search_queries: List[str] = Field(description="Generated search queries")
    query_reasoning: Optional[List[str]] = Field(description="Reasoning for each query")

class QueryGenerationAgent(BaseResearchAgent[QueryGenerationInput, QueryGenerationOutput]):
    """Agent that generates targeted search queries from research topics."""
    
    def __init__(self, config: Optional[Configuration] = None):
        super().__init__(config)
        self.system_prompt = self._build_system_prompt()
        
    def run(self, agent_input: QueryGenerationInput) -> QueryGenerationOutput:
        """Generate search queries from research topic."""
        try:
            self._log_execution_start(agent_input)
            
            # Core implementation
            queries = self._generate_queries(
                topic=agent_input.research_topic,
                count=agent_input.query_count,
                context=agent_input.context
            )
            
            result = QueryGenerationOutput(search_queries=queries)
            self._log_execution_end(result)
            return result
            
        except Exception as e:
            self._handle_error(e, "query generation")
    
    def _generate_queries(self, topic: str, count: int, context: Optional[str]) -> List[str]:
        """Core query generation logic."""
        # Implementation details using Gemini API
        # This method contains the actual AI query generation logic
        pass
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for query generation."""
        return """You are an expert research query generator.
        Generate diverse, specific search queries that will help gather comprehensive information on the given topic.
        Focus on different angles, perspectives, and aspects of the topic."""
```

### 3. Search Provider Pattern

All search providers implement a common interface:

#### `backend/src/agent/search/base_provider.py`

```python
"""Base search provider interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field

class SearchResult(BaseModel):
    """Standard search result format."""
    title: str = Field(description="Title of the search result")
    url: str = Field(description="URL of the search result")
    snippet: str = Field(description="Brief description or snippet")
    source: Optional[str] = Field(default=None, description="Source website")
    published_date: Optional[str] = Field(default=None, description="Publication date")
    domain_type: Optional[str] = Field(default=None, description="Type of domain (academic, news, etc.)")

class BaseSearchProvider(ABC):
    """Base class for all search providers."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.provider_name = self.__class__.__name__.replace("SearchProvider", "")
        
    @abstractmethod
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform search and return standardized results."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass
    
    def _parse_result(self, raw_result: dict) -> SearchResult:
        """Parse provider-specific result to standard format."""
        # Override in subclasses for provider-specific parsing
        pass
```

### 4. FastAPI Application Pattern

#### `backend/src/agent/app.py`

```python
"""FastAPI application for the research backend."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path

from agent.orchestrator import ResearchOrchestrator
from agent.state import ResearchRequest, ResearchResponse

# Initialize FastAPI app
app = FastAPI(
    title="AI Research Agent API",
    description="AI-powered web research with Atomic Agents",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = ResearchOrchestrator()

@app.post("/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest) -> ResearchResponse:
    """Conduct AI-powered research on a given question."""
    try:
        result = await orchestrator.run_research_async(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "atomic-research-agent"}

# Mount static files for frontend (production)
frontend_dist_path = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
if frontend_dist_path.exists():
    app.mount("/app", StaticFiles(directory=frontend_dist_path, html=True), name="frontend")
```

## 🎨 Frontend Implementation Patterns

### 1. React Component Pattern

All React components follow this structure:

#### Component Template

```typescript
// components/ComponentName.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { ComponentProps } from '@/types';
import { Button } from '@/components/ui/button';

interface ComponentNameProps {
  data: ComponentData;
  onUpdate?: (data: ComponentData) => void;
  className?: string;
}

export function ComponentName({ 
  data, 
  onUpdate, 
  className = '' 
}: ComponentNameProps) {
  const [localState, setLocalState] = useState<ComponentState>(initialState);
  
  useEffect(() => {
    // Effect logic
  }, [data]);
  
  const handleAction = useCallback((value: any) => {
    setLocalState(prev => ({ ...prev, value }));
    onUpdate?.(updatedData);
  }, [onUpdate]);
  
  return (
    <div className={`component-container ${className}`}>
      {/* Component JSX */}
    </div>
  );
}
```

### 2. API Service Pattern

#### `frontend/src/services/api.ts`

```typescript
"""API service for backend communication."""

export interface ResearchRequest {
  question: string;
  initial_search_query_count?: number;
  max_research_loops?: number;
  reasoning_model?: string;
  source_quality_filter?: 'high' | 'medium' | 'low' | null;
}

export interface ResearchResponse {
  final_answer: string;
  sources: Source[];
  research_loops_executed: number;
  total_queries: number;
}

export interface Source {
  title: string;
  url: string;
  label?: string;
  source_credibility?: 'high' | 'medium' | 'low';
  domain_type?: 'academic' | 'news' | 'official' | 'commercial' | 'other';
  quality_score?: number;
}

export class AtomicAgentAPI {
  private baseUrl: string;
  
  constructor() {
    // Dynamic base URL detection
    if (import.meta.env.VITE_API_URL) {
      this.baseUrl = import.meta.env.VITE_API_URL;
    } else if (import.meta.env.DEV) {
      this.baseUrl = '/api';
    } else if (window.location.pathname.startsWith('/app')) {
      this.baseUrl = '';
    } else {
      this.baseUrl = `${window.location.protocol}//${window.location.host}`;
    }
  }
  
  async conductResearch(request: ResearchRequest): Promise<ResearchResponse> {
    const response = await fetch(`${this.baseUrl}/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      throw new Error(`Research failed: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  }
  
  async healthCheck(): Promise<{status: string, service: string}> {
    const response = await fetch(`${this.baseUrl}/health`);
    return await response.json();
  }
}
```

### 3. State Management Pattern

#### Hook-based State Management

```typescript
// hooks/useResearchState.ts
import { useState, useCallback } from 'react';
import { ResearchResponse, ResearchRequest } from '@/services/api';

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
}

export function useResearchState() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const addMessage = useCallback((message: Message) => {
    setMessages(prev => [...prev, { ...message, timestamp: new Date() }]);
  }, []);
  
  const addUserMessage = useCallback((content: string) => {
    addMessage({
      id: Date.now().toString(),
      type: 'user',
      content,
    });
  }, [addMessage]);
  
  const addAssistantMessage = useCallback((response: ResearchResponse) => {
    addMessage({
      id: Date.now().toString(),
      type: 'assistant',
      content: response.final_answer,
      sources: response.sources,
    });
  }, [addMessage]);
  
  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);
  
  return {
    messages,
    isLoading,
    error,
    addUserMessage,
    addAssistantMessage,
    clearMessages,
    setIsLoading,
    setError,
  };
}
```

## 🔧 Configuration Patterns

### 1. Python Configuration Pattern

#### `backend/src/agent/configuration.py`

```python
"""Configuration management for the research application."""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class Configuration:
    """Central configuration for all agents and components."""
    
    # AI Model Configuration
    gemini_model: str = "gemini-1.5-flash"
    reasoning_model: Optional[str] = None
    
    # Search Configuration
    search_timeout: int = 30
    max_sources_per_query: int = 20
    quality_threshold: float = 0.5
    
    # Research Workflow Configuration
    default_initial_query_count: int = 3
    default_max_loops: int = 2
    max_allowed_loops: int = 10
    
    # API Keys (loaded from environment)
    gemini_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    langsmith_api_key: Optional[str] = field(default_factory=lambda: os.getenv("LANGSMITH_API_KEY"))
    google_cse_id: Optional[str] = field(default_factory=lambda: os.getenv("GOOGLE_CSE_ID"))
    google_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    searchapi_key: Optional[str] = field(default_factory=lambda: os.getenv("SEARCHAPI_KEY"))
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Configuration':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    def validate(self) -> None:
        """Validate configuration and raise errors for missing required fields."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required but not set")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
```

### 2. Environment Configuration Patterns

#### Development Environment (`.env` template)

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

## 🔄 Data Flow Implementation

### 1. Orchestrator Pattern

#### `backend/src/agent/orchestrator.py`

```python
"""Research orchestrator coordinating all agents."""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Any
import os

from agent.configuration import Configuration
from agent.state import ResearchRequest, ResearchResponse, ResearchState
from agent.agents.query_generation_agent import QueryGenerationAgent
from agent.agents.web_search_agent import WebSearchAgent
from agent.agents.reflection_agent import ReflectionAgent
from agent.agents.finalization_agent import FinalizationAgent

class ResearchOrchestrator:
    """Orchestrates the complete research workflow."""
    
    def __init__(self, config: Optional[Configuration] = None):
        self.config = config or Configuration()
        self.config.validate()
        
        # Lazy initialization for performance
        self._query_agent = None
        self._search_agent = None
        self._reflection_agent = None
        self._finalization_agent = None
        
        # Thread pool for parallel operations
        self._init_thread_pool()
    
    def _init_thread_pool(self):
        """Initialize thread pool with optimal sizing."""
        max_workers = min(max(os.cpu_count() * 2, 4), 10)
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
    
    @property
    def query_agent(self) -> QueryGenerationAgent:
        """Lazy-loaded query generation agent."""
        if self._query_agent is None:
            self._query_agent = QueryGenerationAgent(self.config)
        return self._query_agent
    
    @property
    def search_agent(self) -> WebSearchAgent:
        """Lazy-loaded web search agent."""
        if self._search_agent is None:
            self._search_agent = WebSearchAgent(self.config)
        return self._search_agent
    
    async def run_research_async(self, request: ResearchRequest) -> ResearchResponse:
        """Execute the complete research workflow asynchronously."""
        try:
            # Initialize research state
            state = ResearchState(
                original_question=request.question,
                initial_query_count=request.initial_search_query_count or 3,
                max_loops=request.max_research_loops or 2,
            )
            
            # Step 1: Generate initial queries
            queries = await self._generate_queries(state)
            
            # Step 2: Execute research loops
            for loop_count in range(state.max_loops):
                # Parallel web search
                search_results = await self._parallel_web_search(queries)
                state.web_research_results.extend(search_results)
                
                # Reflection and gap analysis
                reflection_result = await self._reflect_and_analyze(state)
                
                if reflection_result.is_complete:
                    break
                    
                # Generate additional queries for next loop
                queries = reflection_result.additional_queries
                state.research_loop_count += 1
            
            # Step 3: Finalize answer
            final_response = await self._finalize_answer(state)
            
            return final_response
            
        except Exception as e:
            # Error handling and logging
            raise RuntimeError(f"Research orchestration failed: {str(e)}")
    
    async def _parallel_web_search(self, queries: List[str]) -> List[Any]:
        """Execute web searches in parallel."""
        futures = []
        for query in queries:
            future = self._thread_pool.submit(
                self.search_agent.run,
                WebSearchInput(search_query=query)
            )
            futures.append(future)
        
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                # Log error but continue with other results
                self.logger.error(f"Search failed: {e}")
                
        return results
```

## 🧪 Testing Implementation Patterns

### 1. Backend Testing Pattern

#### Unit Test Template

```python
# backend/src/agent/test/test_agent_name.py
import pytest
from unittest.mock import Mock, patch
from agent.agents.agent_name import AgentName, AgentInput, AgentOutput
from agent.configuration import Configuration

class TestAgentName:
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration(
            gemini_api_key="test_key",
            gemini_model="gemini-1.5-flash"
        )
    
    @pytest.fixture
    def agent(self, config):
        """Create agent instance for testing."""
        return AgentName(config)
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input for testing."""
        return AgentInput(
            field1="test_value1",
            field2="test_value2"
        )
    
    def test_agent_initialization(self, agent, config):
        """Test agent initializes correctly."""
        assert agent.config == config
        assert agent.logger is not None
    
    def test_successful_execution(self, agent, sample_input):
        """Test successful agent execution."""
        result = agent.run(sample_input)
        
        assert isinstance(result, AgentOutput)
        assert result.output_field is not None
    
    @patch('agent.agents.agent_name.external_api_call')
    def test_with_mocked_dependencies(self, mock_api, agent, sample_input):
        """Test agent with mocked external dependencies."""
        # Setup mock
        mock_api.return_value = "mocked_response"
        
        result = agent.run(sample_input)
        
        # Verify mock was called
        mock_api.assert_called_once()
        assert result.output_field == "expected_result"
    
    def test_error_handling(self, agent):
        """Test agent error handling."""
        invalid_input = AgentInput(field1="", field2=None)
        
        with pytest.raises(ValueError, match="Invalid input"):
            agent.run(invalid_input)
```

### 2. Frontend Testing Pattern

#### React Component Test Template

```typescript
// frontend/src/components/__tests__/ComponentName.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { ComponentName } from '../ComponentName';

// Mock external dependencies
vi.mock('@/services/api', () => ({
  AtomicAgentAPI: vi.fn().mockImplementation(() => ({
    conductResearch: vi.fn().mockResolvedValue(mockResearchResponse),
  })),
}));

describe('ComponentName', () => {
  const defaultProps = {
    data: mockData,
    onUpdate: vi.fn(),
  };
  
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('renders with default props', () => {
    render(<ComponentName {...defaultProps} />);
    
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
  
  it('handles user interactions', async () => {
    const mockOnUpdate = vi.fn();
    render(<ComponentName {...defaultProps} onUpdate={mockOnUpdate} />);
    
    const button = screen.getByRole('button', { name: /submit/i });
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(mockOnUpdate).toHaveBeenCalledWith(expectedData);
    });
  });
  
  it('handles loading states', async () => {
    render(<ComponentName {...defaultProps} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
  });
  
  it('handles error states', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    // Mock API to throw error
    vi.mocked(AtomicAgentAPI).mockImplementation(() => ({
      conductResearch: vi.fn().mockRejectedValue(new Error('API Error')),
    }));
    
    render(<ComponentName {...defaultProps} />);
    
    // Trigger error scenario
    // Assert error handling
    
    consoleSpy.mockRestore();
  });
});
```

## 🔒 Error Handling Patterns

### Backend Error Handling

```python
# backend/src/agent/base/error_handling.py
"""Centralized error handling for research agents."""

import logging
from typing import Optional, Dict, Any
from enum import Enum

class ErrorType(Enum):
    """Types of errors that can occur."""
    VALIDATION_ERROR = "validation_error"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    PROCESSING_ERROR = "processing_error"

class ResearchError(Exception):
    """Base exception for research-related errors."""
    
    def __init__(
        self, 
        message: str, 
        error_type: ErrorType, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(message)

class ErrorHandler:
    """Centralized error handling and logging."""
    
    @staticmethod
    def handle_agent_error(
        error: Exception, 
        agent_name: str, 
        context: str = ""
    ) -> ResearchError:
        """Handle and convert errors to ResearchError format."""
        
        logger = logging.getLogger(agent_name)
        
        if isinstance(error, ResearchError):
            logger.error(f"Research error in {context}: {error.message}")
            return error
        
        # Convert standard exceptions
        if isinstance(error, ValueError):
            research_error = ResearchError(
                message=str(error),
                error_type=ErrorType.VALIDATION_ERROR,
                details={"context": context}
            )
        elif isinstance(error, ConnectionError):
            research_error = ResearchError(
                message="Network connection failed",
                error_type=ErrorType.NETWORK_ERROR,
                details={"original_error": str(error), "context": context}
            )
        else:
            research_error = ResearchError(
                message=f"Unexpected error: {str(error)}",
                error_type=ErrorType.PROCESSING_ERROR,
                details={"original_error": str(error), "context": context}
            )
        
        logger.error(f"Error in {agent_name} - {context}: {research_error.message}")
        return research_error
```

This implementation guide provides the exact patterns, templates, and code structures needed to recreate every component of the AI research application. Each pattern includes proper error handling, logging, testing, and follows the established architectural principles.