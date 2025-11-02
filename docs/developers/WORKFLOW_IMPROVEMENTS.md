# Workflow Improvements Plan

**Created:** 2025-11-02
**Status:** In Progress

## Overview

Fixing two major issues with the Octave Clone workflow:
1. `main.py` only runs Phase 1 (5 steps) instead of all 4 phases (8 steps)
2. Slow scraping performance (need to add `maxAge` for 500% speedup)
3. Add Agno native TUI for workflow visualization

---

## Issue 1: Incomplete Workflow Execution

### Current State
**File:** `main.py:15`
```python
from workflow import phase1_workflow
```

**Problem:** Only imports `phase1_workflow` which contains Steps 1-5 (Intelligence Gathering only).

**Available workflows in workflow.py:**
- `phase1_workflow` - Steps 1-5 (Intelligence Gathering)
- `phase1_2_workflow` - Steps 1-6 (+ Vendor Extraction)
- `phase1_2_3_workflow` - Steps 1-7 (+ Prospect Analysis)
- `phase1_2_3_4_workflow` - Steps 1-8 (Complete MVP with Playbook)

### Proposed Solution

**Consolidate workflow definition in main.py** with all steps defined inline:

```python
from agno.workflow import Workflow, Step, Parallel

workflow = Workflow(
    name="Octave Clone - Complete Sales Intelligence Pipeline",
    steps=[
        # Phase 1: Intelligence Gathering (Steps 1-5)
        Parallel(
            name="parallel_validation",
            steps=[
                Step(name="validate_vendor", executor=validate_vendor),
                Step(name="validate_prospect", executor=validate_prospect)
            ]
        ),
        Parallel(
            name="parallel_homepage_scraping",
            steps=[
                Step(name="scrape_vendor_home", executor=scrape_vendor_homepage),
                Step(name="scrape_prospect_home", executor=scrape_prospect_homepage)
            ]
        ),
        Parallel(
            name="parallel_homepage_analysis",
            steps=[
                Step(name="analyze_vendor_home", executor=analyze_vendor_homepage),
                Step(name="analyze_prospect_home", executor=analyze_prospect_homepage)
            ]
        ),
        Step(name="url_prioritization", executor=prioritize_urls),
        Step(name="batch_scrape", executor=batch_scrape_selected_pages),

        # Phase 2: Vendor Extraction (Step 6)
        Parallel(
            name="vendor_element_extraction",
            steps=[
                Step(name="extract_offerings", executor=extract_offerings),
                Step(name="extract_case_studies", executor=extract_case_studies),
                Step(name="extract_testimonials", executor=extract_testimonials),
                Step(name="extract_competitive_intel", executor=extract_competitive_intel),
                Step(name="extract_pricing", executor=extract_pricing),
                Step(name="extract_roi_stats", executor=extract_roi_stats),
                Step(name="extract_integrations", executor=extract_integrations),
                Step(name="extract_key_differentiators", executor=extract_key_differentiators)
            ]
        ),

        # Phase 3: Prospect Analysis (Step 7)
        Parallel(
            name="prospect_context_analysis",
            steps=[
                Step(name="analyze_company", executor=analyze_company_context),
                Step(name="analyze_pain_points", executor=analyze_pain_points),
                Step(name="identify_personas", executor=identify_buyer_personas)
            ]
        ),

        # Phase 4: Playbook Generation (Step 8)
        Parallel(
            name="playbook_generation",
            steps=[
                Step(name="generate_battle_card", executor=generate_battle_card),
                Step(name="generate_email_sequence", executor=generate_email_sequence),
                Step(name="generate_talk_tracks", executor=generate_talk_tracks)
            ]
        )
    ]
)
```

**Benefits:**
- ✅ Single workflow definition in main.py
- ✅ Clear visualization of all 8 steps
- ✅ Easy to understand pipeline flow
- ✅ No need for separate workflow.py file
- ✅ Matches Agno best practices

---

## Issue 2: Slow Scraping Performance

### Current State

**File:** `utils/firecrawl_helpers.py`

**Single URL scraping (line 67):**
```python
result = fc.scrape(url, formats=formats, wait_for=config.SCRAPE_WAIT_TIME)
```

**Batch scraping (lines 112-117):**
```python
job = fc.batch_scrape(
    urls,
    formats=formats,
    poll_interval=config.BATCH_SCRAPE_POLL_INTERVAL,
    wait_timeout=config.BATCH_SCRAPE_TIMEOUT
)
```

**Problem:** No `maxAge` parameter = fresh scrape every time (slow!)

### Proposed Solution

**Add maxAge parameter for 500% faster scraping**

According to Firecrawl docs:
> Get your results **up to 500% faster** when you don't need the absolute freshest data.

**Step 1: Add configuration**

**File:** `config.py`
```python
# Scraping Performance Configuration
SCRAPE_MAX_AGE = 172800000  # 48 hours in milliseconds (2 days)
                            # Use cached data if available - 500% faster!
                            # Set to 0 to force fresh scrapes
```

