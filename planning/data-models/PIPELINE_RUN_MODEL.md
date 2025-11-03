# Pipeline Run Model - Master Data Model Specification

**Purpose**: Define the complete Pydantic data model for capturing ALL pipeline execution data.

---

## Overview

The `PipelineRun` model is the master container for a complete pipeline execution, capturing:
- Input parameters (`WorkflowInput`)
- All Phase 1-4 intermediary data
- Final outputs
- Execution metadata (timing, costs, errors)
- Audit trail

This allows us to:
1. **Debug**: Trace exactly what happened at each step
2. **Replay**: Re-run Phase 2-4 using cached Phase 1 data
3. **Analyze**: Query across all pipeline runs
4. **Optimize**: Track costs and performance
5. **Monitor**: Measure quality over time

---

## Model Hierarchy

```
PipelineRun (Master Model)
├── run_id, timestamp, status, execution_time
├── workflow_input: WorkflowInput
├── phase1_output: Phase1Output
│   ├── vendor_validation: DomainValidation
│   ├── prospect_validation: DomainValidation
│   ├── vendor_homepage: HomepageScrapedContent
│   ├── prospect_homepage: HomepageScrapedContent
│   ├── vendor_homepage_analysis: HomepageAnalysis
│   ├── prospect_homepage_analysis: HomepageAnalysis
│   ├── vendor_url_prioritization: URLPrioritization
│   ├── prospect_url_prioritization: URLPrioritization
│   ├── vendor_batch_content: BatchScrapedContent
│   └── prospect_batch_content: BatchScrapedContent
├── phase2_output: Phase2Output
│   └── vendor_elements: VendorElements (existing model)
├── phase3_output: Phase3Output
│   └── prospect_intelligence: ProspectIntelligence (existing model)
├── phase4_output: Phase4Output
│   └── sales_playbook: SalesPlaybook (existing model)
├── total_api_calls, total_tokens_used, estimated_cost_usd
└── errors: List[Dict], warnings: List[Dict]
```

---

## Complete Model Definitions

### Phase 1 Intermediary Models (NEW)

These models capture the rich intermediary data from Phase 1 that is currently lost:

#### 1. DomainValidation
**Captures**: Step 1 - Domain validation and URL discovery results

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DomainValidation(BaseModel):
    """Results from Step 1: Domain validation and URL discovery"""

    domain: str = Field(
        description="Validated domain (https://example.com)"
    )

    urls_discovered: List[str] = Field(
        description="All URLs discovered via map_website()",
        default_factory=list
    )

    url_count: int = Field(
        description="Total number of URLs discovered"
    )

    map_timestamp: datetime = Field(
        description="When the domain mapping occurred"
    )

    validation_status: str = Field(
        description="Status: 'success', 'partial', 'failed'"
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Error details if validation failed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "domain": "https://octavehq.com",
                "urls_discovered": [
                    "https://octavehq.com/about",
                    "https://octavehq.com/platform",
                    "https://octavehq.com/customers",
                    # ... 91 more URLs
                ],
                "url_count": 94,
                "map_timestamp": "2025-11-02T20:30:15",
                "validation_status": "success",
                "error_message": None
            }
        }
```

#### 2. HomepageScrapedContent
**Captures**: Step 2 - Raw homepage content and metadata

```python
class HomepageScrapedContent(BaseModel):
    """Results from Step 2: Homepage scraping"""

    url: str = Field(
        description="Homepage URL that was scraped"
    )

    markdown_content: str = Field(
        description="Complete homepage content in markdown format"
    )

    char_count: int = Field(
        description="Total character count of content"
    )

    word_count: int = Field(
        description="Approximate word count"
    )

    scrape_timestamp: datetime = Field(
        description="When the scraping occurred"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Firecrawl metadata (title, description, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://octavehq.com",
                "markdown_content": "# Octave - GTM Context Engine\n\n...",
                "char_count": 12450,
                "word_count": 2100,
                "scrape_timestamp": "2025-11-02T20:30:25",
                "metadata": {
                    "title": "Octave - GTM Context Engine",
                    "description": "AI-powered sales intelligence",
                    "has_cta": True
                }
            }
        }
