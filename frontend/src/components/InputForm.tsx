import { useState } from "react";
import { Button } from "@/components/ui/button";
import { SquarePen, Brain, Send, StopCircle, Zap, Cpu, Shield, HelpCircle, Settings } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

// Updated InputFormProps
interface InputFormProps {
  onSubmit: (inputValue: string, effort: string, model: string, sourceQuality: string, enhancedFiltering?: boolean, qualityThreshold?: number) => void;
  onCancel: () => void;
  isLoading: boolean;
  hasHistory: boolean;
}

export const InputForm: React.FC<InputFormProps> = ({
  onSubmit,
  onCancel,
  isLoading,
  hasHistory,
}) => {
  const [internalInputValue, setInternalInputValue] = useState("");
  const [effort, setEffort] = useState("medium");
  const [model, setModel] = useState("gemini-2.5-flash");
  const [sourceQuality, setSourceQuality] = useState("any");
  const [enhancedFiltering, setEnhancedFiltering] = useState(false);
  const [qualityThreshold, setQualityThreshold] = useState(0.6);

  // Quality descriptions for user transparency
  const qualityDescriptions = {
    "any": {
      title: "Any Quality",
      description: "Include all sources (fastest, most comprehensive)",
      expectedSources: "8-15 sources",
      speed: "Fastest",
      icon: <Shield className="h-4 w-4 mr-2 text-gray-400" />
    },
    "medium": {
      title: "Medium+",
      description: "Filter low-credibility sources (balanced approach)",
      expectedSources: "5-10 sources",
      speed: "Balanced",
      icon: <Shield className="h-4 w-4 mr-2 text-blue-400" />
    },
    "high": {
      title: "High Only",
      description: "Only high-credibility sources (slowest, most reliable)",
      expectedSources: "2-6 sources",
      speed: "Slowest",
      icon: <Shield className="h-4 w-4 mr-2 text-green-400" />
    }
  };

  const handleInternalSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!internalInputValue.trim()) return;
    onSubmit(internalInputValue, effort, model, sourceQuality, enhancedFiltering, qualityThreshold);
    setInternalInputValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit with Ctrl+Enter (Windows/Linux) or Cmd+Enter (Mac)
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleInternalSubmit();
    }
  };

  const isSubmitDisabled = !internalInputValue.trim() || isLoading;

  return (
    <form
      onSubmit={handleInternalSubmit}
      className={`flex flex-col p-2 pb-3`}
    >
      <div
        className={`flex flex-row items-center justify-between text-white rounded-3xl rounded-bl-sm ${
          hasHistory ? "rounded-br-sm" : ""
        } break-words min-h-[80px] bg-neutral-700 px-4 pt-3 relative z-10`}
      >
        <Textarea
          value={internalInputValue}
          onChange={(e) => setInternalInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Who won the Euro 2024 and scored the most goals?"
          className={`w-full text-neutral-100 placeholder-neutral-500 resize-none border-0 focus:outline-none focus:ring-0 outline-none focus-visible:ring-0 shadow-none
                        md:text-base  min-h-[56px] max-h-[200px]`}
          rows={1}
        />
        <div className="-mt-3">
          {isLoading ? (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="text-red-500 hover:text-red-400 hover:bg-red-500/10 p-2 cursor-pointer rounded-full transition-all duration-200"
              onClick={onCancel}
            >
              <StopCircle className="h-5 w-5" />
            </Button>
          ) : (
            <Button
              type="submit"
              variant="ghost"
              className={`${
                isSubmitDisabled
                  ? "text-neutral-500"
                  : "text-blue-500 hover:text-blue-400 hover:bg-blue-500/10"
              } p-2 cursor-pointer rounded-full transition-all duration-200 text-base`}
              disabled={isSubmitDisabled}
            >
              Search
              <Send className="h-5 w-5" />
            </Button>
          )}
        </div>
      </div>
      <div className="flex flex-col gap-2 mt-3 relative z-0">
        <div className="flex flex-col gap-2 bg-neutral-800/50 p-2 rounded-lg border border-neutral-700/50 overflow-hidden">
          {/* Basic Controls Group */}
          <div className="flex flex-col gap-2">
            <div className="flex flex-row gap-2 bg-neutral-700 hover:bg-neutral-650 border-neutral-600 text-neutral-300 focus:ring-neutral-500 rounded-xl pl-2 min-w-fit transition-colors duration-200">
            <div className="flex flex-row items-center text-sm">
              <Brain className="h-4 w-4 mr-2" />
              Effort
            </div>
            <Select value={effort} onValueChange={setEffort}>
              <SelectTrigger className="w-[100px] bg-transparent border-none cursor-pointer">
                <SelectValue placeholder="Effort" />
              </SelectTrigger>
              <SelectContent className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer">
                <SelectItem
                  value="low"
                  className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                >
                  Low
                </SelectItem>
                <SelectItem
                  value="medium"
                  className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                >
                  Medium
                </SelectItem>
                <SelectItem
                  value="high"
                  className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                >
                  High
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-row gap-2 bg-neutral-700 hover:bg-neutral-650 border-neutral-600 text-neutral-300 focus:ring-neutral-500 rounded-xl pl-2 min-w-fit transition-colors duration-200">
            <div className="flex flex-row items-center text-sm ml-2">
              <Cpu className="h-4 w-4 mr-2" />
              Model
            </div>
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger className="w-[120px] bg-transparent border-none cursor-pointer">
                <SelectValue placeholder="Model" />
              </SelectTrigger>
              <SelectContent className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer">
                <SelectItem
                  value="gemini-2.0-flash"
                  className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                >
                  <div className="flex items-center">
                    <Zap className="h-4 w-4 mr-2 text-yellow-400" /> 2.0 Flash
                  </div>
                </SelectItem>
                <SelectItem
                  value="gemini-2.5-flash"
                  className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                >
                  <div className="flex items-center">
                    <Zap className="h-4 w-4 mr-2 text-orange-400" /> 2.5 Flash
                  </div>
                </SelectItem>
                <SelectItem
                  value="gemini-2.5-pro"
                  className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                >
                  <div className="flex items-center">
                    <Cpu className="h-4 w-4 mr-2 text-purple-400" /> 2.5 Pro
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <TooltipProvider>
            <div className="flex flex-row gap-2 bg-neutral-700 hover:bg-neutral-650 border-neutral-600 text-neutral-300 focus:ring-neutral-500 rounded-xl pl-2 min-w-fit transition-colors duration-200">
              <div className="flex flex-row items-center text-sm ml-2">
                <Shield className="h-4 w-4 mr-2" />
                Quality
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="h-3 w-3 ml-1 text-neutral-500 hover:text-neutral-300" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <div className="space-y-2">
                      <div className="font-semibold">Source Quality Filtering</div>
                      <div className="text-xs space-y-1">
                        <div><strong>Any:</strong> All sources included</div>
                        <div><strong>Medium+:</strong> Filters low-quality sources</div>
                        <div><strong>High:</strong> Only authoritative sources</div>
                      </div>
                    </div>
                  </TooltipContent>
                </Tooltip>
              </div>
              <Select value={sourceQuality} onValueChange={setSourceQuality}>
                <SelectTrigger className="w-[110px] bg-transparent border-none cursor-pointer">
                  <SelectValue placeholder="Quality" />
                </SelectTrigger>
                <SelectContent className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer">
                  {Object.entries(qualityDescriptions).map(([key, desc]) => (
                    <Tooltip key={key}>
                      <TooltipTrigger asChild>
                        <SelectItem
                          value={key}
                          className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                        >
                          <div className="flex items-center">
                            {desc.icon} {desc.title}
                          </div>
                        </SelectItem>
                      </TooltipTrigger>
                      <TooltipContent side="right" className="max-w-sm">
                        <div className="space-y-1">
                          <div className="font-semibold">{desc.title}</div>
                          <div className="text-xs text-neutral-300">{desc.description}</div>
                          <div className="text-xs text-neutral-400 space-y-0.5">
                            <div>Expected: {desc.expectedSources}</div>
                            <div>Speed: {desc.speed}</div>
                          </div>
                        </div>
                      </TooltipContent>
                    </Tooltip>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </TooltipProvider>
          </div>
          
          {/* Advanced Controls Group */}
          <div className="flex flex-col gap-2">
          {/* Enhanced Filtering Toggle */}
          <TooltipProvider>
            <div className="flex flex-row items-center gap-2 bg-neutral-700 hover:bg-neutral-650 border-neutral-600 text-neutral-300 focus:ring-neutral-500 rounded-xl pl-2 pr-2 py-1 min-w-fit max-w-xs transition-colors duration-200">
              <div className="flex items-center text-sm">
                <Settings className="h-4 w-4 mr-2" />
                <span>Enhanced Filtering</span>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="h-3 w-3 ml-1 text-neutral-500 hover:text-neutral-300" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <div className="space-y-2">
                      <div className="font-semibold">Enhanced Filtering</div>
                      <div className="text-xs">
                        Provides detailed quality scores for sources and shows which sources were filtered out for transparency
                      </div>
                    </div>
                  </TooltipContent>
                </Tooltip>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setEnhancedFiltering(!enhancedFiltering)}
                className={`ml-auto min-w-[44px] min-h-[36px] ${enhancedFiltering 
                  ? 'bg-blue-600 border-blue-500 text-white hover:bg-blue-700' 
                  : 'bg-transparent border-neutral-600 text-neutral-300 hover:bg-neutral-600'
                }`}
              >
                {enhancedFiltering ? 'ON' : 'OFF'}
              </Button>
            </div>
          </TooltipProvider>

          {/* Quality Threshold Slider - Only shown when enhanced filtering is enabled */}
          {enhancedFiltering && (
            <TooltipProvider>
              <div className="flex flex-row items-center gap-2 bg-neutral-700 hover:bg-neutral-650 border-neutral-600 text-neutral-300 focus:ring-neutral-500 rounded-xl pl-2 pr-2 py-1 min-w-fit transition-colors duration-200">
                <div className="flex items-center text-sm min-w-0">
                  <Shield className="h-4 w-4 mr-2 flex-shrink-0" />
                  <span>Quality Threshold: {qualityThreshold.toFixed(1)}</span>
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="h-3 w-3 ml-1 text-neutral-500 hover:text-neutral-300" />
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs">
                      <div className="space-y-2">
                        <div className="font-semibold">Quality Threshold</div>
                        <div className="text-xs">
                          Sources with quality scores below this threshold will be filtered out but still shown for transparency
                        </div>
                      </div>
                    </TooltipContent>
                  </Tooltip>
                </div>
                <div className="flex-1 ml-2 mr-2">
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    value={qualityThreshold}
                    onChange={(e) => setQualityThreshold(parseFloat(e.target.value))}
                    className="w-full h-2 bg-neutral-600 rounded-lg appearance-none cursor-pointer slider"
                  />
                </div>
              </div>
            </TooltipProvider>
          )}
          </div>
        </div>
        {hasHistory && (
          <div className="flex justify-center mt-2">
            <Button
              className="bg-neutral-700 hover:bg-neutral-650 border-neutral-600 text-neutral-300 cursor-pointer rounded-xl px-3 py-1 text-sm transition-colors duration-200"
              variant="default"
              onClick={() => window.location.reload()}
            >
              <SquarePen size={14} />
              New Search
            </Button>
          </div>
        )}
      </div>
    </form>
  );
};
