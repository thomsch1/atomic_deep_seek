/**
 * Frontend performance profiling service for deep search system.
 * Measures end-to-end timing from user input to answer display.
 */

export interface PerformanceMetrics {
  // Frontend timings
  userInputTime: number;
  requestPreparationTime: number;
  networkRequestTime: number;
  responseProcessingTime: number;
  uiRenderTime: number;
  totalFrontendTime: number;
  
  // Backend timings (if available in response)
  backendProcessingTime?: number;
  stepTimings?: {
    queryGeneration?: number;
    initialSearches?: number[];
    reflectionLoops?: number[];
    finalization?: number;
  };
  
  // Request details
  questionLength: number;
  answerLength: number;
  sourcesCount: number;
  timestamp: string;
}

export interface TimingSession {
  sessionId: string;
  startTime: number;
  metrics: Partial<PerformanceMetrics>;
  completed: boolean;
}

export class FrontendPerformanceProfiler {
  private sessions: Map<string, TimingSession> = new Map();
  private sessionCounter = 0;
  
  /**
   * Start timing a new research request
   */
  startTiming(question: string): string {
    const sessionId = `session_${++this.sessionCounter}_${Date.now()}`;
    const startTime = performance.now();
    
    const session: TimingSession = {
      sessionId,
      startTime,
      metrics: {
        userInputTime: startTime,
        questionLength: question.length,
        timestamp: new Date().toISOString(),
      },
      completed: false,
    };
    
    this.sessions.set(sessionId, session);
    console.log(`🕐 Started timing session: ${sessionId}`);
    
    return sessionId;
  }
  
  /**
   * Mark the point where request preparation begins
   */
  markRequestPreparation(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    if (!session) return;
    
    const now = performance.now();
    session.metrics.requestPreparationTime = now - session.startTime;
  }
  
  /**
   * Mark the point where network request begins
   */
  markNetworkRequest(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    if (!session) return;
    
    const now = performance.now();
    const prepTime = session.metrics.requestPreparationTime || 0;
    session.metrics.networkRequestTime = now - session.startTime - prepTime;
  }
  
  /**
   * Mark the point where response processing begins
   */
  markResponseProcessing(sessionId: string, response: any): void {
    const session = this.sessions.get(sessionId);
    if (!session) return;
    
    const now = performance.now();
    const prevTime = (session.metrics.requestPreparationTime || 0) + 
                    (session.metrics.networkRequestTime || 0);
    session.metrics.responseProcessingTime = now - session.startTime - prevTime;
    
    // Extract backend performance data if available
    if (response.performance_profile) {
      session.metrics.backendProcessingTime = response.performance_profile.backend_processing;
      session.metrics.stepTimings = {
        queryGeneration: response.performance_profile.query_generation?.duration,
        initialSearches: response.performance_profile.initial_searches?.map((s: any) => s.duration) || [],
        reflectionLoops: response.performance_profile.reflection_loops?.map((r: any) => r.duration) || [],
        finalization: response.performance_profile.finalization?.duration,
      };
    }
    
    // Extract response metadata
    session.metrics.answerLength = response.final_answer?.length || 0;
    session.metrics.sourcesCount = response.sources?.length || 0;
  }
  
  /**
   * Mark the point where UI rendering completes
   */
  markUIRender(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    if (!session) return;
    
    const now = performance.now();
    const prevTime = (session.metrics.requestPreparationTime || 0) + 
                    (session.metrics.networkRequestTime || 0) + 
                    (session.metrics.responseProcessingTime || 0);
    session.metrics.uiRenderTime = now - session.startTime - prevTime;
    session.metrics.totalFrontendTime = now - session.startTime;
    session.completed = true;
    
    console.log(`✅ Completed timing session: ${sessionId}`, session.metrics);
  }
  
  /**
   * Get performance metrics for a session
   */
  getMetrics(sessionId: string): PerformanceMetrics | null {
    const session = this.sessions.get(sessionId);
    return session?.metrics as PerformanceMetrics || null;
  }
  
  /**
   * Get all completed sessions
   */
  getAllMetrics(): PerformanceMetrics[] {
    return Array.from(this.sessions.values())
      .filter(session => session.completed)
      .map(session => session.metrics as PerformanceMetrics);
  }
  