**Step 2: Update scrape_url() function**

**File:** `utils/firecrawl_helpers.py` (line 67)
```python
result = fc.scrape(
    url,
    formats=formats,
    wait_for=config.SCRAPE_WAIT_TIME,
    maxAge=config.SCRAPE_MAX_AGE  # NEW: 500% faster with cache
)
```

**Step 3: Update batch_scrape_urls() function**

**File:** `utils/firecrawl_helpers.py` (lines 112-117)
```python
job = fc.batch_scrape(
    urls,
    formats=formats,
    poll_interval=config.BATCH_SCRAPE_POLL_INTERVAL,
    wait_timeout=config.BATCH_SCRAPE_TIMEOUT,
    maxAge=config.SCRAPE_MAX_AGE  # NEW: 500% faster with cache
)
```

**Benefits:**
- ✅ **500% faster scraping** using cached data (2-day freshness)
- ✅ **Automatic fallback** to fresh scrape if cache older than maxAge
- ✅ **Configurable** via config.py
- ✅ **No code changes needed** to switch between fresh/cached

**Common maxAge values:**
- 5 minutes: `300000` - For semi-dynamic content
- 1 hour: `3600000` - For hourly-updated content
- 1 day: `86400000` - For daily-updated content
- 2 days: `172800000` - Recommended default
- 1 week: `604800000` - For static content

---

## Issue 3: Add Agno Native TUI

### Current State

**File:** `main.py` (line 52)
```python
result = phase1_workflow.run(input=workflow_input)
```

**Problem:** No workflow visualization during execution.

### Proposed Solution

**Enable Agno's built-in TUI for real-time workflow visualization**

According to Agno docs, there are two ways to visualize workflow execution:

**Option 1: Using print_response() (Recommended)**
```python
# Instead of:
result = workflow.run(input=workflow_input)

# Use:
workflow.print_response(message=workflow_input, stream=True)
```

**Option 2: Using run() with streaming**
```python
result = workflow.run(input=workflow_input, stream=True)
```

**Update main.py:**

```python
# Enable workflow visualization with streaming
if __name__ == "__main__":
    # ... setup code ...

    print("\n" + "="*80)
    print("🚀 Starting Complete Workflow (All 4 Phases)...")
    print("="*80 + "\n")

    # Run with Agno native TUI and streaming
    workflow.print_response(message=workflow_input, stream=True)

    # Alternative: Get result back
    # result = workflow.run(input=workflow_input, stream=True)
```

**Benefits:**
- ✅ **Real-time visualization** of workflow execution
- ✅ **See which step is running** at any moment
- ✅ **Stream output** as it's generated
- ✅ **Native Agno TUI** - no custom code needed
- ✅ **Better debugging** - see exactly where failures occur

---

## Implementation Checklist

### Phase 1: Consolidate Workflow in main.py
- [ ] Move all step imports to main.py
- [ ] Define complete workflow inline with all 8 steps
- [ ] Remove dependency on workflow.py (or deprecate it)
- [ ] Test workflow runs all 4 phases

### Phase 2: Add maxAge for Performance
- [ ] Add `SCRAPE_MAX_AGE` to config.py
- [ ] Update `scrape_url()` in utils/firecrawl_helpers.py
- [ ] Update `batch_scrape_urls()` in utils/firecrawl_helpers.py
- [ ] Test scraping speed improvement

### Phase 3: Enable Agno TUI
- [ ] Update main.py to use `print_response()` or `run(stream=True)`
- [ ] Test TUI visualization during workflow execution
- [ ] Document TUI usage in developer docs

### Phase 4: Testing
- [ ] Run complete workflow: `python main.py https://octavehq.com https://sendoso.com`
- [ ] Verify all 4 phases execute
- [ ] Verify TUI displays workflow progress
- [ ] Verify scraping performance improvement
- [ ] Update documentation

---

## Files to Modify

1. **`main.py`** - Consolidate workflow definition, enable TUI
2. **`config.py`** - Add SCRAPE_MAX_AGE configuration
3. **`utils/firecrawl_helpers.py`** - Add maxAge to scraping calls

---

## Expected Results

### Before
- ✗ Only Phase 1 runs (5 steps)
- ✗ Slow scraping (fresh scrapes every time)
- ✗ No workflow visualization

### After
- ✅ All 4 phases run (8 steps)
- ✅ 500% faster scraping with maxAge
- ✅ Real-time workflow visualization with Agno TUI
- ✅ Single workflow definition in main.py
- ✅ Streaming output

---

## Time Estimate

- **Workflow consolidation:** ~15 minutes
- **Add maxAge parameter:** ~5 minutes
- **Enable TUI:** ~5 minutes
- **Testing:** ~10 minutes
- **Total:** ~35 minutes

---

## References

- **Firecrawl maxAge docs:** https://docs.firecrawl.dev/features/faster-scraping
- **Agno Workflow docs:** https://docs.agno.com
- **Current workflow.py:** Line 74-162 (all workflow definitions)
- **Current main.py:** Line 15 & 52 (imports and execution)
