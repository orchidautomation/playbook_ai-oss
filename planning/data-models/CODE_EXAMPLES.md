# Code Examples - Implementation Reference

**Purpose**: Complete, copy-paste-ready code for implementing the pipeline data model.

---

## Complete models/pipeline_run.py File

```python
"""
Pipeline Run Models - Complete Data Model for Pipeline Execution
Captures all intermediary data and final outputs from Phase 1-4.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from models.workflow_input import WorkflowInput
from models.vendor_elements import VendorElements
from models.prospect_intelligence import ProspectIntelligence
from models.playbook import SalesPlaybook


# ==================================================================
# PHASE 1 INTERMEDIARY MODELS
# ==================================================================

class DomainValidation(BaseModel):
    """Results from Step 1: Domain validation and URL discovery"""
    domain: str
    urls_discovered: List[str] = Field(default_factory=list)
    url_count: int
    map_timestamp: datetime
    validation_status: str  # "success", "partial", "failed"
    error_message: Optional[str] = None


class HomepageScrapedContent(BaseModel):
    """Results from Step 2: Homepage scraping"""
    url: str
    markdown_content: str
    char_count: int
    word_count: int
    scrape_timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HomepageAnalysis(BaseModel):
    """Results from Step 3: AI homepage analysis"""
    company_basics: Dict[str, str] = Field(default_factory=dict)
    key_offerings: List[str] = Field(default_factory=list)
    ctas: List[str] = Field(default_factory=list)
    analysis_timestamp: datetime


class PrioritizedURL(BaseModel):
    """Single prioritized URL with reasoning"""
    url: str
    priority_score: float = Field(ge=0.0, le=10.0)
    reasoning: str
    category: str


class URLPrioritization(BaseModel):
    """Results from Step 4: URL prioritization"""
    prioritized_urls: List[PrioritizedURL] = Field(default_factory=list)
    total_urls_evaluated: int
    urls_selected: int
    prioritization_timestamp: datetime


class BatchScrapedContent(BaseModel):
    """Results from Step 5: Batch scraping"""
    scraped_pages: Dict[str, str] = Field(default_factory=dict)
    page_count: int
    total_chars: int
    total_words: int
    scrape_timestamp: datetime
    failed_urls: List[str] = Field(default_factory=list)


# ==================================================================
# PHASE-LEVEL CONTAINERS
# ==================================================================

class Phase1Output(BaseModel):
    """Complete Phase 1 intelligence gathering output"""
    vendor_validation: DomainValidation
    prospect_validation: DomainValidation
    vendor_homepage: HomepageScrapedContent
    prospect_homepage: HomepageScrapedContent
    vendor_homepage_analysis: HomepageAnalysis
    prospect_homepage_analysis: HomepageAnalysis
    vendor_url_prioritization: URLPrioritization
    prospect_url_prioritization: URLPrioritization
    vendor_batch_content: BatchScrapedContent
    prospect_batch_content: BatchScrapedContent


class Phase2Output(BaseModel):
    """Phase 2 vendor extraction output"""
    vendor_elements: VendorElements
    extraction_timestamp: datetime
    specialist_results: Dict[str, Any] = Field(default_factory=dict)


class Phase3Output(BaseModel):
    """Phase 3 prospect analysis output"""
    prospect_intelligence: ProspectIntelligence
    analysis_timestamp: datetime
    analyst_results: Dict[str, Any] = Field(default_factory=dict)


class Phase4Output(BaseModel):
    """Phase 4 playbook generation output"""
    sales_playbook: SalesPlaybook
    generation_timestamp: datetime
    specialist_results: Dict[str, Any] = Field(default_factory=dict)


# ==================================================================
# MASTER PIPELINE RUN MODEL
# ==================================================================

class PipelineRun(BaseModel):
    """
    Complete pipeline run capturing ALL data from all 4 phases.
    """
    # Metadata
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_timestamp: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="running")
    execution_time_seconds: Optional[float] = None

    # Input
    workflow_input: WorkflowInput

    # Phase Outputs
    phase1_output: Optional[Phase1Output] = None
    phase2_output: Optional[Phase2Output] = None
    phase3_output: Optional[Phase3Output] = None
    phase4_output: Optional[Phase4Output] = None

    # Metrics
    total_api_calls: int = 0
    total_tokens_used: int = 0
    estimated_cost_usd: Optional[float] = None

    # Error Tracking
    errors: List[Dict[str, str]] = Field(default_factory=list)
    warnings: List[Dict[str, str]] = Field(default_factory=list)

    # Audit Trail
    created_by: Optional[str] = None
    created_via: str = "CLI"
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
```

