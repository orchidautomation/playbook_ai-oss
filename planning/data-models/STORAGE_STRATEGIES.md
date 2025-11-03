# Storage Strategies - Persistence Options Comparison

**Purpose**: Compare storage approaches for persisting complete pipeline data with pros/cons and implementation guidance.

---

## TL;DR Recommendation

**🎯 Hybrid Approach (Option 4)** - JSON + SQLite
- Save complete `PipelineRun` as JSON (full fidelity, easy debugging)
- Index key fields in SQLite (fast queries, analytics)
- Best of both worlds with minimal complexity

---

## Option 1: JSON File System (Current Approach)

### Description
Save complete `PipelineRun` model as JSON files in `output/runs/` directory.

### Implementation
```python
# Save
run = PipelineRun(...)
json_path = f"output/runs/{run.run_id}.json"
with open(json_path, 'w') as f:
    f.write(run.model_dump_json(indent=2))

# Load
with open(json_path, 'r') as f:
    data = json.load(f)
    run = PipelineRun(**data)
```

### Directory Structure
```
output/
├── runs/
│   ├── 2025-11-02_octave-sendoso_abc123.json
│   ├── 2025-11-02_octave-gong_def456.json
│   └── 2025-11-03_octave-salesloft_ghi789.json
└── index.json  # Metadata for all runs
```

### Pros ✅
- **Simple**: No database, no setup, works immediately
- **Debuggable**: Human-readable JSON, easy to inspect
- **Version control**: Can commit JSON files to git
- **Portable**: Works on any system, no dependencies

### Cons ❌
- **No querying**: Can't run SQL queries like "show all runs for Sendoso"
- **Performance**: Slow to scan 1000+ files
- **No relationships**: Can't join data across runs
- **No indexing**: Linear search through all files

### When to Use
- MVP/prototyping phase
- < 100 pipeline runs
- Single user, no concurrent access
- Don't need advanced analytics

### Estimated Capacity
- **100 runs**: 50 MB, scan time ~1s
- **1,000 runs**: 500 MB, scan time ~10s
- **10,000 runs**: 5 GB, scan time ~100s ❌ Too slow

---

## Option 2: SQLite Database (Recommended for Production)

### Description
Store pipeline data in SQLite database with normalized tables.

### Complete SQL Schema

```sql
-- Core pipeline runs table
CREATE TABLE pipeline_runs (
    id TEXT PRIMARY KEY,  -- UUID
    vendor_domain TEXT NOT NULL,
    prospect_domain TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('running', 'completed', 'failed', 'partial')),
    run_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    execution_time_seconds REAL,
    total_api_calls INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    estimated_cost_usd REAL,
    created_by TEXT,
    created_via TEXT DEFAULT 'CLI' CHECK(created_via IN ('CLI', 'API')),
    notes TEXT
);

CREATE INDEX idx_runs_vendor ON pipeline_runs(vendor_domain);
CREATE INDEX idx_runs_prospect ON pipeline_runs(prospect_domain);
CREATE INDEX idx_runs_timestamp ON pipeline_runs(run_timestamp DESC);
CREATE INDEX idx_runs_status ON pipeline_runs(status);

-- Phase 1: Domain validations
CREATE TABLE domain_validations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    company_type TEXT NOT NULL CHECK(company_type IN ('vendor', 'prospect')),
    domain TEXT NOT NULL,
    urls_discovered_json TEXT,  -- JSON array
    url_count INTEGER,
    map_timestamp TIMESTAMP,
    validation_status TEXT,
    error_message TEXT
);

CREATE INDEX idx_validations_run ON domain_validations(run_id);

-- Phase 1: Homepage content
CREATE TABLE homepage_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    company_type TEXT NOT NULL CHECK(company_type IN ('vendor', 'prospect')),
    url TEXT NOT NULL,
    markdown_content TEXT,
    char_count INTEGER,
    word_count INTEGER,
    scrape_timestamp TIMESTAMP,
    metadata_json TEXT
);

-- Phase 1: Prioritized URLs
CREATE TABLE prioritized_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    company_type TEXT NOT NULL,
    url TEXT NOT NULL,
    priority_score REAL,
    reasoning TEXT,
    category TEXT
);

CREATE INDEX idx_prio_urls_run ON prioritized_urls(run_id);
CREATE INDEX idx_prio_urls_score ON prioritized_urls(priority_score DESC);

-- Phase 1: Batch scraped pages
CREATE TABLE batch_scraped_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    company_type TEXT NOT NULL,
    url TEXT NOT NULL,
    markdown_content TEXT,
    char_count INTEGER,
    scrape_timestamp TIMESTAMP
);

-- Phase 2: Vendor elements (store as JSON per element type)
CREATE TABLE vendor_elements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    element_type TEXT NOT NULL CHECK(element_type IN (
        'offering', 'case_study', 'proof_point', 'value_proposition',
        'reference_customer', 'use_case', 'persona', 'differentiator'
    )),
    data_json TEXT NOT NULL,  -- Complete Pydantic model as JSON
    extraction_timestamp TIMESTAMP
);

CREATE INDEX idx_vendor_elements_run ON vendor_elements(run_id);
CREATE INDEX idx_vendor_elements_type ON vendor_elements(element_type);

-- Phase 3: Prospect intelligence
CREATE TABLE prospect_intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL UNIQUE REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    company_profile_json TEXT,
    pain_points_json TEXT,
    buyer_personas_json TEXT,
    analysis_timestamp TIMESTAMP
);

-- Phase 4: Sales playbooks
CREATE TABLE sales_playbooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL UNIQUE REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    playbook_json TEXT NOT NULL,  -- Complete SalesPlaybook model
    generation_timestamp TIMESTAMP
);

-- Phase 4: Email sequences (for easy querying)
CREATE TABLE email_sequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    persona_title TEXT NOT NULL,
    sequence_name TEXT,
    total_touches INTEGER,
    sequence_json TEXT NOT NULL,  -- Complete EmailSequence model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email_seq_persona ON email_sequences(persona_title);

-- Phase 4: Battle cards
CREATE TABLE battle_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    card_type TEXT CHECK(card_type IN ('why_we_win', 'objection_handling', 'competitive_positioning')),
    title TEXT,
    card_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Error tracking
CREATE TABLE pipeline_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    phase TEXT,
    step TEXT,
    error_type TEXT,
    error_message TEXT,
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_errors_run ON pipeline_errors(run_id);
```