```

#### 3. HomepageAnalysis
**Captures**: Step 3 - AI analysis of homepage content

```python
class HomepageAnalysis(BaseModel):
    """Results from Step 3: AI homepage analysis"""

    company_basics: Dict[str, str] = Field(
        description="Company name, tagline, primary offering",
        default_factory=dict
    )

    key_offerings: List[str] = Field(
        description="Main products/services identified",
        default_factory=list
    )

    ctas: List[str] = Field(
        description="Call-to-actions found on homepage",
        default_factory=list
    )

    analysis_timestamp: datetime = Field(
        description="When AI analysis was performed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "company_basics": {
                    "name": "Octave",
                    "tagline": "GTM Context Engine",
                    "primary_offering": "AI-powered sales intelligence"
                },
                "key_offerings": [
                    "Automated playbook generation",
                    "ICP refinement",
                    "Messaging personalization"
                ],
                "ctas": [
                    "Book a demo",
                    "Try for free"
                ],
                "analysis_timestamp": "2025-11-02T20:30:45"
            }
        }
```

#### 4. PrioritizedURL
**Captures**: Step 4 - Single URL with prioritization reasoning

```python
class PrioritizedURL(BaseModel):
    """Single prioritized URL with reasoning"""

    url: str = Field(
        description="The prioritized URL"
    )

    priority_score: float = Field(
        description="Priority score (0.0-10.0)",
        ge=0.0,
        le=10.0
    )

    reasoning: str = Field(
        description="Why this URL was prioritized"
    )

    category: str = Field(
        description="URL category: about, case_study, pricing, blog, etc."
    )
```

#### 5. URLPrioritization
**Captures**: Step 4 - Complete URL prioritization results

```python
class URLPrioritization(BaseModel):
    """Results from Step 4: URL prioritization"""

    prioritized_urls: List[PrioritizedURL] = Field(
        description="Top 10-15 URLs selected for scraping",
        default_factory=list
    )

    total_urls_evaluated: int = Field(
        description="Total URLs considered (from Step 1)"
    )

    urls_selected: int = Field(
        description="Number of URLs selected for scraping"
    )

    prioritization_timestamp: datetime = Field(
        description="When prioritization occurred"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prioritized_urls": [
                    {
                        "url": "https://octavehq.com/about",
                        "priority_score": 9.5,
                        "reasoning": "Core company information",
                        "category": "about"
                    },
                    {
                        "url": "https://octavehq.com/customers",
                        "priority_score": 9.0,
                        "reasoning": "Customer proof points",
                        "category": "customers"
                    }
                    # ... 10-13 more URLs
                ],
                "total_urls_evaluated": 94,
                "urls_selected": 14,
                "prioritization_timestamp": "2025-11-02T20:31:10"
            }
        }
```

#### 6. BatchScrapedContent
**Captures**: Step 5 - Batch scraping results

```python
class BatchScrapedContent(BaseModel):
    """Results from Step 5: Batch scraping"""

    scraped_pages: Dict[str, str] = Field(
        description="Map of URL -> markdown content",
        default_factory=dict
    )

    page_count: int = Field(
        description="Number of pages successfully scraped"
    )

    total_chars: int = Field(
        description="Total characters across all pages"
    )

    total_words: int = Field(
        description="Estimated total word count"
    )

    scrape_timestamp: datetime = Field(
        description="When batch scraping completed"
    )

    failed_urls: List[str] = Field(
        default_factory=list,
        description="URLs that failed to scrape"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scraped_pages": {
                    "https://octavehq.com/about": "# About Octave...",
                    "https://octavehq.com/platform": "# Platform...",
                    # ... 12 more pages
                },
                "page_count": 14,
                "total_chars": 85000,
                "total_words": 14200,
                "scrape_timestamp": "2025-11-02T20:32:45",
                "failed_urls": []
            }
        }
