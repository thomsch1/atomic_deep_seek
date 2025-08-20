export interface QualityMetrics {
  source_credibility: number;
  content_relevance: number;
  information_completeness: number;
  recency_score: number;
  overall_score: number;
}

export interface Source {
  title: string;
  url: string;
  label?: string;
  content?: string;
  source_credibility?: string;
  domain_type?: string;
  quality_score?: number;
  quality_breakdown?: QualityMetrics;
}

export interface QualitySummary {
  total_sources: number;
  included_sources: number;
  filtered_sources: number;
  average_quality_score: number;
  quality_threshold: number;
}

export interface ResearchRequest {
  question: string;
  initial_search_query_count?: number;
  max_research_loops?: number;
  reasoning_model?: string;
  source_quality_filter?: string;
  enhanced_filtering?: boolean;
  quality_threshold?: number;
}

export interface ResearchResponse {
  final_answer: string;
  sources: Source[];
  filtered_sources?: Source[];
  quality_summary?: QualitySummary;
  filtering_applied?: boolean;
  research_loops_executed: number;
  total_queries: number;
  performance_profile?: any; // Backend performance data
}

// Custom Message interface to replace LangChain types
export interface Message {
  type: "human" | "ai";
  content: string;
  id: string;
}

import { performanceProfiler } from './performance-profiler';

export class AtomicAgentAPI {
  private baseUrl: string;

  constructor() {
    // Use environment variable if available, otherwise detect based on current URL
    if (import.meta.env.VITE_API_URL) {
      this.baseUrl = import.meta.env.VITE_API_URL;
    } else if (import.meta.env.DEV) {
      // Development mode: always use proxy regardless of path
      this.baseUrl = '/api';
    } else if (window.location.pathname.startsWith('/app')) {
      // Production: running under /app route (served by backend), use relative URLs
      this.baseUrl = '';
    } else {
      // Dynamic production: use same origin as current page
      this.baseUrl = `${window.location.protocol}//${window.location.host}`;
    }
    
    console.log('🚀 API Service initialized:', {
      baseUrl: this.baseUrl,
      currentLocation: window.location.href,
      isDev: import.meta.env.DEV,
      pathStartsWithApp: window.location.pathname.startsWith('/app'),
      hasViteApiUrl: !!import.meta.env.VITE_API_URL
    });
  }
  
  async conductResearch(request: ResearchRequest): Promise<ResearchResponse> {
    // Start performance timing
    const sessionId = performanceProfiler.startTiming(request.question);
    
    const url = `${this.baseUrl}/research`;
    console.log('🔍 API Request:', {
      baseUrl: this.baseUrl,
      fullUrl: url,
      currentLocation: window.location.href,
      isDev: import.meta.env.DEV,
      request,
      sessionId
    });
    
    try {
      // Mark request preparation complete
      performanceProfiler.markRequestPreparation(sessionId);
      
      // Mark network request start
      performanceProfiler.markNetworkRequest(sessionId);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      
      console.log('📡 API Response:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        sessionId
      });
      
      if (!response.ok) {
        throw new Error(`Research failed: ${response.status} ${response.statusText}`);
      }
      
      const result = await response.json();
      
      // Mark response processing start
      performanceProfiler.markResponseProcessing(sessionId, result);
      
      console.log('✅ API Success:', result);
      
      // Note: UI rendering timing should be marked by the component that renders the result
      
      return result;
    } catch (error) {
      console.error('❌ API Error:', error);
      throw error;
    }
  }

  async healthCheck(): Promise<{status: string, service: string}> {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }
}