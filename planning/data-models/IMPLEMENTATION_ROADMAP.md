# Implementation Roadmap - 4-Phase Build Plan

**Total Estimated Effort**: 2-3 weeks
**Recommended Approach**: Incremental implementation with testing at each phase

---

## Phase 1: Basic Infrastructure (Week 1, Days 1-3)

### Goal
Set up basic `PipelineRun` model and JSON persistence without breaking existing functionality.

### Tasks

**1. Create models/pipeline_run.py** (2 hours)
- Copy Phase 1 models from [PIPELINE_RUN_MODEL.md](./PIPELINE_RUN_MODEL.md)
- Create: `DomainValidation`, `HomepageScrapedContent`, `HomepageAnalysis`, `URLPrioritization`, `BatchScrapedContent`
- Create: `Phase1Output`, `Phase2Output`, `Phase3Output`, `Phase4Output`
- Create: `PipelineRun` master model
- Test: Import models, create instances, verify model_dump_json() works

**2. Add run_id to workflow execution** (1 hour)
```python
# main.py
import uuid
from datetime import datetime

run_id = str(uuid.uuid4())
run_timestamp = datetime.now()

print(f"🚀 Starting pipeline run {run_id}")
print(f"   Vendor: {vendor_domain}")
print(f"   Prospect: {prospect_domain}")
```

**3. Create output/runs/ directory** (30 min)
```python
import os
os.makedirs("output/runs", exist_ok=True)
```

**4. Save basic PipelineRun as JSON** (2 hours)
```python
# At end of workflow in main.py
from models.pipeline_run import PipelineRun

# Create PipelineRun instance (start with just input/output)
run = PipelineRun(
    run_id=run_id,
    run_timestamp=run_timestamp,
    workflow_input=WorkflowInput(
        vendor_domain=vendor_domain,
        prospect_domain=prospect_domain
    ),
    # Leave phase outputs as None for now
    status="completed",
    execution_time_seconds=time.time() - start_time
)

# Save JSON
json_path = f"output/runs/{run.run_id}.json"
with open(json_path, 'w') as f:
    f.write(run.model_dump_json(indent=2))

print(f"✅ Pipeline run saved: {json_path}")
```

**5. Test end-to-end** (1 hour)
```bash
python main.py octavehq.com sendoso.com
# Verify JSON file created in output/runs/
```

### Success Criteria
- ✅ Models import without errors
- ✅ Can create PipelineRun instance
- ✅ JSON file saved to output/runs/
- ✅ Existing workflow still works (no breaking changes)

---

## Phase 2: Capture Phase 1 Intermediary Data (Week 1, Days 4-7)

### Goal
Modify Phase 1 steps to return structured data, populate `Phase1Output`.

### Tasks

**1. Update Step 1: Domain Validation** (2 hours)
```python
# steps/step1_domain_validation.py
from models.pipeline_run import DomainValidation
from datetime import datetime

def validate_vendor_domain(step_input: StepInput) -> StepOutput:
    # ... existing code ...

    validation = DomainValidation(
        domain=normalized_domain,
        urls_discovered=all_urls,
        url_count=len(all_urls),
        map_timestamp=datetime.now(),
        validation_status="success"
    )

    return StepOutput(content=validation.model_dump())
```

**2. Update Step 2: Homepage Scraping** (2 hours)
```python
# steps/step2_homepage_scraping.py
from models.pipeline_run import HomepageScrapedContent

def scrape_vendor_homepage(step_input: StepInput) -> StepOutput:
    # ... scraping logic ...

    homepage = HomepageScrapedContent(
        url=homepage_url,
        markdown_content=content,
        char_count=len(content),
        word_count=len(content.split()),
        scrape_timestamp=datetime.now(),
        metadata={"title": "...", "description": "..."}
    )

    return StepOutput(content=homepage.model_dump())
```

**3. Update Step 3-5** (4 hours total)
- Follow same pattern for Steps 3, 4, 5
- Each step returns structured model via `model_dump()`

