# Phase Models - Detailed Breakdown

**Purpose**: Deep dive into each phase's data structures and data flow transformations.

---

## Data Flow Overview

```
Input: WorkflowInput {vendor_domain, prospect_domain}
  ↓
Phase 1: Raw Intelligence Gathering
  Step 1 → DomainValidation (2x: vendor + prospect)
  Step 2 → HomepageScrapedContent (2x)
  Step 3 → HomepageAnalysis (2x)
  Step 4 → URLPrioritization (2x)
  Step 5 → BatchScrapedContent (2x)
  ↓
Phase 2: Vendor GTM Element Extraction
  8 parallel specialists → VendorElements {8 element types}
  ↓
Phase 3: Prospect Intelligence Analysis
  3 analysts → ProspectIntelligence {profile, pain points, personas}
  ↓
Phase 4: Sales Playbook Generation
  5-step process → SalesPlaybook {emails, talk tracks, battle cards}
  ↓
Output: PipelineRun {complete data from all phases}
```

---

## Phase 1: Intelligence Gathering (Steps 1-5)

### Current State: Partially Captured
- ✅ **Final output captured**: `vendor_content`, `prospect_content` dicts
- ❌ **Intermediary data lost**: Domain validation, homepage analysis, URL prioritization reasoning

### Future State: Fully Captured

#### Step 1: Domain Validation (Parallel)

**Executor Functions**: `validate_vendor_domain()`, `validate_prospect_domain()`

**Current Return**: `{"domain": str, "urls": List[str]}`

**Future Model**: `DomainValidation`
```python
{
    "domain": "https://octavehq.com",
    "urls_discovered": [...],  # Full list of ~100 URLs
    "url_count": 94,
    "map_timestamp": "2025-11-02T20:30:15",
    "validation_status": "success",
    "error_message": None
}
```

**Why Capture This**:
- Debug: "Why did we only discover 20 URLs instead of 100?"
- Analytics: "Which URL categories are most common?"
- Replay: Cache URL discovery to avoid re-mapping

---

#### Step 2: Homepage Scraping (Parallel)

**Executor Functions**: `scrape_vendor_homepage()`, `scrape_prospect_homepage()`

**Current Return**: `{"url": str, "content": str}`

**Future Model**: `HomepageScrapedContent`
```python
{
    "url": "https://octavehq.com",
    "markdown_content": "# Octave...",  # Full content
    "char_count": 12450,
    "word_count": 2100,
    "scrape_timestamp": "2025-11-02T20:30:25",
    "metadata": {
        "title": "Octave - GTM Context Engine",
        "description": "...",
        "has_cta": True
    }
}
```

**Why Capture This**:
- Debug: "Why did homepage analysis fail?" → Check raw content
- Quality: "How long are homepages we're analyzing?"
- Cache: Reuse homepage content without re-scraping

---

#### Step 3: Homepage Analysis (Parallel)

**Executor Functions**: `analyze_vendor_homepage()`, `analyze_prospect_homepage()`

**Current Return**: `{"company_basics": dict, "offerings": list}`

**Future Model**: `HomepageAnalysis`
```python
{
    "company_basics": {
        "name": "Octave",
        "tagline": "GTM Context Engine",
        "primary_offering": "AI-powered sales intelligence"
    },
    "key_offerings": [
        "Automated playbook generation",
        "ICP refinement"
    ],
    "ctas": ["Book a demo", "Try for free"],
    "analysis_timestamp": "2025-11-02T20:30:45"
}
```

**Why Capture This**:
- Debug: "Why didn't we identify any offerings?"
- Quality: "Are we correctly parsing homepage CTAs?"
- A/B Testing: Compare different homepage analysis prompts

---

#### Step 4: URL Prioritization

**Executor Function**: `prioritize_urls()`

**Current Return**: `{"vendor_urls": List[str], "prospect_urls": List[str]}`

**Future Model**: `URLPrioritization` with `PrioritizedURL` list
```python
{
    "prioritized_urls": [
        {
            "url": "https://octavehq.com/about",
            "priority_score": 9.5,
            "reasoning": "Core company information, likely contains mission/values",
            "category": "about"
        },
        {
            "url": "https://octavehq.com/customers",
            "priority_score": 9.0,
            "reasoning": "Customer proof points and case studies",
            "category": "customers"
        }
        # ... 10-13 more
    ],
    "total_urls_evaluated": 94,
    "urls_selected": 14,
    "prioritization_timestamp": "2025-11-02T20:31:10"
}
```

