# API Documentation

This document provides comprehensive documentation for the AI-powered web research application's REST API, including endpoints, request/response schemas, and integration examples.

## 🌐 API Overview

The backend exposes a RESTful API built with FastAPI that provides research capabilities through intelligent agent orchestration. The API supports both development and production environments with automatic OpenAPI documentation.

### Base URLs

- **Development**: `http://localhost:2024`
- **Production**: `http://localhost:8123` (Docker deployment)
- **Frontend Integration**: `/api` (proxied through Vite dev server)

### API Documentation Access

- **Swagger UI**: `http://localhost:2024/docs`
- **ReDoc**: `http://localhost:2024/redoc`
- **OpenAPI JSON**: `http://localhost:2024/openapi.json`

## 🚀 Endpoints

### Research Endpoint

#### `POST /research`

Conducts comprehensive AI-powered research on a given question.

**Request Body:**

```json
{
  "question": "What is artificial intelligence and how does it work?",
  "initial_search_query_count": 3,
  "max_research_loops": 2,
  "reasoning_model": "gemini-1.5-flash",
  "source_quality_filter": "high"
}
```

**Response:**

```json
{
  "final_answer": "Artificial intelligence (AI) is a branch of computer science...",
  "sources": [
    {
      "title": "Introduction to Artificial Intelligence",
      "url": "https://example.com/ai-intro",
      "label": "[1]",
      "source_credibility": "high",
      "domain_type": "academic", 
      "quality_score": 0.95,
      "quality_breakdown": {
        "credibility": 0.98,
        "relevance": 0.92,
        "completeness": 0.96,
        "recency": 0.89,
        "authority": 0.97
      }
    }
  ],
  "research_loops_executed": 2,
  "total_queries": 7
}
```

### Health Check Endpoint

#### `GET /health`

Returns the service health status.

**Response:**

```json
{
  "status": "healthy",
  "service": "atomic-research-agent"
}
```

## 📋 Data Schemas

### Request Schemas

#### ResearchRequest

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `question` | string | ✅ Yes | - | The research question or topic to investigate |
| `initial_search_query_count` | integer | ❌ No | 3 | Number of initial search queries to generate (1-10) |
| `max_research_loops` | integer | ❌ No | 2 | Maximum number of research loops to perform (1-10) |
| `reasoning_model` | string | ❌ No | null | Gemini model variant to use for reasoning tasks |
| `source_quality_filter` | string | ❌ No | null | Minimum source quality level: "high", "medium", "low", or null |

```typescript
interface ResearchRequest {
  question: string;
  initial_search_query_count?: number; // 1-10
  max_research_loops?: number;         // 1-10
  reasoning_model?: string;            // e.g., "gemini-1.5-flash"
  source_quality_filter?: "high" | "medium" | "low" | null;
}
```

### Response Schemas

#### ResearchResponse

| Field | Type | Description |
|-------|------|-------------|
| `final_answer` | string | The synthesized research answer with citations |
| `sources` | Source[] | Array of sources used in the research |
| `research_loops_executed` | integer | Number of research loops actually performed |
| `total_queries` | integer | Total number of search queries executed |

```typescript
interface ResearchResponse {
  final_answer: string;
  sources: Source[];
  research_loops_executed: number;
  total_queries: number;
}
```

#### Source Schema

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Title of the source document |
| `url` | string | Full URL of the source |
| `label` | string | Citation label (e.g., "[1]", "[2]") |
| `source_credibility` | string | Credibility level: "high", "medium", "low" |
| `domain_type` | string | Domain classification: "academic", "news", "official", "commercial", "other" |
| `quality_score` | number | Overall quality score (0.0-1.0) |
| `quality_breakdown` | QualityBreakdown | Detailed quality metrics |

```typescript
interface Source {
  title: string;
  url: string;
  label?: string;
  source_credibility?: "high" | "medium" | "low";
  domain_type?: "academic" | "news" | "official" | "commercial" | "other";
  quality_score?: number; // 0.0-1.0
  quality_breakdown?: QualityBreakdown;
}
```

#### QualityBreakdown Schema

| Field | Type | Description |
|-------|------|-------------|
| `credibility` | number | Source credibility score (0.0-1.0) |
| `relevance` | number | Content relevance score (0.0-1.0) |
| `completeness` | number | Information completeness score (0.0-1.0) |
| `recency` | number | Information recency score (0.0-1.0) |
| `authority` | number | Source authority score (0.0-1.0) |

