# Agno Parallel Outputs - Complete Guide

This guide demonstrates how to use Agno's parallel execution capabilities to run multiple steps simultaneously, then aggregate their results with both Python functions and LLM agents.

## 📚 Examples Included

1. **`parallel_outputs_example.py`** - Basic pattern with parallel research + LLM summary
2. **`parallel_outputs_advanced.py`** - Advanced pattern with validation and structured intelligence

## 🎯 Key Concepts

### Parallel Execution Pattern

```python
from agno.workflow import Parallel, Step, Workflow

workflow = Workflow(
    steps=[
        # Multiple steps run simultaneously
        Parallel(
            step1,
            step2,
            step3,
            name="Parallel Phase"
        ),
        # Next step receives all parallel outputs
        processing_step,
        # Final step can be an LLM that summarizes everything
        summary_step
    ]
)
```

### Accessing Parallel Outputs

When you have parallel steps, you can access their outputs in subsequent steps:

#### Method 1: Access Specific Parallel Step by Name

```python
def process_parallel_outputs(step_input: StepInput) -> StepOutput:
    # Returns a dict with keys = individual step names
    parallel_results = step_input.get_step_content("Parallel Phase")

    # parallel_results structure:
    # {
    #     "step1_name": "output from step 1",
    #     "step2_name": "output from step 2",
    #     "step3_name": "output from step 3"
    # }

    step1_data = parallel_results.get("step1_name", "")
    step2_data = parallel_results.get("step2_name", "")

    # Process the data...
    return StepOutput(content=processed_data)
```

#### Method 2: Access All Previous Content

```python
def aggregate_everything(step_input: StepInput) -> StepOutput:
    # Gets ALL previous content as a single string
    all_content = step_input.get_all_previous_content()

    # Get original workflow input
    original_query = step_input.input

    return StepOutput(content=f"Query: {original_query}\n\n{all_content}")
```

#### Method 3: Access Original Workflow Input

```python
def use_original_input(step_input: StepInput) -> StepOutput:
    # Access the original message passed to workflow.run()
    original_message = step_input.input

    # Also access previous step content
    previous_content = step_input.previous_step_content

    return StepOutput(content=f"Original: {original_message}")
```

## 🚀 Example 1: Basic Parallel Research with LLM Summary

**File:** `parallel_outputs_example.py`

### Workflow Structure
```
┌─────────────────────────────────────────┐
│  Parallel Research Phase                │
│  ┌────────────┐    ┌────────────┐      │
│  │ HackerNews │    │    Web     │      │
│  │  Research  │    │  Research  │      │
│  └────────────┘    └────────────┘      │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  Extract Metrics (Python Function)      │
│  - Access parallel outputs by name      │
│  - Compute metrics                      │
│  - Prepare data for LLM                 │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  Final Summary (LLM Agent)              │
│  - Synthesize all findings              │
│  - Create comprehensive report          │
└─────────────────────────────────────────┘
```

### Key Features
- ✅ Parallel execution of independent research tasks
- ✅ Python function processes parallel outputs
- ✅ LLM agent creates final synthesis
- ✅ Demonstrates both `get_step_content()` and `get_all_previous_content()`

### Running the Example
```bash
python parallel_outputs_example.py
```

## 🧠 Example 2: Advanced Multi-Source Intelligence

**File:** `parallel_outputs_advanced.py`

### Workflow Structure
```
┌───────────────────────────────────────────────────┐
│  Research Phase (3 Parallel Sources)              │
│  ┌──────┐  ┌──────┐  ┌────────────┐             │
│  │ Tech │  │Market│  │ Competitor │             │
│  └──────┘  └──────┘  └────────────┘             │
└───────────────────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────┐
│  Validate Research Quality (Fail-Fast)            │
│  - Check each source meets minimum quality        │
│  - Stop workflow if validation fails              │
└───────────────────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────┐
│  Structure Intelligence Brief (Python)            │
│  - Extract specific parallel outputs              │
│  - Create structured brief for LLM                │
└───────────────────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────┐
│  Synthesize Intelligence Report (LLM)             │
│  - Create executive-level strategic report        │
│  - Highlight cross-source insights                │
└───────────────────────────────────────────────────┘
```

### Key Features
- ✅ 3-source parallel research (Tech, Market, Competitive)
- ✅ Fail-fast validation pattern (stops if quality insufficient)
- ✅ Structured data preparation for LLM
- ✅ Executive-level intelligence synthesis