  /**
   * Generate performance report
   */
  generateReport(): any {
    const allMetrics = this.getAllMetrics();
    
    if (allMetrics.length === 0) {
      return { error: 'No completed sessions to analyze' };
    }
    
    // Calculate statistics
    const totalTimes = allMetrics.map(m => m.totalFrontendTime);
    const networkTimes = allMetrics.map(m => m.networkRequestTime).filter(t => t !== undefined) as number[];
    const backendTimes = allMetrics.map(m => m.backendProcessingTime).filter(t => t !== undefined) as number[];
    
    const calculateStats = (values: number[]) => {
      if (values.length === 0) return null;
      values.sort((a, b) => a - b);
      return {
        count: values.length,
        min: Math.min(...values),
        max: Math.max(...values),
        mean: values.reduce((a, b) => a + b, 0) / values.length,
        median: values[Math.floor(values.length / 2)],
      };
    };
    
    // Analyze step performance
    const stepAnalysis = this.analyzeStepPerformance(allMetrics);
    
    return {
      summary: {
        totalSessions: allMetrics.length,
        timeRange: {
          start: Math.min(...allMetrics.map(m => new Date(m.timestamp).getTime())),
          end: Math.max(...allMetrics.map(m => new Date(m.timestamp).getTime())),
        },
      },
      timing_statistics: {
        total_frontend_time: calculateStats(totalTimes),
        network_request_time: calculateStats(networkTimes),
        backend_processing_time: calculateStats(backendTimes),
      },
      step_analysis: stepAnalysis,
      insights: this.generateInsights(allMetrics),
      detailed_sessions: allMetrics,
      timestamp: new Date().toISOString(),
    };
  }
  
  private analyzeStepPerformance(metrics: PerformanceMetrics[]): any {
    const stepData = {
      queryGeneration: [] as number[],
      initialSearches: [] as number[],
      reflectionLoops: [] as number[],
      finalization: [] as number[],
    };
    
    metrics.forEach(m => {
      if (m.stepTimings) {
        if (m.stepTimings.queryGeneration) stepData.queryGeneration.push(m.stepTimings.queryGeneration);
        if (m.stepTimings.initialSearches) stepData.initialSearches.push(...m.stepTimings.initialSearches);
        if (m.stepTimings.reflectionLoops) stepData.reflectionLoops.push(...m.stepTimings.reflectionLoops);
        if (m.stepTimings.finalization) stepData.finalization.push(m.stepTimings.finalization);
      }
    });
    
    const calculateStats = (values: number[]) => {
      if (values.length === 0) return { count: 0 };
      values.sort((a, b) => a - b);
      return {
        count: values.length,
        min: Math.min(...values),
        max: Math.max(...values),
        mean: values.reduce((a, b) => a + b, 0) / values.length,
        median: values[Math.floor(values.length / 2)],
      };
    };
    
    return {
      query_generation: calculateStats(stepData.queryGeneration),
      initial_searches: calculateStats(stepData.initialSearches),
      reflection_loops: calculateStats(stepData.reflectionLoops),
      finalization: calculateStats(stepData.finalization),
    };
  }
  
  private generateInsights(metrics: PerformanceMetrics[]): string[] {
    const insights: string[] = [];
    
    if (metrics.length === 0) return insights;
    
    // Analyze average response times
    const avgTotal = metrics.reduce((sum, m) => sum + m.totalFrontendTime, 0) / metrics.length;
    
    if (avgTotal < 3000) {
      insights.push('🚀 Excellent response times - under 3 seconds average');
    } else if (avgTotal < 8000) {
      insights.push('⚡ Good response times - under 8 seconds average');
    } else if (avgTotal < 15000) {
      insights.push('⚠️ Moderate response times - consider optimization');
    } else {
      insights.push('🐌 Slow response times - optimization needed');
    }
    
    // Analyze network vs processing time
    const avgNetwork = metrics.reduce((sum, m) => sum + (m.networkRequestTime || 0), 0) / metrics.length;
    const avgBackend = metrics.reduce((sum, m) => sum + (m.backendProcessingTime || 0), 0) / metrics.length;
    
    if (avgNetwork > avgBackend * 0.1) {
      insights.push('🌐 Network latency is significant - consider backend location');
    }
    
    // Analyze consistency
    const totalTimes = metrics.map(m => m.totalFrontendTime);
    const maxTime = Math.max(...totalTimes);
    const minTime = Math.min(...totalTimes);
    const ratio = maxTime / minTime;
    
    if (ratio > 3) {
      insights.push('📊 High variance in response times - investigate inconsistencies');
    } else {
      insights.push('✅ Consistent performance across requests');
    }
    
    return insights;
  }
  
  /**
   * Clear old sessions to prevent memory leaks
   */
  cleanup(maxAge: number = 300000): void { // 5 minutes default
    const now = Date.now();
    for (const [sessionId, session] of this.sessions.entries()) {
      if (now - session.startTime > maxAge) {
        this.sessions.delete(sessionId);
      }
    }
  }
  
  /**
   * Export data as JSON
   */
  exportData(): string {
    return JSON.stringify(this.generateReport(), null, 2);
  }
}

// Global profiler instance
export const performanceProfiler = new FrontendPerformanceProfiler();

// Auto-cleanup every 5 minutes
setInterval(() => {
  performanceProfiler.cleanup();
}, 300000);