from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


class Message(BaseModel):
    """Message model for chat interactions."""
    role: str = Field(description="Role of the message sender")
    content: str = Field(description="Content of the message")


class Source(BaseModel):
    """Source information for citations."""
    title: str = Field(description="Title of the source")
    url: str = Field(description="URL of the source") 
    short_url: Optional[str] = Field(default=None, description="Shortened URL for token efficiency")
    label: Optional[str] = Field(default=None, description="Citation label")


class Citation(BaseModel):
    """Citation metadata."""
    start_index: int = Field(description="Start index in text")
    end_index: int = Field(description="End index in text")
    segments: List[Source] = Field(default_factory=list, description="Source segments")


class ResearchState(BaseModel):
    """Complete state for the research workflow."""
    messages: List[Message] = Field(default_factory=list, description="Chat messages")
    search_queries: List[str] = Field(default_factory=list, description="Generated search queries")
    web_research_results: List[str] = Field(default_factory=list, description="Research summaries")
    sources_gathered: List[Source] = Field(default_factory=list, description="All gathered sources")
    initial_search_query_count: int = Field(default=3, description="Number of initial queries")
    max_research_loops: int = Field(default=2, description="Maximum research loops")
    research_loop_count: int = Field(default=0, description="Current research loop")
    reasoning_model: Optional[str] = Field(default=None, description="Model for reasoning tasks")
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))
    
    def add_search_queries(self, queries: List[str]):
        """Add search queries to the state."""
        self.search_queries.extend(queries)
    
    def add_research_result(self, result: str):
        """Add a research result to the state."""
        self.web_research_results.append(result)
    
    def add_sources(self, sources: List[Source]):
        """Add sources to the gathered sources."""
        self.sources_gathered.extend(sources)


# Input/Output schemas for atomic agents
class QueryGenerationInput(BaseModel):
    """
    Input for generating search queries for research topics.
    
    You are a query generation agent. Your task is to analyze the research topic and 
    generate effective search queries that will help gather comprehensive information.
    Consider the current date for temporal relevance and generate the specified number
    of diverse, specific queries that cover different aspects of the topic.
    """
    research_topic: str = Field(description="The research topic to investigate thoroughly")
    number_of_queries: int = Field(default=3, description="Exact number of search queries to generate")
    current_date: str = Field(description="Current date for temporal context and recency")


class QueryGenerationOutput(BaseModel):
    """Output containing generated search queries and reasoning."""
    queries: List[str] = Field(description="List of generated search queries, diverse and specific")
    rationale: str = Field(description="Brief explanation of the search strategy and query selection reasoning")


class WebSearchInput(BaseModel):
    """Input for web search agent."""
    search_query: str = Field(description="Query to search for")
    query_id: int = Field(description="Unique identifier for this query")
    current_date: str = Field(description="Current date for context")


class WebSearchOutput(BaseModel):
    """Output from web search agent."""
    content: str = Field(description="Research content found")
    sources: List[Source] = Field(description="Source information")
    citations: List[Citation] = Field(description="Citation metadata")


class ReflectionInput(BaseModel):
    """Input for reflection agent."""
    research_topic: str = Field(description="Original research topic")
    summaries: List[str] = Field(description="Research summaries to analyze")
    current_loop: int = Field(description="Current research loop count")


class ReflectionOutput(BaseModel):
    """Output from reflection agent."""
    is_sufficient: bool = Field(description="Whether research is sufficient")
    knowledge_gap: str = Field(description="Identified knowledge gaps")
    follow_up_queries: List[str] = Field(description="Suggested follow-up queries")


class FinalizationInput(BaseModel):
    """Input for answer finalization agent."""
    research_topic: str = Field(description="Original research topic") 
    summaries: List[str] = Field(description="All research summaries")
    sources: List[Source] = Field(description="All gathered sources")
    current_date: str = Field(description="Current date for context")


class FinalizationOutput(BaseModel):
    """Output from finalization agent."""
    final_answer: str = Field(description="Complete research answer")
    used_sources: List[Source] = Field(description="Sources cited in answer")


class SearchStateOutput(BaseModel):
    """Final output from the search workflow."""
    running_summary: Optional[str] = Field(default=None, description="Final research report")
