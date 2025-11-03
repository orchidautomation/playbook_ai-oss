# Use Cases - Real-World Applications

**Purpose**: Demonstrate the practical value of comprehensive pipeline data capture with concrete examples.

---

## 1. Debugging Pipeline Failures

### Scenario
A pipeline run fails during Phase 2, but you don't know which specialist agent caused the problem.

### Without Full Telemetry ❌
```
Error: Phase 2 failed
Status: 500 Internal Server Error
```

You have no visibility into:
- Which URLs were scraped
- Which specialist failed
- What the AI actually saw
- What error occurred

### With Full Telemetry ✅
```python
# Load the failed run
from utils.storage_helpers import load_pipeline_run

run = load_pipeline_run("abc-123-def")

# Check Phase 1 output
print(f"URLs scraped: {run.phase1_output.vendor_batch_content.page_count}")
print(f"Failed URLs: {run.phase1_output.vendor_batch_content.failed_urls}")

# Check errors
for error in run.errors:
    print(f"  Phase: {error['phase']}")
    print(f"  Step: {error['step']}")
    print(f"  Message: {error['message']}")

# Output:
#   Phase: phase2
#   Step: extract_case_studies
#   Message: No valid JSON returned from GPT-4o
```

**Result**: You know exactly which specialist failed and can debug the prompt.

---

## 2. Why Did URL Prioritization Select Only 5 URLs?

### Scenario
You expect 15 prioritized URLs, but only 5 were selected.

### Without Full Telemetry ❌
You can't answer:
- What URLs were evaluated?
- What were their priority scores?
- Why were some URLs rejected?

### With Full Telemetry ✅
```python
run = load_pipeline_run("abc-123-def")

# Inspect URL prioritization
prio = run.phase1_output.vendor_url_prioritization

print(f"URLs evaluated: {prio.total_urls_evaluated}")  # 94
print(f"URLs selected: {prio.urls_selected}")  # 5

# See the reasoning
for url_data in prio.prioritized_urls:
    print(f"{url_data.priority_score:.1f} | {url_data.url}")
    print(f"  Reasoning: {url_data.reasoning}")

# Output:
#   9.5 | https://vendor.com/about
#     Reasoning: Core company information
#   8.2 | https://vendor.com/customers
#     Reasoning: Customer proof points
#   ... (only 5 URLs had score > 8.0)
```

**Result**: You discover the AI's priority threshold was too high. Adjust the prompt to lower the bar.

---

## 3. Cost Optimization

### Scenario
Your pipeline costs are increasing. Which phase is most expensive?

### Without Full Telemetry ❌
- No per-phase cost tracking
- Can't identify bottlenecks
- Can't optimize expensive steps

### With Full Telemetry ✅
```python
# Analyze costs across all runs
from utils.query_interface import get_cost_summary

summary = get_cost_summary(since_date="2025-11-01")

print(f"Total runs: {summary['total_runs']}")
print(f"Avg cost per run: ${summary['avg_cost']:.2f}")
print(f"Total tokens: {summary['total_tokens']:,}")

# Drill into specific run
run = load_pipeline_run("abc-123")

# Add per-phase tracking (future enhancement)
print("\nCost by phase:")
print(f"  Phase 1 (scraping): $0.05")
print(f"  Phase 2 (8 specialists): $0.12")  # Most expensive!
print(f"  Phase 3 (3 analysts): $0.04")
print(f"  Phase 4 (playbook): $0.07")
```

**Result**: Phase 2 is the bottleneck. Optimize prompts or reduce specialist count.

---

## 4. Replay Phase 2-4 Without Re-Scraping

### Scenario
You improved the Phase 2 prompts and want to re-run analysis on existing data.

### Without Full Telemetry ❌
Must re-scrape everything (costs time + money):
```bash
python main.py octavehq.com sendoso.com  # Full pipeline
```

### With Full Telemetry ✅
```python
# Load Phase 1 data from previous run
previous_run = load_pipeline_run("abc-123")
phase1_data = previous_run.phase1_output

# Create new workflow starting at Phase 2
from workflow import phase2_3_4_workflow

new_result = phase2_3_4_workflow.run(
    input=phase1_data.model_dump()
)

# Save as new run
new_run = PipelineRun(
    workflow_input=previous_run.workflow_input,
    phase1_output=phase1_data,  # Reuse!
    phase2_output=extract_phase2(new_result),
    # ... etc
)
```

**Result**: Save $0.05 per run by skipping Phase 1 scraping. 100 replays = $5 saved.

---

## 5. Analytics: Which Pain Points Are Most Common?

### Scenario
You want to know which prospect pain points appear most frequently across all runs.

### Without Full Telemetry ❌
- No way to query across runs
- Manual inspection of JSON files

