# Revised Source Bias Assessment Feature - Practical MVP Approach

## Core Philosophy
Start with a simple, performant solution that delivers immediate user value, then iterate to add sophistication.

## Phase 1: MVP Implementation (Recommended First Step)

### Backend Changes

#### 1. Minimal Source Model Extension (`backend/src/agent/state.py`)
Add only essential fields to avoid complexity:
```python
class Source(BaseModel):
    # Existing fields...
    source_credibility: Optional[str] = None  # "high", "medium", "low"
    domain_type: Optional[str] = None  # "academic", "commercial", "news", "other"
```

#### 2. Simple Classification Service
Create `backend/src/agent/source_classifier.py`:
- Domain-based classification using simple rules (.edu = academic, major news domains = news)
- Lightweight credibility scoring based on domain reputation
- Easily extensible for future enhancements
- Cached results for performance

#### 3. Integration in FinalizationAgent (`backend/src/agent/agents/finalization_agent.py`)
- Classify sources after research is complete (no performance impact on search)
- Filter sources based on minimum credibility level if specified
- Maintain backward compatibility when no filtering is requested

#### 4. Optional API Parameter (`backend/src/agent/app.py`)
- Add `source_quality_filter: Optional[str] = None` to ResearchRequest
- Values: "high", "medium", "low", None (no filtering)
- Only filter when explicitly requested

### Frontend Changes

#### 1. Conservative UI Approach (`frontend/src/components/InputForm.tsx`)
Instead of adding a third dropdown, integrate into existing "Effort" system:
- High effort → automatically applies "high" source quality filter
- Medium effort → applies "medium" filter  
- Low effort → no filtering
- This leverages existing UI without adding complexity

#### 2. API Integration (`frontend/src/services/api.ts`)
- Map effort levels to source quality filters behind the scenes
- Extend Source interface minimally for new fields

#### 3. Optional Enhancement: Source Quality Indicators
- Add subtle badge/indicator showing source credibility in results
- Use existing UI patterns for consistency

## Phase 2: Future Enhancements (After MVP)

### Advanced Classification
- Implement the full bias assessment data structure from the plan
- Add ML-based content analysis
- Publisher reputation database

### Enhanced UI
- Add dedicated "Advanced Options" panel
- Granular source type filtering
- Source bias explanation tooltips

### Configuration
- User preference storage
- Admin-configurable classification rules

## Key Advantages of This Approach

1. **Performance**: No impact on search speed (classification happens post-research)
2. **Simplicity**: Leverages existing UI patterns, minimal new complexity
3. **Compatibility**: Existing functionality unchanged, fully backward compatible
4. **Iterative**: Easy to enhance sophistication over time
5. **User Value**: Immediate benefit without overwhelming users with options

## Implementation Order

1. Create source classifier service with domain-based rules
2. Integrate classification in finalization agent
3. Add optional API parameter
4. Modify frontend to map effort → source quality
5. Add source credibility indicators to results
6. Test with different effort levels
7. Monitor performance and user feedback

## Risk Mitigation

- **Fallback**: If classification fails, continue without filtering
- **Performance**: Classification only runs once per research session
- **User Experience**: Changes are subtle and optional
- **Maintainability**: Simple rule-based system easy to debug and extend

This approach delivers the core value of source quality filtering while maintaining system performance and user experience simplicity.

## Original Complex Plan Reference

The original plan from `plan_source_check.md` contains the full bias assessment data structure:

```python
bias_assessment_data = {
    'Source Type': [
        'Academic Peer-Reviewed',
        'Commercial Software Vendor',
        'Commercial Consulting',
        'Academic Independent',
        # etc.
    ],
    'Bias Risk Level': [
        'Very Low',
        'Low', 
        'High',
        'Very High'
    ],
    'Recommendation': [
        'Use as primary evidence',
        'Use as supporting evidence',
        'Use with caution - not peer reviewed',
        'Exclude - commercial bias'
    ]
}
```

This sophisticated classification system should be implemented in Phase 2 after the MVP proves successful and user adoption is confirmed.