```typescript
interface QualityBreakdown {
  credibility?: number;   // 0.0-1.0
  relevance?: number;     // 0.0-1.0
  completeness?: number;  // 0.0-1.0
  recency?: number;       // 0.0-1.0
  authority?: number;     // 0.0-1.0
}
```

## 🔧 Configuration Parameters

### Research Parameters

#### Initial Search Query Count

Controls the number of diverse search queries generated from the input question.

- **Range**: 1-10 queries
- **Default**: 3
- **Impact**: More queries provide broader coverage but increase response time
- **Recommendation**: 
  - Low effort: 1-2 queries
  - Medium effort: 3-5 queries  
  - High effort: 5-10 queries

#### Maximum Research Loops

Determines the maximum number of iterative research refinement cycles.

- **Range**: 1-10 loops
- **Default**: 2
- **Impact**: More loops improve answer quality but increase processing time
- **Process**: Each loop performs reflection, identifies gaps, and conducts additional searches

#### Reasoning Model Selection

Specifies the Gemini model variant for AI reasoning tasks.

- **Options**: 
  - `"gemini-1.5-flash"` (default) - Fast, efficient for most tasks
  - `"gemini-1.5-pro"` - Higher quality for complex reasoning
  - `null` - Use system default
- **Impact**: Model choice affects response quality, speed, and cost

#### Source Quality Filter

Sets the minimum quality threshold for source inclusion.

- **Options**:
  - `"high"` - Only high-credibility sources (academic, official)
  - `"medium"` - Medium to high credibility sources
  - `"low"` - Include all sources regardless of quality
  - `null` - No filtering (default)
- **Impact**: Higher filtering improves answer reliability but may reduce source diversity

## 📡 API Client Examples

### JavaScript/TypeScript Client

```typescript
class ResearchAPIClient {
  private baseURL: string;
  
  constructor(baseURL: string = 'http://localhost:2024') {
    this.baseURL = baseURL;
  }
  
  async conductResearch(request: ResearchRequest): Promise<ResearchResponse> {
    const response = await fetch(`${this.baseURL}/research`, {
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
    const response = await fetch(`${this.baseURL}/health`);
    return await response.json();
  }
}

// Usage example
const client = new ResearchAPIClient();

const result = await client.conductResearch({
  question: "What are the latest developments in quantum computing?",
  initial_search_query_count: 5,
  max_research_loops: 3,
  reasoning_model: "gemini-1.5-pro",
  source_quality_filter: "high"
});

console.log(result.final_answer);
console.log(`Used ${result.sources.length} sources in ${result.research_loops_executed} loops`);
```

### Python Client

```python
import httpx
from typing import Optional, List, Dict, Any

class ResearchAPIClient:
    def __init__(self, base_url: str = "http://localhost:2024"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url)
    
    def conduct_research(
        self,
        question: str,
        initial_search_query_count: int = 3,
        max_research_loops: int = 2,
        reasoning_model: Optional[str] = None,
        source_quality_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Conduct research on a given question."""
        
        request_data = {
            "question": question,
            "initial_search_query_count": initial_search_query_count,
            "max_research_loops": max_research_loops,
        }
        
        if reasoning_model:
            request_data["reasoning_model"] = reasoning_model
        if source_quality_filter:
            request_data["source_quality_filter"] = source_quality_filter
        
        response = self.client.post("/research", json=request_data)
        response.raise_for_status()
        
        return response.json()
    
    def health_check(self) -> Dict[str, str]:
        """Check service health."""
        response = self.client.get("/health")
        response.raise_for_status()
        return response.json()

# Usage example
client = ResearchAPIClient()

result = client.conduct_research(
    question="How does machine learning impact healthcare?",
    initial_search_query_count=4,
    max_research_loops=2,
    reasoning_model="gemini-1.5-flash",
    source_quality_filter="medium"
)

print(f"Answer: {result['final_answer']}")
print(f"Sources: {len(result['sources'])}")
print(f"Loops: {result['research_loops_executed']}")
```

### cURL Examples

#### Basic Research Request

```bash
curl -X POST "http://localhost:2024/research" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the current state of renewable energy adoption?",
    "initial_search_query_count": 3,
    "max_research_loops": 2
  }'
```

#### Advanced Research with Quality Filter

```bash  
curl -X POST "http://localhost:2024/research" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Latest breakthroughs in artificial intelligence research",
    "initial_search_query_count": 5,
    "max_research_loops": 3,
    "reasoning_model": "gemini-1.5-pro",
    "source_quality_filter": "high"
  }'
```

#### Health Check

```bash
curl -X GET "http://localhost:2024/health"
```

## ⚡ Performance Considerations

### Request Processing Time