**4. Extract Phase1Output in main.py** (3 hours)
```python
# main.py - after workflow execution
from utils.workflow_helpers import get_parallel_step_content

# Extract all Phase 1 data
vendor_validation = DomainValidation(**get_parallel_step_content(result, "validate_vendor"))
prospect_validation = DomainValidation(**get_parallel_step_content(result, "validate_prospect"))

# ... similar for all Phase 1 steps ...

phase1_output = Phase1Output(
    vendor_validation=vendor_validation,
    prospect_validation=prospect_validation,
    vendor_homepage=vendor_homepage,
    # ... all 10 fields
)

# Add to PipelineRun
run = PipelineRun(
    # ... existing fields ...
    phase1_output=phase1_output
)
```

**5. Test** (1 hour)
- Verify Phase 1 data captured in JSON
- Check all fields populated correctly
- Validate against Pydantic schema

### Success Criteria
- ✅ All 10 Phase 1 data points captured
- ✅ JSON file contains phase1_output
- ✅ No data loss from previous behavior

---

## Phase 3: SQLite Indexing (Week 2, Days 1-4)

### Goal
Add SQLite database for fast querying without losing JSON storage.

### Tasks

**1. Create database schema** (3 hours)
```bash
sqlite3 output/octave.db < planning/data-models/schema.sql
```

Create `schema.sql` with tables from [STORAGE_STRATEGIES.md](./STORAGE_STRATEGIES.md)

**2. Add database helper module** (4 hours)
```python
# utils/database_helpers.py
import sqlite3
from models.pipeline_run import PipelineRun

def init_database():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect('output/octave.db')
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()

def index_pipeline_run(run: PipelineRun):
    """Index key fields in SQLite"""
    conn = sqlite3.connect('output/octave.db')
    cursor = conn.cursor()

    # Insert main run
    cursor.execute("""
        INSERT INTO pipeline_runs
        (id, vendor_domain, prospect_domain, status, ...)
        VALUES (?, ?, ?, ?, ...)
    """, (...))

    # Index email sequences
    if run.phase4_output:
        for seq in run.phase4_output.sales_playbook.email_sequences:
            cursor.execute("""
                INSERT INTO email_sequences (...)
                VALUES (...)
            """, (...))

    conn.commit()
    conn.close()
```

**3. Update main.py to call index** (1 hour)
```python
# main.py - after saving JSON
from utils.database_helpers import index_pipeline_run

# Save JSON (existing)
with open(json_path, 'w') as f:
    f.write(run.model_dump_json(indent=2))

# Index in SQLite (new)
index_pipeline_run(run)

print(f"✅ Run indexed in database")
```

**4. Create query interface** (3 hours)
```python
# utils/query_interface.py
import sqlite3

def find_runs_by_prospect(prospect_domain: str):
    """Find all runs for a prospect"""
    conn = sqlite3.connect('output/octave.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, vendor_domain, run_timestamp
        FROM pipeline_runs
        WHERE prospect_domain = ?
        ORDER BY run_timestamp DESC
    """, (prospect_domain,))
    return cursor.fetchall()

def get_email_sequences_by_persona(persona_title: str):
    """Get all email sequences for a persona"""
    # ... query logic ...
```

**5. Test queries** (2 hours)
```python
# Test in Python shell
from utils.query_interface import find_runs_by_prospect
runs = find_runs_by_prospect("https://sendoso.com")
print(f"Found {len(runs)} runs for Sendoso")
```

### Success Criteria
- ✅ SQLite database created with schema
- ✅ Pipeline runs indexed automatically
- ✅ Can query runs by prospect/vendor
- ✅ Email sequences queryable by persona

---

## Phase 4: Analytics & Monitoring (Week 2-3, Days 5-10)

### Goal
Build analytics dashboard and cost tracking.

### Tasks

**1. Add cost tracking to workflow** (3 hours)
```python
# Track tokens per step
from agno.utils import count_tokens  # hypothetical

class CostTracker:
    def __init__(self):
        self.total_tokens = 0
        self.total_api_calls = 0

    def track_openai_call(self, prompt, response):
        tokens = count_tokens(prompt) + count_tokens(response)
        self.total_tokens += tokens
        self.total_api_calls += 1

    def estimate_cost(self):
        # GPT-4o: $2.50 / 1M input tokens, $10 / 1M output
        return (self.total_tokens / 1_000_000) * 6.25  # Average

# Use in workflow
tracker = CostTracker()
# ... track each AI call ...
run.total_tokens_used = tracker.total_tokens
run.estimated_cost_usd = tracker.estimate_cost()
```