### Example Queries

```sql
-- Find all runs for a specific prospect
SELECT * FROM pipeline_runs
WHERE prospect_domain = 'https://sendoso.com'
ORDER BY run_timestamp DESC;

-- Get average execution time by status
SELECT status, AVG(execution_time_seconds) as avg_time, COUNT(*) as run_count
FROM pipeline_runs
GROUP BY status;

-- Find all prospects with "ROI proof" pain points
SELECT DISTINCT pr.prospect_domain, pi.pain_points_json
FROM pipeline_runs pr
JOIN prospect_intelligence pi ON pr.id = pi.run_id
WHERE pi.pain_points_json LIKE '%ROI proof%';

-- Track total costs over time
SELECT DATE(run_timestamp) as date,
       SUM(estimated_cost_usd) as daily_cost,
       COUNT(*) as runs_per_day
FROM pipeline_runs
WHERE status = 'completed'
GROUP BY DATE(run_timestamp)
ORDER BY date DESC;

-- Find which URLs get highest priority scores
SELECT url, AVG(priority_score) as avg_score, COUNT(*) as times_selected
FROM prioritized_urls
GROUP BY url
HAVING COUNT(*) > 3
ORDER BY avg_score DESC
LIMIT 20;

-- Get email sequences for CMO persona
SELECT pr.vendor_domain, pr.prospect_domain, es.sequence_json
FROM email_sequences es
JOIN pipeline_runs pr ON es.run_id = pr.id
WHERE es.persona_title = 'CMO'
ORDER BY es.created_at DESC;
```

### Pros ✅
- **Queryable**: Full SQL support for analytics
- **Fast**: Indexes make queries instant
- **Portable**: Single .db file, no server needed
- **Transactional**: ACID compliance
- **Built-in**: Python sqlite3 module included

### Cons ❌
- **More complex**: Need ORM or raw SQL
- **Schema migrations**: Changes require ALTER TABLE
- **Binary format**: Not human-readable (use SQLite Browser)

### When to Use
- 100+ pipeline runs
- Need analytics ("Show all runs for Sendoso")
- Multiple users querying data
- Production deployment

### Implementation (Python + SQLAlchemy)
```python
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class PipelineRunDB(Base):
    __tablename__ = 'pipeline_runs'
    id = Column(String, primary_key=True)
    vendor_domain = Column(String, nullable=False)
    prospect_domain = Column(String, nullable=False)
    # ... other fields

engine = create_engine('sqlite:///output/octave.db')
Base.metadata.create_all(engine)
```

---

## Option 3: PostgreSQL (Enterprise Scale)

### When to Use
- 10,000+ pipeline runs
- Multiple concurrent users
- Advanced analytics with BI tools (Metabase, Tableau)
- Cloud deployment (AWS RDS, GCP Cloud SQL)

### Pros ✅
- **Scalable**: Handles millions of runs
- **Concurrent**: Multiple users, connections
- **Advanced features**: Full-text search, JSON querying, views
- **Integrations**: Works with BI tools, data warehouses

### Cons ❌
- **Infrastructure**: Requires PostgreSQL server
- **Cost**: Database hosting costs
- **Overkill**: Too much for < 10,000 runs