```

---

### Phase-Level Container Models

#### Phase1Output
**Contains**: All 10 Phase 1 data points (5 steps × 2 companies)

```python
class Phase1Output(BaseModel):
    """Complete Phase 1 intelligence gathering output"""

    # Step 1: Domain validation (parallel)
    vendor_validation: DomainValidation
    prospect_validation: DomainValidation

    # Step 2: Homepage scraping (parallel)
    vendor_homepage: HomepageScrapedContent
    prospect_homepage: HomepageScrapedContent

    # Step 3: Homepage analysis (parallel)
    vendor_homepage_analysis: HomepageAnalysis
    prospect_homepage_analysis: HomepageAnalysis

    # Step 4: URL prioritization
    vendor_url_prioritization: URLPrioritization
    prospect_url_prioritization: URLPrioritization

    # Step 5: Batch scraping
    vendor_batch_content: BatchScrapedContent
    prospect_batch_content: BatchScrapedContent
```

#### Phase2Output
**Contains**: Vendor extraction results (existing `VendorElements` model)

```python
from models.vendor_elements import VendorElements

class Phase2Output(BaseModel):
    """Phase 2 vendor extraction output (uses existing model)"""

    vendor_elements: VendorElements = Field(
        description="8 types of vendor GTM elements"
    )

    extraction_timestamp: datetime = Field(
        description="When extraction completed"
    )

    specialist_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Individual specialist outputs (for debugging)"
    )
```

#### Phase3Output
**Contains**: Prospect analysis results (existing `ProspectIntelligence` model)

```python
from models.prospect_intelligence import ProspectIntelligence

class Phase3Output(BaseModel):
    """Phase 3 prospect analysis output (uses existing model)"""

    prospect_intelligence: ProspectIntelligence = Field(
        description="Company profile, pain points, buyer personas"
    )

    analysis_timestamp: datetime = Field(
        description="When analysis completed"
    )

    analyst_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Individual analyst outputs (for debugging)"
    )
```

#### Phase4Output
**Contains**: Sales playbook (existing `SalesPlaybook` model)

```python
from models.playbook import SalesPlaybook

class Phase4Output(BaseModel):
    """Phase 4 playbook generation output (uses existing model)"""

    sales_playbook: SalesPlaybook = Field(
        description="Complete sales playbook"
    )

    generation_timestamp: datetime = Field(
        description="When playbook generation completed"
    )

    specialist_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Individual playbook specialist outputs (for debugging)"
    )
