# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio

from agent.orchestrator import ResearchOrchestrator
from agent.state import Message

# Define the FastAPI app
app = FastAPI(title="Atomic Research Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the orchestrator
orchestrator = ResearchOrchestrator()


# Pydantic models for API
class ResearchRequest(BaseModel):
    question: str
    initial_search_query_count: Optional[int] = 3
    max_research_loops: Optional[int] = 2
    reasoning_model: Optional[str] = None


class ResearchResponse(BaseModel):
    final_answer: str
    sources: List[Dict[str, Any]]
    research_loops_executed: int
    total_queries: int


@app.post("/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """Conduct research on a given question."""
    try:
        result = await orchestrator.run_research_async(
            request.question,
            initial_search_query_count=request.initial_search_query_count,
            max_research_loops=request.max_research_loops,
            reasoning_model=request.reasoning_model
        )
        
        return ResearchResponse(
            final_answer=result["final_answer"],
            sources=result["sources_gathered"],
            research_loops_executed=result["research_loops_executed"],
            total_queries=result["total_queries"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "atomic-research-agent"}


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    return StaticFiles(directory=build_path, html=True)


# Mount the frontend under /app (no longer conflicts with LangGraph)
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
