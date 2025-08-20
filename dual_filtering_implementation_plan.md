# Dual Filtering System Implementation Plan

## Overview
Implement both binary (current) and enhanced (graduated) filtering with frontend transparency controls, giving users granular control over source quality vs. completeness trade-offs.

## Architecture Summary

### Backend Changes

**1. Enhanced FinalizationAgent (`finalization_agent.py:114-147`)**
- Keep existing binary filtering as default/fallback mode
- Add new method `_classify_and_filter_sources_enhanced()` that uses `quality_validator.classify_and_filter_sources_graduated()`
- Route filtering based on new `enhanced_filtering` parameter
- Update response to include filtered sources and quality metrics

**2. API Response Enhancement (`state.py:138-145`)**
- `FinalizationOutput` already has required fields: `filtered_sources`, `quality_summary`, `filtering_applied`
- Ensure these fields are properly populated by enhanced filtering method

**3. Source Quality Integration**
- `Source` model already supports quality fields: `quality_score`, `quality_breakdown` 
- `quality_validator.py:539-614` already implements graduated filtering method
- Just need to connect these components

### Frontend Changes

**4. Enhanced Quality Controls (`InputForm.tsx:197-250`)**
- Add new "Enhanced Filtering" toggle/checkbox near existing quality selector
- When enabled, show additional controls:
  - Quality threshold slider (0.1-1.0)
  - "Show filtered sources" preference toggle
- Maintain existing 3-tier system as default

**5. Response Transparency Components**
- New `QualityIndicator` component showing filtering summary
- New `FilteredSourcesExpander` component with "Show X filtered sources" button
- Enhanced source display with individual quality scores
- Visual quality indicators (🟢🟡🔴) for each source

**6. API Integration**
- Pass `enhanced_filtering: boolean` parameter to backend
- Handle new response fields: `filtered_sources`, `quality_summary`, `filtering_applied`
- Display transparency information when filtering is applied

## Implementation Steps

### Phase 1: Backend Enhanced Filtering (1-2 days)
1. Update `FinalizationAgent._classify_and_filter_sources()` to support dual modes
2. Implement enhanced mode using existing `quality_validator.classify_and_filter_sources_graduated()`
3. Ensure `FinalizationOutput` populates all transparency fields
4. Add configuration for enhanced filtering enable/disable

### Phase 2: Frontend Controls (2-3 days)
1. Add "Enhanced Filtering" toggle to `InputForm.tsx`
2. Create quality threshold slider component (conditional display)
3. Update API calls to pass enhanced filtering parameters
4. Handle new response structure with filtered sources

### Phase 3: Transparency Components (2-3 days)
1. Build `QualityIndicator` component showing filtering summary
2. Create `FilteredSourcesExpander` with expand/collapse functionality
3. Add individual source quality score displays
4. Implement visual quality indicators system

### Phase 4: Integration & Testing (1-2 days)
1. End-to-end testing of dual filtering modes
2. Quality assurance for transparency features
3. Performance testing with enhanced filtering
4. User experience validation

## Technical Details

**Key Files to Modify:**
- `backend/src/agent/agents/finalization_agent.py` (add enhanced filtering mode)
- `frontend/src/components/InputForm.tsx` (add enhanced controls)
- New: `frontend/src/components/QualityIndicator.tsx`
- New: `frontend/src/components/FilteredSourcesExpander.tsx`

**API Changes:**
- Request: Add `enhanced_filtering: boolean` parameter
- Response: Populate `filtered_sources`, `quality_summary`, `filtering_applied` fields (already exist in schema)

**Backward Compatibility:**
- Default behavior remains unchanged (binary filtering)
- Enhanced filtering is opt-in via frontend toggle
- Existing quality selector continues working as before

## Benefits
- ✅ Preserves existing binary filtering for users who prefer simplicity
- ✅ Adds advanced transparency for power users
- ✅ Leverages existing quality infrastructure (`quality_validator.py`)
- ✅ Maintains backward compatibility
- ✅ Provides granular user control over quality vs. completeness trade-off

## Current State Analysis

### What Already Works
- **Binary filtering system**: `SourceClassifier` with high/medium/low credibility levels
- **Quality validation framework**: Comprehensive scoring in `quality_validator.py`
- **Graduated filtering method**: Already implemented in `quality_validator.classify_and_filter_sources_graduated()`
- **UI foundation**: Quality selector with descriptions and tooltips in `InputForm.tsx`
- **API schema**: `FinalizationOutput` supports transparency fields

### What Needs Implementation
- **Connection layer**: Link graduated filtering to `FinalizationAgent`
- **Frontend toggle**: Enhanced filtering option in UI
- **Transparency display**: Components to show filtered sources and quality metrics
- **API parameter**: Pass enhanced filtering preference to backend

## Risk Assessment

**Low Risk:**
- Existing infrastructure supports most requirements
- Additive changes preserve backward compatibility
- Quality algorithms are already tested

**Medium Risk:**
- UI complexity increase may confuse some users
- Performance impact of graduated filtering needs testing

**Mitigation:**
- Progressive disclosure (advanced features hidden by default)
- Feature flag for easy rollback
- Performance monitoring and optimization