**Why Capture This**:
- Debug: "Why did we only select 5 URLs instead of 15?"
- Insights: "Which URL categories get highest priority?"
- Optimization: "Are we prioritizing the right pages?"
- A/B Testing: Compare different prioritization strategies

**This is HIGH VALUE data currently lost!**

---

#### Step 5: Batch Scraping

**Executor Function**: `batch_scrape_selected_pages()`

**Current Return**:
```python
{
    "vendor_content": {"url1": "content1", "url2": "content2"},
    "prospect_content": {...},
    "stats": {"vendor_pages": 12, ...}
}
```

**Future Model**: `BatchScrapedContent`
```python
{
    "scraped_pages": {
        "https://octavehq.com/about": "# About Octave...",
        "https://octavehq.com/platform": "# Platform...",
        # ... 12 more
    },
    "page_count": 14,
    "total_chars": 85000,
    "total_words": 14200,
    "scrape_timestamp": "2025-11-02T20:32:45",
    "failed_urls": ["https://octavehq.com/old-blog"]  # Timeouts, 404s, etc.
}
```

**Why Capture This**:
- Debug: "Which URLs failed to scrape?"
- Quality: "How much content are we feeding to Phase 2?"
- Cache: Reuse scraped content for Phase 2-4 replays

---

## Phase 2: Vendor Extraction (Step 6)

### Current State: ✅ Well Captured
Model: `VendorElements` (already exists in `models/vendor_elements.py`)

### 8 Parallel Specialists

| Specialist | Extracts | Model |
|------------|----------|-------|
| `extract_offerings()` | Products/services | `Offering` |
| `extract_case_studies()` | Customer stories | `CaseStudy` |
| `extract_proof_points()` | Testimonials, stats | `ProofPoint` |
| `extract_value_props()` | Value propositions | `ValueProposition` |
| `extract_customers()` | Reference customers | `ReferenceCustomer` |
| `extract_use_cases()` | Use cases | `UseCase` |
| `extract_personas()` | Vendor's ICP | `TargetPersona` |
| `extract_differentiators()` | Competitive advantages | `Differentiator` |

**Container Model**: `VendorElements`
```python
{
    "offerings": [Offering, Offering, ...],
    "case_studies": [CaseStudy, ...],
    "proof_points": [ProofPoint, ...],
    "value_propositions": [ValueProposition, ...],
    "reference_customers": [ReferenceCustomer, ...],
    "use_cases": [UseCase, ...],
    "vendor_icp_personas": [TargetPersona, ...],
    "differentiators": [Differentiator, ...]
}
```

**Future Enhancement**: Add `specialist_results` dict to `Phase2Output`:
```python
{
    "vendor_elements": VendorElements,  # Final merged output
    "extraction_timestamp": "2025-11-02T20:35:00",
    "specialist_results": {
        "offerings": {
            "raw_output": "...",
            "tokens_used": 1200,
            "execution_time": 3.5
        },
        "case_studies": {...},
        # ... for all 8 specialists
    }
}
```

**Why**: Debug individual specialist performance, track costs per specialist

---

## Phase 3: Prospect Analysis (Step 7)

### Current State: ✅ Well Captured
Model: `ProspectIntelligence` (already exists in `models/prospect_intelligence.py`)

### 3 Analysts (2 Parallel + 1 Sequential)

**Step 7a (Parallel)**:
- `analyze_company_profile()` → `CompanyProfile`
- `analyze_pain_points()` → `List[PainPoint]`

**Step 7b (Sequential)**:
- `identify_buyer_personas()` → `List[TargetBuyerPersona]`

**Container Model**: `ProspectIntelligence`
```python
{
    "company_profile": {
        "company_name": "Sendoso",
        "industry": "B2B SaaS",
        "company_size": "200-500",
        "what_they_do": "Gifting platform for sales and marketing",
        "target_market": "B2B companies with sales teams",
        "sources": [...]
    },
    "pain_points": [
        {
            "description": "Low cold outreach response rates",
            "category": "operational",
            "evidence": "Blog post mentions 'breaking through the noise'",
            "affected_personas": ["VP of Sales", "SDR Manager"],
            "confidence": "medium",
            "sources": [...]
        }
        # ... 5-10 pain points
    ],
    "target_buyer_personas": [
        {
            "persona_title": "VP of Sales",
            "department": "Sales",
            "why_they_care": "Needs to improve outbound effectiveness",
            "pain_points": ["Low response rates", "Team efficiency"],
            "goals": ["Increase pipeline", "Improve close rates"],
            "suggested_talking_points": [...],
            "priority_score": 9,
            "sources": [...]
        }
        # ... 2-4 more personas
    ]
}
```

