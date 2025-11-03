# Data Models - Future Enhancement Documentation

**Status**: 📋 Planning Phase
**Priority**: Medium
**Effort**: 2-3 weeks
**Impact**: High (enables analytics, debugging, cost tracking, quality monitoring)

---

## 🎯 Vision

Transform the Octave Clone pipeline from "output-only" to "full pipeline telemetry" by capturing **all intermediary data** at every step, not just the final sales playbook output.

Currently, we only persist the final Phase 4 output (`sales_playbook` in `output/output.txt`). We lose all the rich intermediary data generated during:
- Phase 1: Domain validation, homepage analysis, URL prioritization
- Phase 2: Individual specialist extractions (8 agents)
- Phase 3: Individual analyst outputs (3 agents)
- Phase 4: Individual playbook specialist outputs (4 agents)

This documentation defines a comprehensive data model for capturing and storing **everything** the pipeline generates.

---

## 📊 Current State vs. Future State

### Current State (Output-Only)
```
Input: octavehq.com + sendoso.com
         ↓
    [Black Box]
    12 steps
    19 AI agents
         ↓
Output: sales_playbook.json
```

**What We Lose:**
- ❌ Can't debug why a step failed
- ❌ Can't analyze which URLs were prioritized
- ❌ Can't track AI costs per step
- ❌ Can't re-run Phase 2-4 without re-scraping
- ❌ Can't query "Show me all prospects with 'ROI proof' pain points"
- ❌ Can't compare playbook quality over time

### Future State (Full Telemetry)
```
Input: WorkflowInput
         ↓
Phase 1: DomainValidation, HomepageContent, URLPrioritization, BatchContent
         ↓
Phase 2: VendorElements (8 specialists)
         ↓
Phase 3: ProspectIntelligence (3 analysts)
         ↓
Phase 4: SalesPlaybook (4 specialists)
         ↓
Output: PipelineRun (complete data model)
```

**What We Gain:**
- ✅ Complete audit trail of every step
- ✅ Debug exactly where/why failures occur
- ✅ Replay Phase 2-4 without re-scraping (save $)
- ✅ Track AI costs per step/agent
- ✅ Query analytics: "Which prospects care about personalization?"
- ✅ A/B test different prompts and compare results
- ✅ Monitor playbook quality metrics over time

---

## 📚 Documentation Index

### Core Specifications

1. **[PIPELINE_RUN_MODEL.md](./PIPELINE_RUN_MODEL.md)** - Master Data Model
   - Complete `PipelineRun` Pydantic model
   - All Phase 1-4 intermediary models
   - Field-by-field documentation
   - Example JSON output structure

2. **[PHASE_MODELS_DETAILED.md](./PHASE_MODELS_DETAILED.md)** - Phase-by-Phase Breakdown
   - Phase 1 intermediary models (5 steps)
   - Phase 2 VendorElements (reference)
   - Phase 3 ProspectIntelligence (reference)
   - Phase 4 SalesPlaybook (reference)
   - Data flow diagrams

### Implementation Planning

3. **[STORAGE_STRATEGIES.md](./STORAGE_STRATEGIES.md)** - Storage Options
   - JSON File System (current approach)
   - SQLite Database (recommended)
   - PostgreSQL (enterprise scale)
   - Hybrid Approach (JSON + SQLite) ⭐ **Recommended**
   - Complete SQL schemas and query examples

4. **[IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)** - Build Plan
   - 4-phase implementation timeline
   - Code changes required per phase
   - Testing strategy
   - Rollout plan

5. **[CODE_EXAMPLES.md](./CODE_EXAMPLES.md)** - Implementation Code
   - Complete `models/pipeline_run.py` file
   - Workflow modifications for data capture
   - Hybrid storage implementation
   - Query interface examples

### Applications

6. **[USE_CASES.md](./USE_CASES.md)** - Why This Matters
   - Debugging and error tracing
   - Analytics and insights
   - Cost optimization
   - Quality monitoring
   - A/B testing prompts

---

## 🚀 Quick Start (When Ready to Implement)

### 1. Read Core Docs
Start with these three in order:
1. [PIPELINE_RUN_MODEL.md](./PIPELINE_RUN_MODEL.md) - Understand the data structure
2. [STORAGE_STRATEGIES.md](./STORAGE_STRATEGIES.md) - Choose storage approach
3. [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) - Plan the build

### 2. Phase 1 Implementation (Week 1)
- Copy code from [CODE_EXAMPLES.md](./CODE_EXAMPLES.md)
- Create `models/pipeline_run.py`
- Add `run_id` (UUID) to workflow execution
- Save complete JSON after each run

### 3. Phase 2-4 (Weeks 2-4)
Follow the detailed roadmap in [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)

---

## 💡 Key Benefits

### For Developers
- **Debugging**: See exactly what happened at each step
- **Testing**: Compare outputs across different prompt versions
- **Performance**: Identify bottlenecks and expensive operations

### For Product
- **Analytics**: "Which personas are most common?" "Which pain points drive engagement?"
- **Quality**: Monitor playbook quality metrics over time
- **Cost**: Track spend per phase/step/agent

### For Business
- **ROI**: Replay analysis without re-scraping (save API costs)
- **Insights**: Aggregate learnings across all pipeline runs
- **Compliance**: Complete audit trail for every generated playbook

---

## 📈 Success Metrics (Post-Implementation)

After implementing this data model, we should be able to:

1. ✅ Query: "Show me all pipeline runs for prospects in 'B2B SaaS' industry"
2. ✅ Debug: "Why did URL prioritization select only 5 URLs instead of 15?"
3. ✅ Optimize: "Which AI agent uses the most tokens?"
4. ✅ Replay: "Re-run Phase 2-4 using cached Phase 1 data"
5. ✅ Compare: "Did the new prompt improve email open rate predictions?"
6. ✅ Monitor: "What's the average playbook generation cost this month?"

---

## 🗂️ Related Documentation

- [Main README](../../README.md) - Project overview
- [API Serving Guide](../../docs/API_SERVING_GUIDE.md) - AgentOS integration
- [Architecture](../../docs/developers/ARCHITECTURE.md) - System architecture
- [Phase 4 Completion Summary](../../docs/phases/PHASE4_COMPLETION_SUMMARY.md) - Latest milestone

---

## 📝 Changelog

- **2025-11-02**: Initial documentation created based on comprehensive data model analysis
- **Future**: Implementation tracking will be added here

---

## 🤝 Contributing

When implementing these models:

1. **Follow Pydantic conventions**: Use Field() for descriptions, default_factory for lists/dicts
2. **Add source attribution**: Every extracted data point should reference its source URL
3. **Keep models flat**: Avoid deep nesting (max 3 levels)
4. **Use timestamps**: Every phase/step should record when it executed
5. **Fail gracefully**: Optional fields should have sensible defaults

---

**Ready to build?** Start with [PIPELINE_RUN_MODEL.md](./PIPELINE_RUN_MODEL.md) →