### With Full Telemetry ✅
```sql
-- SQLite query
SELECT
    json_extract(pain_points_json, '$[*].description') as pain_point,
    COUNT(*) as frequency
FROM prospect_intelligence
WHERE pain_points_json LIKE '%operational%'
GROUP BY pain_point
ORDER BY frequency DESC
LIMIT 10;
```

Or Python:
```python
from utils.storage_helpers import *
import sqlite3

conn = sqlite3.connect('output/octave.db')
cursor = conn.cursor()

# Get all pain points
cursor.execute("""
    SELECT pr.prospect_domain, pi.pain_points_json
    FROM prospect_intelligence pi
    JOIN pipeline_runs pr ON pi.run_id = pr.id
""")

pain_points = []
for prospect, pain_json in cursor.fetchall():
    pain_data = json.loads(pain_json)
    for p in pain_data:
        pain_points.append(p['description'])

# Count frequency
from collections import Counter
top_pains = Counter(pain_points).most_common(10)

for pain, count in top_pains:
    print(f"{count:3d}x | {pain}")

# Output:
#   25x | Low cold outreach response rates
#   18x | Difficulty proving ROI to stakeholders
#   15x | Manual personalization at scale
```

**Result**: Discover patterns across all prospects. Use for content marketing, product roadmap.

---

## 6. A/B Testing Email Prompt Strategies

### Scenario
You have two different prompts for generating email sequences. Which performs better?

### Without Full Telemetry ❌
- No systematic comparison
- Subjective assessment

### With Full Telemetry ✅
```python
# Run 10 playbooks with Prompt A
for i in range(10):
    run_workflow(vendor, prospect, email_prompt="A", tags=["prompt-A"])

# Run 10 playbooks with Prompt B
for i in range(10):
    run_workflow(vendor, prospect, email_prompt="B", tags=["prompt-B"])

# Compare results
def analyze_email_quality(run_id):
    run = load_pipeline_run(run_id)
    sequences = run.phase4_output.sales_playbook.email_sequences

    metrics = {
        "avg_subject_length": ...,
        "avg_body_length": ...,
        "has_personalization_tokens": ...,
        "cta_clarity_score": ...
    }
    return metrics

# Query by tag
prompt_a_runs = query_runs_by_tag("prompt-A")
prompt_b_runs = query_runs_by_tag("prompt-B")

# Compare
for run_id in prompt_a_runs:
    metrics = analyze_email_quality(run_id)
    # ... aggregate metrics

# Output:
#   Prompt A: Avg subject length 62 chars, CTA clarity 7.5/10
#   Prompt B: Avg subject length 48 chars, CTA clarity 8.8/10
#   Winner: Prompt B
```

**Result**: Data-driven prompt optimization. Ship the better prompt.

---

## 7. Quality Monitoring Over Time

### Scenario
Track playbook quality metrics as you improve the system.

### Without Full Telemetry ❌
- No baseline to compare against
- Can't measure improvements

### With Full Telemetry ✅
```python
# Weekly quality report
from datetime import datetime, timedelta

def calculate_quality_metrics(run: PipelineRun) -> dict:
    playbook = run.phase4_output.sales_playbook

    return {
        "email_count": len(playbook.email_sequences),
        "avg_email_word_count": ...,
        "has_all_personas": len(playbook.priority_personas) >= 3,
        "battle_card_completeness": len(playbook.battle_cards) / 3,
        "execution_time": run.execution_time_seconds,
        "cost": run.estimated_cost_usd
    }

# Get runs from last week
last_week = datetime.now() - timedelta(days=7)
recent_runs = query_runs_since(last_week)

# Calculate metrics
weekly_metrics = [calculate_quality_metrics(load_pipeline_run(r)) for r in recent_runs]

# Report
print("Weekly Quality Report:")
print(f"  Runs: {len(weekly_metrics)}")
print(f"  Avg emails per playbook: {sum(m['email_count'] for m in weekly_metrics) / len(weekly_metrics):.1f}")
print(f"  Persona coverage: {sum(m['has_all_personas'] for m in weekly_metrics) / len(weekly_metrics) * 100:.0f}%")
print(f"  Avg execution time: {sum(m['execution_time'] for m in weekly_metrics) / len(weekly_metrics):.1f}s")
```

**Result**: Track improvements week-over-week. Demonstrate system is getting better.

---

## 8. Customer Support: "Why Did My Playbook Look Like This?"

### Scenario
A customer asks why their playbook only had 2 email sequences instead of 3.

### Without Full Telemetry ❌
"🤷 Not sure, can you run it again?"