---

## Hybrid Storage Implementation

### utils/storage_helpers.py

```python
"""
Storage Helpers - Hybrid JSON + SQLite Storage
"""

import json
import sqlite3
import os
from pathlib import Path
from datetime import datetime
from models.pipeline_run import PipelineRun


def ensure_directories():
    """Create necessary directories"""
    os.makedirs("output/runs", exist_ok=True)


def save_pipeline_run(run: PipelineRun) -> str:
    """
    Save pipeline run with hybrid storage.
    Returns the JSON file path.
    """
    ensure_directories()

    # 1. Save complete JSON (full fidelity)
    json_path = f"output/runs/{run.run_id}.json"
    with open(json_path, 'w') as f:
        f.write(run.model_dump_json(indent=2))

    # 2. Index in SQLite (fast queries)
    index_pipeline_run(run)

    return json_path


def load_pipeline_run(run_id: str) -> PipelineRun:
    """Load complete pipeline run from JSON"""
    json_path = f"output/runs/{run_id}.json"

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Pipeline run {run_id} not found")

    with open(json_path, 'r') as f:
        data = json.load(f)
        return PipelineRun(**data)


def index_pipeline_run(run: PipelineRun):
    """Index key fields in SQLite for fast queries"""
    conn = sqlite3.connect('output/octave.db')
    cursor = conn.cursor()

    # Insert main run
    cursor.execute("""
        INSERT OR REPLACE INTO pipeline_runs
        (id, vendor_domain, prospect_domain, status, run_timestamp,
         execution_time_seconds, total_api_calls, total_tokens_used,
         estimated_cost_usd, created_by, created_via)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run.run_id,
        run.workflow_input.vendor_domain,
        run.workflow_input.prospect_domain,
        run.status,
        run.run_timestamp.isoformat(),
        run.execution_time_seconds,
        run.total_api_calls,
        run.total_tokens_used,
        run.estimated_cost_usd,
        run.created_by,
        run.created_via
    ))

    # Index email sequences
    if run.phase4_output and run.phase4_output.sales_playbook:
        for seq in run.phase4_output.sales_playbook.email_sequences:
            cursor.execute("""
                INSERT INTO email_sequences
                (run_id, persona_title, sequence_name, total_touches, sequence_json)
                VALUES (?, ?, ?, ?, ?)
            """, (
                run.run_id,
                seq.persona_title,
                seq.sequence_name,
                seq.total_touches,
                seq.model_dump_json()
            ))

    # Index battle cards
    if run.phase4_output and run.phase4_output.sales_playbook:
        for card in run.phase4_output.sales_playbook.battle_cards:
            cursor.execute("""
                INSERT INTO battle_cards
                (run_id, card_type, title, card_json)
                VALUES (?, ?, ?, ?)
            """, (
                run.run_id,
                card.card_type,
                card.title,
                card.model_dump_json()
            ))

    conn.commit()
    conn.close()
```

---

## Query Interface

### utils/query_interface.py

