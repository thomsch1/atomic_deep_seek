###Plan a new feature for app

##Backend
All found should be classified with the following finding
bias_assessment_data = {
    'Source Type': [
        'Academic Peer-Reviewed',
        'Academic Peer-Reviewed', 
        'Academic Peer-Reviewed',
        'Commercial Software Vendor',
        'Commercial Consulting',
        'Academic Independent',
        'Academic Independent',
        'Academic Independent'
    ],
    'Publication/Entity': [
        'University Research',
        'IEEE/Taylor&Francis Journals',
        'International Forecasting Conferences',
        'SAP Community Blog',
        'Commercial Whitepapers',
        'arXiv Preprints',
        'University Theses',
        'Independent Research Labs'
    ],
    'Key Finding': [
        'TSB and zero-inflated methods consistently outperform Croston',
        'Machine learning hybrids show 6-35% improvements over traditional methods',
        'SPEC metric reveals traditional metrics favor zero forecasts inappropriately',
        'Emphasis on proprietary solutions without independent validation',
        'Claims of superior performance without academic peer review',
        'Rigorous mathematical analysis of bias in traditional methods',
        'Independent validation of method performance on real industrial data',
        'Development of new evaluation metrics (SPEC) addressing business needs'
    ],
    'Bias Risk Level': [
        'Very Low',
        'Very Low',
        'Very Low', 
        'High',
        'Very High',
        'Low',
        'Low',
        'Low'
    ],
    'Publication Date Range': [
        '2020-2025',
        '2020-2025',
        '2015-2025',
        '2020-2025',
        '2018-2025',
        '2020-2025',
        '2020-2025',
        '2020-2025'
    ],
    'Recommendation': [
        'Use as primary evidence',
        'Use as primary evidence',
        'Use as primary evidence',
        'Exclude - commercial bias',
        'Exclude - commercial bias',
        'Use with caution - not peer reviewed',
        'Use as supporting evidence',
        'Use as primary evidence'
    ]
}

The 'Publication Date Range' should be used to check the recentness of sources.
The'Recommendation' the minimum as source used level should be adjustable in the frontend.

## Front End
Right next to model should be added a component to choose the the minimum as source used level of 'Recommendation'