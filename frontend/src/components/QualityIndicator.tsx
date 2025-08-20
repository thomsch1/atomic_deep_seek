import React, { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Shield, Eye, EyeOff, ChevronDown, ChevronUp, Info } from 'lucide-react';
import {
  Collapsible,
  CollapsibleContent,
} from '@/components/ui/collapsible';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface QualityMetrics {
  source_credibility: number;
  content_relevance: number;
  information_completeness: number;
  recency_score: number;
  overall_score: number;
}

interface Source {
  title: string;
  url: string;
  quality_score?: number;
  quality_breakdown?: QualityMetrics;
}

interface QualitySummary {
  total_sources: number;
  included_sources: number;
  filtered_sources: number;
  average_quality_score: number;
  quality_threshold: number;
}

interface QualityIndicatorProps {
  usedSources: Source[];
  filteredSources?: Source[];
  qualitySummary?: QualitySummary;
  filteringApplied?: boolean;
}

export const QualityIndicator: React.FC<QualityIndicatorProps> = ({
  usedSources,
  filteredSources = [],
  qualitySummary,
  filteringApplied = false,
}) => {
  const [showFilteredSources, setShowFilteredSources] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const getQualityIcon = (score: number): React.ReactNode => {
    if (score >= 0.8) return <Shield className="h-3 w-3 text-green-400" />;
    if (score >= 0.6) return <Shield className="h-3 w-3 text-blue-400" />;
    if (score >= 0.4) return <Shield className="h-3 w-3 text-yellow-400" />;
    return <Shield className="h-3 w-3 text-red-400" />;
  };

  const formatScore = (score: number): string => {
    return Math.round(score * 100).toString();
  };

  if (!filteringApplied && (!qualitySummary || qualitySummary.total_sources === 0)) {
    return null;
  }

  return (
    <TooltipProvider>
      <div className="mt-4 p-3 bg-neutral-800 rounded-lg border border-neutral-700">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Info className="h-4 w-4 text-neutral-400" />
            <span className="text-sm font-medium text-neutral-200">
              Source Quality Summary
            </span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-neutral-400 hover:text-neutral-200"
          >
            {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>

        <div className="flex items-center gap-4 text-xs text-neutral-300">
          <div>
            Showing <strong>{qualitySummary?.included_sources || usedSources.length}</strong> of{' '}
            <strong>{qualitySummary?.total_sources || usedSources.length}</strong> sources
          </div>
          {filteringApplied && filteredSources.length > 0 && (
            <div>
              (<strong>{filteredSources.length}</strong> filtered by quality settings)
            </div>
          )}
          {qualitySummary?.average_quality_score && (
            <div className="flex items-center gap-1">
              {getQualityIcon(qualitySummary.average_quality_score)}
              <span>Avg: {formatScore(qualitySummary.average_quality_score)}%</span>
            </div>
          )}
        </div>

        {filteredSources.length > 0 && (
          <div className="mt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFilteredSources(!showFilteredSources)}
              className="text-neutral-400 hover:text-neutral-200 text-xs"
            >
              {showFilteredSources ? (
                <>
                  <EyeOff className="h-3 w-3 mr-1" />
                  Hide filtered sources
                </>
              ) : (
                <>
                  <Eye className="h-3 w-3 mr-1" />
                  Show {filteredSources.length} filtered sources
                </>
              )}
            </Button>
          </div>
        )}

        <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
          <CollapsibleContent className="space-y-2 mt-3">
            {/* Used Sources */}
            {usedSources.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-neutral-300 mb-2 flex items-center gap-1">
                  <Shield className="h-3 w-3 text-green-400" />
                  Included Sources ({usedSources.length})
                </h4>
                <div className="space-y-1">
                  {usedSources.map((source, index) => (
                    <SourceItem key={index} source={source} isFiltered={false} />
                  ))}
                </div>
              </div>
            )}

            {/* Filtered Sources (if shown) */}
            {showFilteredSources && filteredSources.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-neutral-400 mb-2 flex items-center gap-1">
                  <Shield className="h-3 w-3 text-red-400" />
                  Filtered Sources ({filteredSources.length})
                </h4>
                <div className="space-y-1">
                  {filteredSources.map((source, index) => (
                    <SourceItem key={index} source={source} isFiltered={true} />
                  ))}
                </div>
              </div>
            )}
          </CollapsibleContent>
        </Collapsible>
      </div>
    </TooltipProvider>
  );
};

interface SourceItemProps {
  source: Source;
  isFiltered: boolean;
}

const SourceItem: React.FC<SourceItemProps> = ({ source, isFiltered }) => {
  const getQualityColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.6) return 'text-blue-400';
    if (score >= 0.4) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getQualityIcon = (score: number): React.ReactNode => {
    if (score >= 0.8) return <Shield className="h-3 w-3 text-green-400" />;
    if (score >= 0.6) return <Shield className="h-3 w-3 text-blue-400" />;
    if (score >= 0.4) return <Shield className="h-3 w-3 text-yellow-400" />;
    return <Shield className="h-3 w-3 text-red-400" />;
  };

  const formatScore = (score: number): string => {
    return Math.round(score * 100).toString();
  };

  return (
    <div className={`flex items-center gap-2 p-2 rounded text-xs ${
      isFiltered ? 'bg-neutral-900 border border-neutral-700' : 'bg-neutral-800'
    }`}>
      <div className="flex items-center gap-1 min-w-0 flex-1">
        {source.quality_score !== undefined && getQualityIcon(source.quality_score)}
        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-400 hover:text-blue-300 truncate flex-1"
          title={source.title}
        >
          {source.title}
        </a>
      </div>
      
      {source.quality_score !== undefined && (
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs">
            <span className={getQualityColor(source.quality_score)}>
              {formatScore(source.quality_score)}%
            </span>
          </Badge>
          
          {source.quality_breakdown && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Info className="h-3 w-3 text-neutral-500 hover:text-neutral-300" />
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                  <div className="space-y-1">
                    <div className="font-semibold">Quality Breakdown</div>
                    <div className="text-xs space-y-0.5">
                      <div>Credibility: {formatScore(source.quality_breakdown.source_credibility)}%</div>
                      <div>Relevance: {formatScore(source.quality_breakdown.content_relevance)}%</div>
                      <div>Completeness: {formatScore(source.quality_breakdown.information_completeness)}%</div>
                      <div>Recency: {formatScore(source.quality_breakdown.recency_score)}%</div>
                    </div>
                  </div>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
      )}
    </div>
  );
};