```python
"""
Query Interface - Fast SQLite Queries
"""

import sqlite3
from typing import List, Tuple, Optional
from datetime import datetime


def find_runs_by_prospect(prospect_domain: str) -> List[Tuple]:
    """Find all runs for a specific prospect"""
    conn = sqlite3.connect('output/octave.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, vendor_domain, run_timestamp, status, execution_time_seconds
        FROM pipeline_runs
        WHERE prospect_domain = ?
        ORDER BY run_timestamp DESC
    """, (prospect_domain,))
    results = cursor.fetchall()
    conn.close()
    return results


def find_runs_by_vendor(vendor_domain: str) -> List[Tuple]:
    """Find all runs for a specific vendor"""
    conn = sqlite3.connect('output/octave.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, prospect_domain, run_timestamp, status
        FROM pipeline_runs
        WHERE vendor_domain = ?
        ORDER BY run_timestamp DESC
    """, (vendor_domain,))
    results = cursor.fetchall()
    conn.close()
    return results


def get_email_sequences_by_persona(persona_title: str, limit: int = 10) -> List[Tuple]:
    """Get email sequences for a specific persona"""
    conn = sqlite3.connect('output/octave.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT es.run_id, pr.vendor_domain, pr.prospect_domain, es.sequence_json
        FROM email_sequences es
        JOIN pipeline_runs pr ON es.run_id = pr.id
        WHERE es.persona_title = ?
        ORDER BY es.created_at DESC
        LIMIT ?
    """, (persona_title, limit))
    results = cursor.fetchall()
    conn.close()
    return results


def get_cost_summary(since_date: Optional[str] = None) -> dict:
    """Get cost summary statistics"""
    conn = sqlite3.connect('output/octave.db')
    cursor = conn.cursor()

    query = """
        SELECT
            COUNT(*) as total_runs,
            SUM(estimated_cost_usd) as total_cost,
            AVG(estimated_cost_usd) as avg_cost,
            AVG(execution_time_seconds) as avg_time,
            SUM(total_tokens_used) as total_tokens
        FROM pipeline_runs
        WHERE status = 'completed'
    """

    if since_date:
        query += " AND run_timestamp >= ?"
        cursor.execute(query, (since_date,))
    else:
        cursor.execute(query)

    result = cursor.fetchone()
    conn.close()

    return {
        "total_runs": result[0],
        "total_cost": result[1] or 0.0,
        "avg_cost": result[2] or 0.0,
        "avg_time": result[3] or 0.0,
        "total_tokens": result[4] or 0
    }


def get_failed_runs(limit: int = 20) -> List[Tuple]:
    """Get recent failed pipeline runs"""
    conn = sqlite3.connect('output/octave.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, vendor_domain, prospect_domain, run_timestamp
        FROM pipeline_runs
        WHERE status = 'failed'
        ORDER BY run_timestamp DESC
        LIMIT ?
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    return results
```

---

## Updated main.py Integration

```python
"""
main.py - Updated to use PipelineRun model
"""

import sys
import time
from datetime import datetime
from models.workflow_input import WorkflowInput
from models.pipeline_run import PipelineRun
from utils.storage_helpers import save_pipeline_run
from workflow import phase1_2_3_4_workflow

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <vendor_domain> <prospect_domain>")
        sys.exit(1)

    # Parse input
    vendor_domain = sys.argv[1]
    prospect_domain = sys.argv[2]

    # Create workflow input (with domain normalization)
    workflow_input = WorkflowInput(
        vendor_domain=vendor_domain,
        prospect_domain=prospect_domain
    )

    # Initialize pipeline run
    run = PipelineRun(
        workflow_input=workflow_input,
        status="running",
        created_via="CLI"
    )

    print(f"🚀 Starting pipeline run {run.run_id}")
    print(f"   Vendor: {workflow_input.vendor_domain}")
    print(f"   Prospect: {workflow_input.prospect_domain}")
    print()

    start_time = time.time()

    try:
        # Execute workflow
        result = phase1_2_3_4_workflow.print_response(
            message=workflow_input.to_workflow_dict(),
            stream=True
        )

        # Update run status
        run.status = "completed"
        run.execution_time_seconds = time.time() - start_time

        # Extract phase outputs (TODO: implement extraction logic)
        # run.phase1_output = extract_phase1_output(result)
        # run.phase2_output = extract_phase2_output(result)
        # ... etc

    except Exception as e:
        run.status = "failed"
        run.errors.append({
            "phase": "unknown",
            "step": "unknown",
            "message": str(e)
        })
        print(f"❌ Pipeline failed: {str(e)}")

    # Save run (JSON + SQLite)
    json_path = save_pipeline_run(run)

    print()
    print(f"✅ Pipeline run completed in {run.execution_time_seconds:.1f}s")
    print(f"   Run ID: {run.run_id}")
    print(f"   Output: {json_path}")
    print(f"   Status: {run.status}")


if __name__ == "__main__":
    main()
```

