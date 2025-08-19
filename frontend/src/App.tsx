import { useState, useEffect, useRef, useCallback } from "react";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";
import { Button } from "@/components/ui/button";
import { AtomicAgentAPI, Message, ResearchResponse } from "@/services/api";

export default function App() {
  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<
    ProcessedEvent[]
  >([]);
  const [historicalActivities, setHistoricalActivities] = useState<
    Record<string, ProcessedEvent[]>
  >({});
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const hasFinalizeEventOccurredRef = useRef(false);
  const [error, setError] = useState<string | null>(null);
  
  // New state management for REST API
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const api = new AtomicAgentAPI();

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [messages]);

  useEffect(() => {
    if (
      hasFinalizeEventOccurredRef.current &&
      !isLoading &&
      messages.length > 0
    ) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.type === "ai" && lastMessage.id) {
        setHistoricalActivities((prev) => ({
          ...prev,
          [lastMessage.id!]: [...processedEventsTimeline],
        }));
      }
      hasFinalizeEventOccurredRef.current = false;
    }
  }, [messages, isLoading, processedEventsTimeline]);

  // Helper function to map effort levels to research parameters
  const mapEffortToParams = (effort: string) => {
    switch (effort) {
      case "low":
        return { 
          initial_search_query_count: 1, 
          max_research_loops: 1
        };
      case "medium":
        return { 
          initial_search_query_count: 3, 
          max_research_loops: 3
        };
      case "high":
        return { 
          initial_search_query_count: 5, 
          max_research_loops: 10
        };
      default:
        return { 
          initial_search_query_count: 3, 
          max_research_loops: 2
        };
    }
  };

  // Convert response to activity events
  const convertResponseToEvents = (response: ResearchResponse): ProcessedEvent[] => {
    const events: ProcessedEvent[] = [];
    
    // Generate query event
    events.push({
      title: "Generating Search Queries",
      data: `Generated ${response.total_queries} search queries`
    });
    
    // Web research event
    events.push({
      title: "Web Research",
      data: `Gathered ${response.sources.length} sources`
    });
    
    // Research loops
    if (response.research_loops_executed > 1) {
      events.push({
        title: "Reflection", 
        data: `Completed ${response.research_loops_executed} research loops`
      });
    }
    
    // Finalization
    events.push({
      title: "Finalizing Answer",
      data: "Composing and presenting the final answer"
    });
    
    return events;
  };

  const handleSubmit = useCallback(
    async (submittedInputValue: string, effort: string, model: string, sourceQuality: string) => {
      if (!submittedInputValue.trim()) return;
      
      setIsLoading(true);
      setProcessedEventsTimeline([]);
      setError(null);
      hasFinalizeEventOccurredRef.current = false;
      
      // Add human message
      const humanMessage: Message = {
        type: "human",
        content: submittedInputValue,
        id: Date.now().toString()
      };
      const newMessages = [...messages, humanMessage];
      setMessages(newMessages);
      
      try {
        // Convert effort to parameters (excluding source quality filter)
        const { initial_search_query_count, max_research_loops } = mapEffortToParams(effort);
        
        // Use explicit source quality selection, with fallback to effort-based mapping
        const effectiveSourceQuality = sourceQuality === "any" ? undefined : sourceQuality;
        
        // Call backend
        const response = await api.conductResearch({
          question: submittedInputValue,
          initial_search_query_count,
          max_research_loops,
          reasoning_model: model,
          source_quality_filter: effectiveSourceQuality
        });
        
        // Create AI response message
        const aiMessage: Message = {
          type: "ai",
          content: response.final_answer,
          id: (Date.now() + 1).toString()
        };
        
        // Add AI response
        const finalMessages = [...newMessages, aiMessage];
        setMessages(finalMessages);
        
        // Convert response to activity events
        const events = convertResponseToEvents(response);
        setProcessedEventsTimeline(events);
        
        // Store historical activities for this message
        setHistoricalActivities(prev => ({
          ...prev,
          [aiMessage.id]: events
        }));

        hasFinalizeEventOccurredRef.current = true;
        
      } catch (error: any) {
        setError(error?.message || 'An error occurred during research');
      } finally {
        setIsLoading(false);
      }
    },
    [api, messages]
  );

  const handleCancel = useCallback(() => {
    setIsLoading(false);
    setProcessedEventsTimeline([]);
    setError(null);
    // Note: With REST API, we can't cancel in-flight requests easily
    // But we can reset the UI state
  }, []);

  return (
    <div className="flex h-screen bg-neutral-800 text-neutral-100 font-sans antialiased">
      <main className="h-full w-full max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <WelcomeScreen
              handleSubmit={handleSubmit}
              isLoading={isLoading}
              onCancel={handleCancel}
            />
          ) : error ? (
            <div className="flex flex-col items-center justify-center h-full">
              <div className="flex flex-col items-center justify-center gap-4">
                <h1 className="text-2xl text-red-400 font-bold">Error</h1>
                <p className="text-red-400">{error}</p>

                <Button
                  variant="destructive"
                  onClick={() => {
                    setError(null);
                    setMessages([]);
                  }}
                >
                  Retry
                </Button>
              </div>
            </div>
          ) : (
            <ChatMessagesView
              messages={messages}
              isLoading={isLoading}
              scrollAreaRef={scrollAreaRef}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              liveActivityEvents={processedEventsTimeline}
              historicalActivities={historicalActivities}
            />
          )}
      </main>
    </div>
  );
}