### Running the Example
```bash
python parallel_outputs_advanced.py
```

## 📖 StepInput Methods Reference

| Method | Returns | Description |
|--------|---------|-------------|
| `step_input.input` | `str` | Original workflow input message |
| `step_input.previous_step_content` | `str` | Output from immediate previous step |
| `step_input.get_step_content("name")` | `str \| dict` | Output from specific named step |
| `step_input.get_all_previous_content()` | `str` | All previous step outputs combined |

### Special Case: Parallel Steps

When calling `get_step_content()` on a **Parallel step**, it returns a **dictionary**:

```python
parallel_results = step_input.get_step_content("Parallel Research Phase")

# Returns:
{
    "HackerNews Research": "content from HackerNews step...",
    "Web Research": "content from Web step...",
    "Tech Analysis": "content from Analysis step..."
}
```

## 🎨 Common Patterns

### Pattern 1: Parallel Research → Python Aggregation → LLM Summary
**Use Case:** Multi-source research with metrics and final synthesis
```python
Parallel(research1, research2) → Python function → LLM summary
```

### Pattern 2: Parallel Analysis → Validation → LLM Decision
**Use Case:** Quality control with fail-fast validation
```python
Parallel(analysis1, analysis2) → Validation (fail-fast) → LLM decision
```

### Pattern 3: Parallel Data Collection → Structured Brief → LLM Report
**Use Case:** Intelligence gathering and executive reporting
```python
Parallel(source1, source2, source3) → Structure brief → LLM report
```

## 🛠️ Best Practices

### 1. **Name Your Steps**
Always name your steps for easier access:
```python
Step(name="HackerNews Research", agent=researcher)
```

### 2. **Use Fail-Fast Validation**
Validate critical data and stop workflow if needed:
```python
if not data_is_valid:
    return StepOutput(content="Error message", stop=True)
```

### 3. **Prepare Data for LLMs**
Python functions should structure data optimally for LLM consumption:
```python
def prepare_for_llm(step_input: StepInput) -> StepOutput:
    # Extract, validate, structure
    structured_brief = create_structured_output(data)
    return StepOutput(content=structured_brief)
```

### 4. **Leverage Parallel Execution**
Use parallel steps when tasks are independent:
```python
# ✅ Good - Independent tasks
Parallel(research_hn, research_web, research_academic)

# ❌ Bad - Sequential dependency
Parallel(gather_data, process_data, analyze_data)
```

## 🔍 Troubleshooting

### Issue: Parallel results returning None
**Solution:** Ensure you're using the correct parallel step name:
```python
# Check the name you gave to Parallel()
Parallel(..., name="Research Phase")  # Must match
results = step_input.get_step_content("Research Phase")
```

### Issue: LLM summary doesn't have all data
**Solution:** Use `get_all_previous_content()` to ensure all data is included:
```python
def prepare_summary(step_input: StepInput) -> StepOutput:
    all_data = step_input.get_all_previous_content()
    return StepOutput(content=f"All research:\n{all_data}")
```

### Issue: Workflow doesn't stop on validation failure
**Solution:** Use `stop=True` in StepOutput:
```python
return StepOutput(content="Validation failed", stop=True)
```

## 📚 Additional Resources

- [Agno Parallel Steps Documentation](https://docs.agno.com/examples/concepts/workflows/04-workflows-parallel-execution/parallel_steps_workflow)
- [Accessing Previous Steps](https://docs.agno.com/examples/concepts/workflows/06_workflows_advanced_concepts/access_multiple_previous_steps_output)
- [StepInput/StepOutput Reference](https://docs.agno.com/reference/workflows/step-input-output)

## 💡 Real-World Applications

1. **Sales Intelligence** (like your Lotus workflow):
   - Parallel: Company research + LinkedIn search + News scraping
   - Python: Validate quality, extract entities
   - LLM: Synthesize strategic insights

2. **Content Research**:
   - Parallel: Multiple research sources
   - Python: Compute metrics, deduplicate
   - LLM: Create comprehensive article

3. **Competitive Analysis**:
   - Parallel: Research multiple competitors
   - Python: Structure comparison matrix
   - LLM: Strategic recommendations

---

**Created using Agno Workflows 2.0** | [Documentation](https://docs.agno.com)
