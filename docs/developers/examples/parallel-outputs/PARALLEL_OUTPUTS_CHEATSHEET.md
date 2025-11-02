# Agno Parallel Outputs - Quick Reference Cheatsheet

## 🎯 Basic Pattern

```python
from agno.workflow import Parallel, Step, Workflow
from agno.workflow.types import StepInput, StepOutput

# Pattern: Parallel Steps → Python Processing → LLM Summary
workflow = Workflow(
    steps=[
        Parallel(step1, step2, step3, name="Parallel Phase"),
        python_processing_step,
        llm_summary_step
    ]
)
```

## 📥 Accessing Parallel Outputs

### Get Specific Parallel Step Results
```python
def process_parallel(step_input: StepInput) -> StepOutput:
    # Returns dict: {"step1_name": "output1", "step2_name": "output2"}
    results = step_input.get_step_content("Parallel Phase")

    step1_output = results.get("step1_name", "")
    step2_output = results.get("step2_name", "")

    return StepOutput(content="processed data")
```

### Get All Previous Content
```python
def aggregate_all(step_input: StepInput) -> StepOutput:
    # Returns all previous content as single string
    all_content = step_input.get_all_previous_content()
    return StepOutput(content=f"Aggregated: {all_content}")
```

### Get Original Workflow Input
```python
def use_original_query(step_input: StepInput) -> StepOutput:
    original_query = step_input.input
    return StepOutput(content=f"Query was: {original_query}")
```

## 🔄 StepInput Methods Quick Ref

| Method | Returns | Use Case |
|--------|---------|----------|
| `.input` | `str` | Original workflow input |
| `.previous_step_content` | `str` | Last step's output |
| `.get_step_content("name")` | `str \| dict` | Specific step output |
| `.get_all_previous_content()` | `str` | All previous outputs |

**Note:** For Parallel steps, `get_step_content()` returns a **dict** with step names as keys.

## ✅ Fail-Fast Validation Pattern

```python
def validate_data(step_input: StepInput) -> StepOutput:
    parallel_results = step_input.get_step_content("Research Phase")

    if not parallel_results:
        return StepOutput(
            content="❌ Validation failed - no data",
            stop=True  # Stops workflow immediately
        )

    # Check data quality
    for name, content in parallel_results.items():
        if len(content) < 100:
            return StepOutput(
                content=f"❌ {name} insufficient data",
                stop=True
            )

    return StepOutput(content="✅ Validation passed")
```

## 🏗️ Common Workflow Patterns

### Pattern 1: Multi-Source Research
```python
workflow = Workflow(steps=[
    Parallel(hn_research, web_research, academic_research, name="Research"),
    extract_metrics_step,      # Python: process parallel outputs
    summarize_step             # LLM: create final summary
])
```

### Pattern 2: Quality-Controlled Pipeline
```python
workflow = Workflow(steps=[
    Parallel(source1, source2, source3, name="Collection"),
    validate_step,             # Python: fail-fast validation
    structure_step,            # Python: prepare for LLM
    synthesis_step             # LLM: final report
])
```

### Pattern 3: Intelligence Gathering
```python
workflow = Workflow(steps=[
    Parallel(tech, market, competitor, name="Intelligence"),
    quality_check_step,        # Python: validation
    brief_step,                # Python: structure brief
    strategic_analysis_step    # LLM: executive summary
])
```

## 🎨 Creating Steps

### Agent Step (LLM)
```python
from agno.agent import Agent

researcher = Agent(
    name="Researcher",
    instructions="Research instructions...",
    tools=[SomeTool()],
    markdown=True
)

step = Step(name="Research", agent=researcher)
```

### Python Function Step
```python
def my_function(step_input: StepInput) -> StepOutput:
    # Access data
    data = step_input.get_step_content("PreviousStep")

    # Process
    result = process(data)

    # Return
    return StepOutput(content=result, success=True)

step = Step(name="Process", executor=my_function)
```

## 🚀 Running Workflows

```python
# Simple execution
workflow.print_response("your query here")

# Streaming execution
workflow.print_response(
    input="your query",
    stream=True,
    stream_events=True,
    markdown=True
)

# With session
workflow.print_response(
    input="your query",
    session_id="my-session-123"
)
```

## 💡 Pro Tips

1. **Always name your steps** - Makes accessing outputs easier
2. **Use fail-fast validation** - Stop workflow early if data is bad
3. **Prepare data for LLMs** - Structure outputs optimally for synthesis
4. **Leverage parallelism** - Only for independent tasks
5. **Check parallel dict keys** - Match exact step names

## 🎓 Examples

- `parallel_outputs_example.py` - Basic parallel + LLM summary
- `parallel_outputs_advanced.py` - Advanced with validation & intelligence brief
- `PARALLEL_OUTPUTS_GUIDE.md` - Comprehensive guide

---

**Quick Start:**
```bash
python parallel_outputs_example.py        # Basic example
python parallel_outputs_advanced.py       # Advanced example
```