**Future Enhancement**: Add `analyst_results` to `Phase3Output` (same pattern as Phase 2)

---

## Phase 4: Playbook Generation (Step 8)

### Current State: ✅ Well Captured
Model: `SalesPlaybook` (already exists in `models/playbook.py`)

### 5-Step Process

**Step 8a (Sequential)**: `generate_playbook_summary()`
- Outputs: Executive summary, priority personas, quick wins

**Step 8b-d (Parallel)**:
- `generate_email_sequences()` → `List[EmailSequence]` (4-touch × 3 personas = 12 emails)
- `generate_talk_tracks()` → `List[TalkTrack]` (3 talk tracks)
- `generate_battle_cards()` → `List[BattleCard]` (3 battle cards)

**Step 8e (Sequential)**: `assemble_final_playbook()`
- Combines all outputs into final `SalesPlaybook`

**Container Model**: `SalesPlaybook`
```python
{
    "vendor_name": "Octave",
    "prospect_name": "Sendoso",
    "generated_date": "2025-11-02",
    "executive_summary": "...",
    "priority_personas": ["CMO", "VP of Sales", "COO"],
    "quick_wins": ["Top 5 immediate actions"],
    "success_metrics": {
        "email_open_rate_target": "23%+",
        "email_response_rate_target": "1-3%",
        ...
    },
    "email_sequences": [EmailSequence, EmailSequence, EmailSequence],
    "talk_tracks": [TalkTrack, TalkTrack, TalkTrack],
    "battle_cards": [BattleCard, BattleCard, BattleCard]
}
```

**Sequencer-Ready Output**: `EmailTouch` models have `subject` and `body` fields that map directly to Lemlist/Smartlead/Instantly.

**Future Enhancement**: Add `specialist_results` to `Phase4Output` for debugging

---

## Data Size Estimates

### Per Phase

| Phase | Typical Size | Key Contributors |
|-------|-------------|------------------|
| Phase 1 | 150-200 KB | Scraped content (markdown) |
| Phase 2 | 50-80 KB | Structured vendor elements |
| Phase 3 | 20-30 KB | Prospect intelligence |
| Phase 4 | 100-150 KB | Complete playbook (12 emails, 3 talk tracks, 3 battle cards) |
| **Total** | **~500 KB** | Complete pipeline run |

### Storage Projection

- **100 runs**: 50 MB
- **1,000 runs**: 500 MB
- **10,000 runs**: 5 GB

JSON compression can reduce by ~70%, so 10,000 runs = ~1.5 GB compressed.

---

## Key Insights

### What's Already Well-Modeled ✅
- Phase 2: `VendorElements` (8 element types with sources)
- Phase 3: `ProspectIntelligence` (profile, pain points, personas)
- Phase 4: `SalesPlaybook` (sequencer-ready emails, talk tracks, battle cards)

### What's Missing ❌
- **Phase 1 intermediary data** (highest priority to add!)
  - Domain validation results
  - Homepage analysis reasoning
  - **URL prioritization reasoning** (critical for debugging)
  - Scraping failures/timeouts
- Individual specialist/analyst performance metrics
- Per-step timing and cost tracking

---

## Next Steps

1. **Implement Phase 1 models** first (highest value, currently lost)
2. **Add specialist_results tracking** to Phase 2-4 for debugging
3. **Capture per-step metrics** (timing, tokens, costs)
4. **Choose storage strategy** → See [STORAGE_STRATEGIES.md](./STORAGE_STRATEGIES.md)
5. **Follow implementation roadmap** → See [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)

---

**Related**: [PIPELINE_RUN_MODEL.md](./PIPELINE_RUN_MODEL.md) | [STORAGE_STRATEGIES.md](./STORAGE_STRATEGIES.md) | [CODE_EXAMPLES.md](./CODE_EXAMPLES.md)
