# Agno Parallel Outputs - Complete Example Collection

This collection demonstrates how to use **Agno's parallel execution** to run multiple steps simultaneously, then aggregate and summarize their results using both Python functions and LLM agents.

## 📁 Files in This Collection

| File | Level | Description |
|------|-------|-------------|
| `parallel_outputs_simple.py` | ⭐ Beginner | Start here! Simplest example: 2 parallel agents → LLM summary |
| `parallel_outputs_example.py` | ⭐⭐ Intermediate | Parallel agents → Python processing → LLM summary |
| `parallel_outputs_advanced.py` | ⭐⭐⭐ Advanced | Multi-source intelligence with validation & structured brief |
| `PARALLEL_OUTPUTS_GUIDE.md` | 📖 | Comprehensive guide with patterns and best practices |
| `PARALLEL_OUTPUTS_CHEATSHEET.md` | 📋 | Quick reference for common operations |
| `PARALLEL_OUTPUTS_VISUAL.md` | 🎨 | Visual diagrams showing data flow |

## 🚀 Quick Start

### 1. Start with the Simple Example
```bash
python parallel_outputs_simple.py
```

This shows the basic pattern:
```python
Parallel(agent1, agent2) → LLM Summary
```

### 2. Add Python Processing
```bash
python parallel_outputs_example.py
```

This demonstrates:
```python
Parallel(agent1, agent2) → Python Function → LLM Summary
```

### 3. Advanced Intelligence Pipeline
```bash
python parallel_outputs_advanced.py
```

Full pattern with validation:
```python
Parallel(source1, source2, source3) → Validate → Structure → LLM Synthesis
```

## 🎯 What You'll Learn

### Core Concepts
- ✅ Running multiple agents in parallel
- ✅ Accessing parallel outputs in Python functions
- ✅ Passing aggregated data to LLM agents
- ✅ Creating final summaries from multiple sources

### Advanced Techniques
- ✅ Fail-fast validation patterns
- ✅ Structured data preparation for LLMs
- ✅ Multi-source intelligence gathering
- ✅ Quality control in workflows

## 📖 Documentation

### Quick Reference
See `PARALLEL_OUTPUTS_CHEATSHEET.md` for:
- StepInput methods reference
- Common patterns
- Code snippets
- Pro tips

### Comprehensive Guide
See `PARALLEL_OUTPUTS_GUIDE.md` for:
- Detailed explanations
- Best practices
- Troubleshooting
- Real-world applications

### Visual Learning
See `PARALLEL_OUTPUTS_VISUAL.md` for:
- Workflow diagrams
- Data flow visualization
- Pattern comparisons

## 🔑 Key Patterns

### Pattern 1: Basic Parallel Summary
**Use Case:** Multi-source research with LLM synthesis

```python
workflow = Workflow(steps=[
    Parallel(research1, research2),
    llm_summary
])
```

**Example:** `parallel_outputs_simple.py`

### Pattern 2: Parallel + Python + LLM
**Use Case:** Research with metrics and final summary

```python
workflow = Workflow(steps=[
    Parallel(research1, research2),
    python_processing,  # Compute metrics, structure data
    llm_summary
])
```

**Example:** `parallel_outputs_example.py`

### Pattern 3: Intelligence Pipeline
**Use Case:** Quality-controlled multi-source intelligence

```python
workflow = Workflow(steps=[
    Parallel(source1, source2, source3),
    validate_quality,   # Fail-fast if insufficient
    structure_brief,    # Prepare for LLM
    llm_synthesis
])
```

**Example:** `parallel_outputs_advanced.py`

## 💡 Real-World Applications

### Sales Intelligence (like your Lotus workflow)
```python
Parallel(
    company_research,
    linkedin_search,
    news_scraping
) → validate_data → extract_entities → llm_strategic_brief
```

### Content Research
```python
Parallel(
    hackernews_research,
    web_research,
    academic_search
) → compute_metrics → llm_article_writer
```

### Competitive Analysis
```python
Parallel(
    competitor1_research,
    competitor2_research,
    competitor3_research
) → create_comparison_matrix → llm_strategic_analysis
```

## 🎓 Learning Path

1. **Beginner** → Run `parallel_outputs_simple.py`
   - Understand parallel execution
   - See how LLM receives multiple outputs

2. **Intermediate** → Run `parallel_outputs_example.py`
   - Learn to access parallel outputs in Python
   - Compute metrics and structure data
   - Prepare data for LLM synthesis

3. **Advanced** → Run `parallel_outputs_advanced.py`
   - Implement fail-fast validation
   - Create structured intelligence briefs
   - Build production-ready pipelines

4. **Reference** → Use the cheatsheet and guide
   - Quick lookups while coding
   - Best practices
   - Troubleshooting

## 🔧 Common Operations

### Accessing Parallel Outputs
```python
def process_parallel(step_input: StepInput) -> StepOutput:
    # Get dict: {"Step1": "output1", "Step2": "output2"}
    results = step_input.get_step_content("Parallel Phase")

    step1_output = results.get("Step1", "")
    step2_output = results.get("Step2", "")

    return StepOutput(content="processed")
```

### Getting All Previous Content
```python
def aggregate_all(step_input: StepInput) -> StepOutput:
    # Get everything as single string
    all_content = step_input.get_all_previous_content()
    return StepOutput(content=all_content)
```

### Fail-Fast Validation
```python
def validate(step_input: StepInput) -> StepOutput:
    data = step_input.get_step_content("Research")

    if not meets_threshold(data):
        return StepOutput(
            content="❌ Validation failed",
            stop=True  # Stops workflow
        )

    return StepOutput(content="✅ Valid")
```

## 🎯 When to Use Parallel Execution

### ✅ Good Use Cases
- Multi-source research (different APIs/tools)
- Independent data collection tasks
- Parallel analysis of same data with different approaches
- Competitive research across multiple companies

### ❌ Not Recommended
- Sequential dependencies (step 2 needs step 1's output)
- Single source with sequential processing
- Tasks that share state

## 🛠️ Requirements

```bash
pip install agno
```

Set your API keys:
```bash
export OPENAI_API_KEY="your-key-here"
# or
export ANTHROPIC_API_KEY="your-key-here"
```

## 📚 Additional Resources

- [Agno Documentation](https://docs.agno.com)
- [Parallel Steps Guide](https://docs.agno.com/examples/concepts/workflows/04-workflows-parallel-execution/parallel_steps_workflow)
- [Accessing Previous Steps](https://docs.agno.com/examples/concepts/workflows/06_workflows_advanced_concepts/access_multiple_previous_steps_output)

## 💬 Questions?

- Check `PARALLEL_OUTPUTS_CHEATSHEET.md` for quick answers
- Read `PARALLEL_OUTPUTS_GUIDE.md` for detailed explanations
- See `PARALLEL_OUTPUTS_VISUAL.md` for visual diagrams

---

**Happy Building!** 🚀

Created with [Agno Workflows 2.0](https://docs.agno.com)