```

---

### Master PipelineRun Model

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from models.workflow_input import WorkflowInput

class PipelineRun(BaseModel):
    """
    Complete pipeline run capturing ALL data from all 4 phases.

    This is the master data model for persisting complete pipeline execution:
    - Input parameters
    - All intermediary processing results
    - Final output
    - Execution metadata (timing, status, errors)

    Use this model to:
    1. Debug pipeline failures
    2. Replay Phase 2-4 without re-scraping
    3. Query analytics across all runs
    4. Track costs and performance
    5. Monitor quality over time
    """

    # ========================================================================
    # METADATA
    # ========================================================================

    run_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique run identifier (UUID)"
    )

    run_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the pipeline run started"
    )

    status: str = Field(
        default="running",
        description="Pipeline status: running, completed, failed, partial"
    )

    execution_time_seconds: Optional[float] = Field(
        default=None,
        description="Total execution time in seconds"
    )

    # ========================================================================
    # INPUT
    # ========================================================================

    workflow_input: WorkflowInput = Field(
        description="Input domains (vendor and prospect)"
    )

    # ========================================================================
    # PHASE OUTPUTS
    # ========================================================================

    phase1_output: Optional[Phase1Output] = Field(
        default=None,
        description="Phase 1: Intelligence gathering (Steps 1-5)"
    )

    phase2_output: Optional[Phase2Output] = Field(
        default=None,
        description="Phase 2: Vendor extraction (Step 6, 8 specialists)"
    )

    phase3_output: Optional[Phase3Output] = Field(
        default=None,
        description="Phase 3: Prospect analysis (Step 7, 3 analysts)"
    )

    phase4_output: Optional[Phase4Output] = Field(
        default=None,
        description="Phase 4: Playbook generation (Step 8, 4 specialists)"
    )

    # ========================================================================
    # COST & PERFORMANCE METRICS
    # ========================================================================

    total_api_calls: int = Field(
        default=0,
        description="Total API calls made (Firecrawl + OpenAI)"
    )

    total_tokens_used: int = Field(
        default=0,
        description="Total tokens consumed (OpenAI)"
    )

    estimated_cost_usd: Optional[float] = Field(
        default=None,
        description="Estimated total cost in USD"
    )

    # ========================================================================
    # ERROR TRACKING
    # ========================================================================

    errors: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of errors encountered (phase, step, message)"
    )

    warnings: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of warnings (non-fatal issues)"
    )

    # ========================================================================
    # AUDIT TRAIL
    # ========================================================================

    created_by: Optional[str] = Field(
        default=None,
        description="User who initiated the run (email/username)"
    )

    created_via: str = Field(
        default="CLI",
        description="How the run was initiated: CLI or API"
    )

    tags: List[str] = Field(
        default_factory=list,
        description="Custom tags for categorization"
    )

    notes: Optional[str] = Field(
        default=None,
        description="Free-form notes about this run"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "550e8400-e29b-41d4-a716-446655440000",
                "run_timestamp": "2025-11-02T20:30:00",
                "status": "completed",
                "execution_time_seconds": 185.3,
                "workflow_input": {
                    "vendor_domain": "https://octavehq.com",
                    "prospect_domain": "https://sendoso.com"
                },
                "phase1_output": {
                    # ... (complete Phase1Output)
                },
                "phase2_output": {
                    # ... (complete Phase2Output)
                },
                "phase3_output": {
                    # ... (complete Phase3Output)
                },
                "phase4_output": {
                    # ... (complete Phase4Output)
                },
                "total_api_calls": 47,
                "total_tokens_used": 125000,
                "estimated_cost_usd": 0.28,
                "errors": [],
                "warnings": [
                    {
                        "phase": "phase1",
                        "step": "batch_scrape",
                        "message": "1 URL failed to scrape (timeout)"
                    }
                ],
                "created_by": "brandon@orchid.com",
                "created_via": "API",
                "tags": ["b2b-saas", "test-run"],
                "notes": "Testing new prompt for email sequences"
            }
        }
```

---

## Field Naming Conventions

### Timestamps
- All timestamps use `datetime` type
- Naming: `{action}_timestamp` (e.g., `scrape_timestamp`, `analysis_timestamp`)
- Use UTC timezone

### Status Fields
- Use string enums for status
- Common values: `"success"`, `"failed"`, `"partial"`, `"running"`, `"completed"`

### Counts & Metrics
- Use descriptive names: `url_count`, `page_count`, `char_count`, `word_count`
- Always use integers for counts, floats for scores/metrics

### Collections
- Lists: `prioritized_urls`, `scraped_pages`, `errors`, `warnings`
- Dicts: `metadata`, `scraped_pages` (when mapping URL -> content)

---

## Next Steps

1. **Review** [PHASE_MODELS_DETAILED.md](./PHASE_MODELS_DETAILED.md) for phase-by-phase breakdown
2. **Choose storage** [STORAGE_STRATEGIES.md](./STORAGE_STRATEGIES.md) for persistence strategy
3. **Plan implementation** [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) for build plan
4. **See code** [CODE_EXAMPLES.md](./CODE_EXAMPLES.md) for implementation examples

---

**Total Models**: 13 new + 3 existing = **16 models**
**Total Fields**: ~120 fields across all models
**JSON Size**: ~500KB per complete pipeline run (estimated)
