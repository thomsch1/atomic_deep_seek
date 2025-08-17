# Atomic Agent Research Backend

This backend has been migrated from LangChain/LangGraph to Atomic Agents for improved modularity, maintainability, and performance.

## Architecture

The system now uses:
- **Atomic Agents**: Modular AI agents with clear input/output schemas
- **Pydantic**: Type-safe data models and validation
- **FastAPI**: Modern async web framework
- **Python Control Flow**: Explicit orchestration instead of graph execution

## Key Components

### Agents (`src/agent/agents.py`)
- `QueryGenerationAgent`: Generates search queries from research topics
- `WebSearchAgent`: Performs web research using Google Search API
- `ReflectionAgent`: Analyzes research sufficiency and identifies gaps
- `FinalizationAgent`: Creates final answers with proper citations

### Orchestrator (`src/agent/orchestrator.py`)
- `ResearchOrchestrator`: Coordinates the complete research workflow
- Handles parallel search execution
- Manages research loops and state transitions

### State Management (`src/agent/state.py`)
- Pydantic models for type-safe data handling
- Clear input/output schemas for each agent
- Replaces LangGraph's TypedDict with validated models

## Installation

```bash
cd backend
pip install -e .
```

## Running the Server

### Development Server
```bash
python run_server.py --reload --host 0.0.0.0 --port 8000
```

### Production Server
```bash
python run_server.py --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST `/research`
Conduct research on a given question.

**Request:**
```json
{
  "question": "What are the latest developments in quantum computing?",
  "initial_search_query_count": 3,
  "max_research_loops": 2,
  "reasoning_model": "gemini-2.5-pro"
}
```

**Response:**
```json
{
  "final_answer": "Based on research, quantum computing has seen...",
  "sources": [
    {
      "title": "Quantum Research Paper",
      "url": "https://example.com/paper",
      "label": "Research Paper"
    }
  ],
  "research_loops_executed": 1,
  "total_queries": 4
}
```

### GET `/health`
Health check endpoint.

### GET `/docs`
Interactive API documentation (Swagger UI).

## Command Line Interface

```bash
python examples/cli_research.py "Your research question here"
```

Options:
- `--initial-queries N`: Number of initial search queries (default: 3)
- `--max-loops N`: Maximum research loops (default: 2)
- `--reasoning-model MODEL`: Model for final answer (default: gemini-2.5-pro)

## Environment Variables

Required:
- `GEMINI_API_KEY`: Google Generative AI API key

Optional:
- `QUERY_GENERATOR_MODEL`: Model for query generation (default: gemini-2.0-flash)
- `REFLECTION_MODEL`: Model for reflection (default: gemini-2.5-flash)
- `ANSWER_MODEL`: Model for final answer (default: gemini-2.5-pro)

## Configuration

The system uses `Configuration` class in `src/agent/configuration.py`:

```python
from agent.configuration import Configuration

config = Configuration(
    query_generator_model="gemini-2.0-flash",
    reflection_model="gemini-2.5-flash",
    answer_model="gemini-2.5-pro",
    number_of_initial_queries=3,
    max_research_loops=2
)
```

## Migration from LangGraph

### Key Changes
1. **Dependencies**: Replaced LangGraph/LangChain with Atomic Agents
2. **State Management**: TypedDict → Pydantic models
3. **Execution**: Graph nodes → Python orchestrator
4. **Configuration**: RunnableConfig → AgentConfig
5. **CLI**: `langgraph dev` → `python run_server.py`

### Compatibility
- The `graph.py` module maintains backward compatibility
- Existing `invoke()` interface still works
- FastAPI endpoints provide the same functionality

### Benefits
- **Better Type Safety**: Pydantic validation ensures data integrity
- **Improved Modularity**: Each agent is independently testable
- **Clearer Control Flow**: Explicit Python logic instead of graph execution
- **Easier Debugging**: Standard Python debugging tools work
- **Reduced Dependencies**: Fewer external packages required

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run migration comparison tests
pytest tests/test_migration_comparison.py -v

# Generate migration report
python tests/test_migration_comparison.py
```

## Development

### Adding New Agents
1. Create agent class in `agents.py`
2. Define input/output schemas in `state.py`
3. Add agent to orchestrator workflow
4. Write tests for the new functionality

### Debugging
- Use standard Python debugging tools
- Enable FastAPI debug mode: `python run_server.py --reload`
- Check logs for detailed error information

## Production Deployment

The system no longer requires PostgreSQL/Redis for basic operation. For production:

1. Set environment variables
2. Use a production ASGI server like Gunicorn:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker agent.app:app
   ```
3. Configure proper CORS settings in `app.py`
4. Set up monitoring and logging as needed

## Performance

The Atomic Agent implementation provides:
- Parallel search execution using ThreadPoolExecutor
- Async support for concurrent requests
- Reduced memory overhead without LangGraph state management
- Faster startup times without graph compilation