### With Full Telemetry ✅
```python
# Customer provides run ID
run = load_pipeline_run(customer_run_id)

# Investigate
phase3 = run.phase3_output.prospect_intelligence

print(f"Buyer personas identified: {len(phase3.target_buyer_personas)}")
for persona in phase3.target_buyer_personas:
    print(f"  - {persona.persona_title} (priority: {persona.priority_score})")

# Output:
#   Buyer personas identified: 2
#   - VP of Sales (priority: 9)
#   - CMO (priority: 7)
#   (Only 2 personas identified in Phase 3, so only 2 email sequences generated)

# Check why only 2 personas
print("\nProspect content analyzed:")
print(f"  Pages scraped: {run.phase1_output.prospect_batch_content.page_count}")
print(f"  Content chars: {run.phase1_output.prospect_batch_content.total_chars}")

# If low content...
if run.phase1_output.prospect_batch_content.page_count < 10:
    print("❗ Issue: Not enough content scraped for prospect")
    print(f"  URLs selected: {run.phase1_output.prospect_url_prioritization.urls_selected}")
```

**Result**: Root cause identified. Provide actionable feedback to customer.

---

## 9. Competitive Intelligence

### Scenario
Track which competitors appear most frequently in battle cards.

### Without Full Telemetry ❌
- No aggregation across runs
- Manual analysis

### With Full Telemetry ✅
```python
# Query all battle cards
conn = sqlite3.connect('output/octave.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT card_json FROM battle_cards
    WHERE card_type = 'competitive_positioning'
""")

competitors = []
for (card_json,) in cursor.fetchall():
    card = json.loads(card_json)
    for positioning in card.get('competitive_positioning', []):
        if positioning.get('competitor_name'):
            competitors.append(positioning['competitor_name'])

# Count
from collections import Counter
top_competitors = Counter(competitors).most_common(10)

print("Most Common Competitors:")
for competitor, count in top_competitors:
    print(f"  {count:3d}x | {competitor}")

# Output:
#   15x | Manual Processes
#   12x | HubSpot
#   8x  | Salesforce
#   5x  | In-house Solutions
```

**Result**: Product/marketing insights. Know your competitive landscape.

---

## 10. Automated Playbook Quality Scoring

### Scenario
Automatically score playbooks and flag low-quality outputs for review.

### Without Full Telemetry ❌
- Manual review of every playbook
- Subjective quality assessment

### With Full Telemetry ✅
```python
def score_playbook_quality(run: PipelineRun) -> float:
    """Return quality score 0-100"""
    score = 0
    playbook = run.phase4_output.sales_playbook

    # Email quality (40 points)
    if len(playbook.email_sequences) >= 3:
        score += 20
    if all(len(seq.touches) == 4 for seq in playbook.email_sequences):
        score += 10
    if all(len(t.body) > 100 for seq in playbook.email_sequences for t in seq.touches):
        score += 10

    # Battle card quality (30 points)
    if len(playbook.battle_cards) >= 3:
        score += 15
    if any(len(bc.competitive_positioning) > 0 for bc in playbook.battle_cards):
        score += 15

    # Persona coverage (30 points)
    if len(playbook.priority_personas) >= 3:
        score += 15
    if len(playbook.quick_wins) >= 5:
        score += 15

    return score

# Score all runs
for run_id in recent_runs:
    run = load_pipeline_run(run_id)
    quality_score = score_playbook_quality(run)

    if quality_score < 70:
        print(f"⚠️  Low quality playbook: {run_id[:8]} (score: {quality_score})")
        # Flag for human review
```

**Result**: Automated quality control. Focus human review on problematic outputs.

---

## Summary: Value Proposition

| Use Case | Time Saved | Cost Saved | Insight Value |
|----------|------------|------------|---------------|
| Debugging failures | Hours → Minutes | N/A | High |
| URL prioritization analysis | N/A | N/A | Medium |
| Cost optimization | N/A | 10-20% | High |
| Replay without re-scraping | N/A | $0.05/run | Medium |
| Pain point analytics | Days → Seconds | N/A | High |
| A/B testing prompts | Weeks → Days | N/A | Very High |
| Quality monitoring | N/A | N/A | High |
| Customer support | Hours → Minutes | N/A | Medium |
| Competitive intelligence | N/A | N/A | Medium |
| Automated quality scoring | N/A | N/A | High |

**Total Value**: Debugging + Analytics + Optimization + Quality Control

---

## Next Steps

1. **Implement models**: [CODE_EXAMPLES.md](./CODE_EXAMPLES.md)
2. **Follow roadmap**: [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)
3. **Choose storage**: [STORAGE_STRATEGIES.md](./STORAGE_STRATEGIES.md)
4. **Start with Phase 1**: Capture basic pipeline data

**Related**: [README.md](./README.md) | [PIPELINE_RUN_MODEL.md](./PIPELINE_RUN_MODEL.md) | [PHASE_MODELS_DETAILED.md](./PHASE_MODELS_DETAILED.md)