### Setup (Docker)
```bash
docker run -d \
  --name octave-postgres \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=octave \
  -p 5432:5432 \
  -v octave-data:/var/lib/postgresql/data \
  postgres:15
```

### Schema
Same as SQLite, just change engine:
```python
engine = create_engine('postgresql://user:pass@localhost/octave')
```

---

## Option 4: Hybrid Approach (⭐ RECOMMENDED)

### Strategy
1. **Save complete JSON** (full fidelity, debugging)
2. **Index key fields in SQLite** (fast queries, analytics)

### Implementation

```python
import json
import sqlite3
from datetime import datetime
from models.pipeline_run import PipelineRun

def save_pipeline_run(run: PipelineRun):
    """Save pipeline run with hybrid storage"""

    # 1. Save complete JSON (full fidelity)
    json_path = f"output/runs/{run.run_id}.json"
    with open(json_path, 'w') as f:
        f.write(run.model_dump_json(indent=2))

    # 2. Index key fields in SQLite (fast queries)
    conn = sqlite3.connect('output/octave.db')
    cursor = conn.cursor()

    # Insert main run
    cursor.execute("""
        INSERT INTO pipeline_runs
        (id, vendor_domain, prospect_domain, status, run_timestamp,
         execution_time_seconds, total_api_calls, estimated_cost_usd)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run.run_id,
        run.workflow_input.vendor_domain,
        run.workflow_input.prospect_domain,
        run.status,
        run.run_timestamp,
        run.execution_time_seconds,
        run.total_api_calls,
        run.estimated_cost_usd
    ))

    # Index email sequences for fast persona lookups
    if run.phase4_output:
        for seq in run.phase4_output.sales_playbook.email_sequences:
            cursor.execute("""
                INSERT INTO email_sequences
                (run_id, persona_title, sequence_json)
                VALUES (?, ?, ?)
            """, (
                run.run_id,
                seq.persona_title,
                seq.model_dump_json()
            ))

    conn.commit()
    conn.close()

    print(f"✅ Saved run {run.run_id}")
    print(f"   JSON: {json_path}")
    print(f"   DB: output/octave.db")

def load_pipeline_run(run_id: str) -> PipelineRun:
    """Load complete pipeline run from JSON"""
    json_path = f"output/runs/{run_id}.json"
    with open(json_path, 'r') as f:
        data = json.load(f)
        return PipelineRun(**data)

def query_runs(prospect_domain: str) -> List[str]:
    """Fast query using SQLite index"""
    conn = sqlite3.connect('output/octave.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, vendor_domain, run_timestamp
        FROM pipeline_runs
        WHERE prospect_domain = ?
        ORDER BY run_timestamp DESC
    """, (prospect_domain,))
    return cursor.fetchall()
```

### Pros ✅
- **Best of both worlds**: JSON debugging + SQL queries
- **Flexible**: Can query fast, inspect JSON when needed
- **Incremental**: Start with JSON, add SQLite later
- **Recoverable**: If DB corrupts, have JSON backup

### Cons ❌
- **Duplication**: Data stored twice (JSON + DB)
- **Sync risk**: JSON and DB could drift if not careful

### Storage Overhead
- JSON: 500 KB per run
- SQLite index: ~50 KB per run (only key fields)
- Total: ~550 KB per run (10% overhead)

---

## Comparison Matrix

| Feature | JSON Only | SQLite | PostgreSQL | Hybrid |
|---------|-----------|--------|------------|--------|
| **Setup Complexity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Query Speed** | ❌ | ✅ | ✅✅ | ✅ |
| **Debugging** | ✅✅ | ⭐ | ⭐ | ✅✅ |
| **Scalability** | < 100 | < 10K | 100K+ | < 10K |
| **Portability** | ✅✅ | ✅✅ | ⭐⭐ | ✅✅ |
| **Cost** | Free | Free | $$ | Free |
| **Backup** | ✅✅ | ✅ | ✅ | ✅✅ |

---

## Recommendations

### For Different Scenarios

**Starting Out (MVP)**: Option 1 (JSON Only)
- Simple, works immediately
- Upgrade to Hybrid when you hit 50-100 runs

**Production (< 10K runs)**: Option 4 (Hybrid) ⭐
- Query performance when needed
- Full debugging capability
- Easy backup/restore

**Enterprise (10K+ runs)**: Option 3 (PostgreSQL)
- Proper database infrastructure
- BI tool integration
- Multi-user support

---

## Next Steps

1. **Choose strategy**: Hybrid recommended for most use cases
2. **Implement models**: See [CODE_EXAMPLES.md](./CODE_EXAMPLES.md)
3. **Follow roadmap**: See [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)
4. **Test queries**: Try the SQL examples above

---

**Related**: [PIPELINE_RUN_MODEL.md](./PIPELINE_RUN_MODEL.md) | [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) | [CODE_EXAMPLES.md](./CODE_EXAMPLES.md)