Research requests involve multiple AI model calls and web searches, resulting in processing times that vary based on:

- **Query Complexity**: Complex topics require more processing
- **Search Query Count**: More queries increase parallel search time
- **Research Loops**: Additional loops add iterative processing time
- **Source Quality Filtering**: Higher filtering requires more analysis
- **Model Selection**: Pro models are slower than Flash models

**Typical Response Times:**
- Simple query (1 query, 1 loop): 10-30 seconds
- Standard query (3 queries, 2 loops): 30-60 seconds  
- Complex query (5 queries, 3+ loops): 60-120 seconds

### Rate Limiting

The API doesn't implement built-in rate limiting, but external providers (Google Gemini, search APIs) may have their own limits:

- **Gemini API**: Per-minute and per-day quotas
- **Google Custom Search**: 100 queries/day (free tier)
- **SearchAPI**: Based on subscription plan

### Error Handling

#### Common HTTP Status Codes

| Code | Description | Cause | Solution |
|------|-------------|--------|----------|
| 200 | Success | Request processed successfully | - |
| 400 | Bad Request | Invalid request parameters | Check request schema |
| 422 | Validation Error | Pydantic validation failed | Fix request data types |
| 500 | Internal Server Error | Processing error or API failure | Check logs, retry |
| 503 | Service Unavailable | External API unavailable | Wait and retry |

#### Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "error_type": "ValidationError|APIError|ProcessingError",
  "request_id": "unique-request-identifier"
}
```

#### Error Handling Best Practices

```typescript
async function handleResearchRequest(request: ResearchRequest): Promise<ResearchResponse> {
  try {
    return await client.conductResearch(request);
  } catch (error) {
    if (error.status === 422) {
      // Validation error - fix request parameters
      console.error('Invalid request parameters:', error.detail);
      throw new Error('Please check your request parameters');
    } else if (error.status === 500) {
      // Server error - retry with exponential backoff
      console.error('Server error, retrying...', error.detail);
      return await retryWithBackoff(() => client.conductResearch(request));
    } else if (error.status === 503) {
      // Service unavailable - wait and retry
      console.error('Service temporarily unavailable:', error.detail);
      await new Promise(resolve => setTimeout(resolve, 5000));
      return await client.conductResearch(request);
    }
    throw error;
  }
}
```

## 🔐 Authentication & Security

### Current Implementation

The current API doesn't require authentication, but production deployments should consider:

- **API Key Authentication**: Add API keys for access control
- **Rate Limiting**: Implement per-client rate limits
- **CORS Configuration**: Restrict origins in production
- **Input Sanitization**: Validate and sanitize user inputs
- **Logging**: Log requests for monitoring and debugging

### Future Security Enhancements

```python
# Example API key authentication
from fastapi import Depends, HTTPException, Header

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.post("/research")
async def conduct_research(
    request: ResearchRequest,
    api_key: str = Depends(verify_api_key)
):
    # Protected endpoint implementation
    pass
```

## 📊 API Usage Analytics

### Monitoring Endpoints

Consider implementing these monitoring endpoints for production:

```python
@app.get("/metrics")
async def get_metrics():
    return {
        "total_requests": request_counter,
        "average_response_time": avg_response_time,
        "success_rate": success_rate,
        "active_connections": active_connections
    }

@app.get("/research/stats")  
async def get_research_stats():
    return {
        "total_research_requests": research_counter,
        "average_sources_per_request": avg_sources,
        "average_loops_per_request": avg_loops,
        "popular_topics": popular_topics_list
    }
```

## 🧪 Testing the API

### Manual Testing

Use the interactive Swagger UI at `http://localhost:2024/docs` for manual testing:

1. Start the development server: `make dev-backend`
2. Navigate to `http://localhost:2024/docs`
3. Click "Try it out" on the `/research` endpoint
4. Enter your test parameters and click "Execute"
5. View the response in the interface

### Automated Testing

```python
# Example pytest test
import pytest
from fastapi.testclient import TestClient
from agent.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_research_endpoint_success(client):
    response = client.post(
        "/research",
        json={
            "question": "What is Python programming?",
            "initial_search_query_count": 2,
            "max_research_loops": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "final_answer" in data
    assert "sources" in data
    assert len(data["sources"]) > 0
    
def test_research_endpoint_validation_error(client):
    response = client.post(
        "/research",
        json={"question": ""}  # Empty question should fail
    )
    assert response.status_code == 422
```

---

This API documentation provides comprehensive information for integrating with the AI-powered research system. The RESTful design ensures easy integration across different programming languages and platforms.