---

## CLI Query Tool

### scripts/query_runs.py

```python
"""
CLI Query Tool - Search pipeline runs
"""

import argparse
from utils.query_interface import *
from utils.storage_helpers import load_pipeline_run

def main():
    parser = argparse.ArgumentParser(description="Query pipeline runs")
    parser.add_argument("--prospect", help="Filter by prospect domain")
    parser.add_argument("--vendor", help="Filter by vendor domain")
    parser.add_argument("--persona", help="Find email sequences for persona")
    parser.add_argument("--costs", action="store_true", help="Show cost summary")
    parser.add_argument("--failed", action="store_true", help="Show failed runs")
    parser.add_argument("--latest", type=int, help="Show N latest runs")
    parser.add_argument("--load", help="Load complete run by ID")

    args = parser.parse_args()

    if args.prospect:
        runs = find_runs_by_prospect(args.prospect)
        print(f"\n📊 Runs for prospect: {args.prospect}")
        print(f"Found {len(runs)} runs:\n")
        for run_id, vendor, timestamp, status, exec_time in runs:
            print(f"  {run_id[:8]}... | {vendor} | {timestamp} | {status} | {exec_time:.1f}s")

    elif args.vendor:
        runs = find_runs_by_vendor(args.vendor)
        print(f"\n📊 Runs for vendor: {args.vendor}")
        print(f"Found {len(runs)} runs:\n")
        for run_id, prospect, timestamp, status in runs:
            print(f"  {run_id[:8]}... | {prospect} | {timestamp} | {status}")

    elif args.persona:
        sequences = get_email_sequences_by_persona(args.persona)
        print(f"\n📧 Email sequences for: {args.persona}")
        print(f"Found {len(sequences)} sequences:\n")
        for run_id, vendor, prospect, seq_json in sequences:
            print(f"  {vendor} → {prospect}")

    elif args.costs:
        summary = get_cost_summary()
        print("\n💰 Cost Summary:")
        print(f"  Total Runs: {summary['total_runs']}")
        print(f"  Total Cost: ${summary['total_cost']:.2f}")
        print(f"  Avg Cost: ${summary['avg_cost']:.2f}")
        print(f"  Avg Time: {summary['avg_time']:.1f}s")
        print(f"  Total Tokens: {summary['total_tokens']:,}")

    elif args.failed:
        runs = get_failed_runs()
        print(f"\n❌ Failed Runs: {len(runs)}\n")
        for run_id, vendor, prospect, timestamp in runs:
            print(f"  {run_id[:8]}... | {vendor} → {prospect} | {timestamp}")

    elif args.load:
        run = load_pipeline_run(args.load)
        print(f"\n📄 Pipeline Run: {run.run_id}")
        print(f"  Vendor: {run.workflow_input.vendor_domain}")
        print(f"  Prospect: {run.workflow_input.prospect_domain}")
        print(f"  Status: {run.status}")
        print(f"  Time: {run.execution_time_seconds:.1f}s")
        print(f"  Cost: ${run.estimated_cost_usd:.2f}")
        if run.phase4_output:
            print(f"  Emails: {len(run.phase4_output.sales_playbook.email_sequences)} sequences")
            print(f"  Battle Cards: {len(run.phase4_output.sales_playbook.battle_cards)}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

**Usage**:
```bash
python scripts/query_runs.py --prospect sendoso.com
python scripts/query_runs.py --vendor octavehq.com
python scripts/query_runs.py --persona "CMO"
python scripts/query_runs.py --costs
python scripts/query_runs.py --failed
python scripts/query_runs.py --load abc-123-def-456
```

---

## Next Steps

1. Copy `models/pipeline_run.py` from above
2. Copy storage helpers and query interface
3. Update `main.py` to use `PipelineRun`
4. Test with: `python main.py octavehq.com sendoso.com`
5. Query results: `python scripts/query_runs.py --costs`

**Related**: [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) | [STORAGE_STRATEGIES.md](./STORAGE_STRATEGIES.md) | [USE_CASES.md](./USE_CASES.md)