**2. Create simple Streamlit dashboard** (6 hours)
```python
# analytics/dashboard.py
import streamlit as st
import sqlite3
import pandas as pd

st.title("Octave Pipeline Analytics")

# Load data
conn = sqlite3.connect('output/octave.db')
df = pd.read_sql("SELECT * FROM pipeline_runs", conn)

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Runs", len(df))
col2.metric("Avg Cost", f"${df['estimated_cost_usd'].mean():.2f}")
col3.metric("Avg Time", f"{df['execution_time_seconds'].mean():.1f}s")

# Charts
st.line_chart(df.groupby('run_timestamp')['estimated_cost_usd'].sum())

# Query interface
prospect = st.text_input("Search by prospect domain")
if prospect:
    results = df[df['prospect_domain'].str.contains(prospect)]
    st.dataframe(results)
```

Run: `streamlit run analytics/dashboard.py`

**3. Add quality monitoring** (3 hours)
```python
# Track playbook quality metrics
def calculate_playbook_quality(playbook: SalesPlaybook) -> dict:
    return {
        "email_count": len(playbook.email_sequences),
        "avg_email_length": ...,
        "has_battle_cards": len(playbook.battle_cards) > 0,
        "persona_coverage": len(playbook.priority_personas)
    }
```

**4. Build CLI query tool** (2 hours)
```bash
python scripts/query_runs.py --prospect sendoso.com
python scripts/query_runs.py --vendor octavehq.com --latest 5
python scripts/query_runs.py --status failed --since 2025-11-01
```

**5. Documentation** (2 hours)
- Write guide for querying data
- Document analytics dashboard usage
- Create troubleshooting guide

### Success Criteria
- ✅ Cost tracking per run
- ✅ Analytics dashboard running
- ✅ Can query via CLI
- ✅ Quality metrics calculated

---

## Testing Strategy

### Unit Tests
```python
# tests/test_pipeline_run_model.py
def test_pipeline_run_creation():
    run = PipelineRun(...)
    assert run.run_id is not None
    assert run.status == "running"

def test_phase1_output_serialization():
    phase1 = Phase1Output(...)
    json_str = phase1.model_dump_json()
    reconstructed = Phase1Output.model_validate_json(json_str)
    assert reconstructed == phase1
```

### Integration Tests
```python
# tests/test_storage.py
def test_save_and_load_run():
    run = create_test_run()
    save_pipeline_run(run)
    loaded = load_pipeline_run(run.run_id)
    assert loaded.run_id == run.run_id
```

### End-to-End Tests
```bash
# Run complete pipeline and verify output
python main.py octavehq.com sendoso.com
python -c "from utils.query_interface import *; assert len(find_runs_by_prospect('sendoso.com')) > 0"
```

---

## Rollout Plan

### Week 1
- Days 1-3: Phase 1 (Basic infrastructure)
- Days 4-7: Phase 2 (Capture Phase 1 data)

### Week 2
- Days 1-4: Phase 3 (SQLite indexing)
- Days 5-7: Phase 4 (Analytics start)

### Week 3
- Days 1-3: Phase 4 (Analytics finish)
- Days 4-5: Testing and bug fixes
- Day 6-7: Documentation and deployment

---

## Risk Mitigation

### Breaking Changes Risk
- **Mitigation**: Implement behind feature flag
- Add `ENABLE_FULL_TELEMETRY=false` env var
- Default to false until tested

### Performance Risk
- **Mitigation**: Profile each phase
- Benchmark: Should add < 5% overhead
- Use async for SQLite inserts if needed

### Storage Growth Risk
- **Mitigation**: Implement cleanup policy
- Delete runs older than 90 days (configurable)
- Compress old JSON files

---

## Next Steps

1. **Review code examples**: [CODE_EXAMPLES.md](./CODE_EXAMPLES.md)
2. **Understand use cases**: [USE_CASES.md](./USE_CASES.md)
3. **Create GitHub issues** for each phase
4. **Start with Phase 1** and iterate

---

**Estimated Timeline**: 2-3 weeks (10-15 working days)
**Priority**: Medium (enables future analytics, not blocking current functionality)
**Dependencies**: None (can implement incrementally)

**Related**: [PIPELINE_RUN_MODEL.md](./PIPELINE_RUN_MODEL.md) | [STORAGE_STRATEGIES.md](./STORAGE_STRATEGIES.md) | [CODE_EXAMPLES.md](./CODE_EXAMPLES.md)
