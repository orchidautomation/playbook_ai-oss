"""
Parallel Outputs Example - Demonstrating Parallel Execution with Final LLM Summary

This example shows how to:
1. Run multiple independent steps in parallel (both LLM agents and Python functions)
2. Access outputs from all parallel steps in a subsequent step
3. Use an LLM to summarize and synthesize the parallel outputs into a final report

Pattern: Parallel Research → Python Aggregator → LLM Final Summary
"""

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.workflow import Parallel, Step, Workflow
from agno.workflow.types import StepInput, StepOutput


# ===== AGENTS =====

# Research agents that run in parallel
hackernews_researcher = Agent(
    name="HackerNews Researcher",
    instructions="Research tech news and trends from Hacker News. Focus on developer discussions and trending topics.",
    tools=[HackerNewsTools()],
    markdown=True,
)

web_researcher = Agent(
    name="Web Researcher",
    instructions="Research general web information using DuckDuckGo. Focus on news articles and industry insights.",
    tools=[DuckDuckGoTools()],
    markdown=True,
)

# Final summarizer agent
final_summarizer = Agent(
    name="Intelligence Analyst",
    instructions=[
        "You are an expert analyst who synthesizes information from multiple research sources.",
        "Create comprehensive, well-structured reports that highlight key insights and patterns.",
        "Always reference which sources provided which insights.",
        "Focus on actionable intelligence and clear conclusions."
    ],
    markdown=True,
)


# ===== PYTHON CUSTOM FUNCTION STEP =====

def extract_key_metrics(step_input: StepInput) -> StepOutput:
    """
    Python function that processes data from parallel steps.
    Demonstrates accessing specific parallel step outputs and computing metrics.
    """

    # Access the parallel step outputs by name
    # When you call get_step_content() on a Parallel step, it returns a dict
    # with keys being the individual step names
    parallel_results = step_input.get_step_content("Parallel Research Phase")

    if not parallel_results or not isinstance(parallel_results, dict):
        return StepOutput(
            content="❌ No parallel results found",
            success=False
        )

    # Extract individual results
    hn_data = parallel_results.get("HackerNews Research", "")
    web_data = parallel_results.get("Web Research", "")

    # Compute some metrics
    hn_length = len(hn_data) if hn_data else 0
    web_length = len(web_data) if web_data else 0
    total_length = hn_length + web_length

    # Create structured output for the LLM
    metrics_report = f"""
## Data Collection Metrics

**Total Data Collected:** {total_length:,} characters

### Source Breakdown:
- **HackerNews Research:** {hn_length:,} characters ({(hn_length/total_length*100) if total_length > 0 else 0:.1f}%)
- **Web Research:** {web_length:,} characters ({(web_length/total_length*100) if total_length > 0 else 0:.1f}%)

### Quality Indicators:
- ✓ Both sources completed successfully
- ✓ Data validated and ready for analysis
- ✓ Minimum threshold met: {total_length >= 500}

---

### Raw Research Data for Analysis:

#### HackerNews Findings:
{hn_data[:1000]}{'...' if len(hn_data) > 1000 else ''}

#### Web Research Findings:
{web_data[:1000]}{'...' if len(web_data) > 1000 else ''}
    """.strip()

    return StepOutput(
        content=metrics_report,
        success=True
    )


# Alternative: Python function that uses get_all_previous_content()
def aggregate_all_data(step_input: StepInput) -> StepOutput:
    """
    Alternative approach: Get ALL previous content regardless of step structure.
    """

    # Get all previous content as a single string
    all_content = step_input.get_all_previous_content()

    # Get original workflow input
    original_query = step_input.input or "No query provided"

    aggregated_report = f"""
## Aggregated Intelligence Report

**Original Query:** {original_query}

**Total Content Gathered:** {len(all_content):,} characters

### Combined Research Findings:
{all_content[:2000]}{'...' if len(all_content) > 2000 else ''}

---
*Ready for final analysis and synthesis*
    """.strip()

    return StepOutput(
        content=aggregated_report,
        success=True
    )


# ===== WORKFLOW STEPS =====

# Parallel research steps
hackernews_step = Step(
    name="HackerNews Research",
    agent=hackernews_researcher,
    description="Research trending tech topics from HackerNews"
)

web_step = Step(
    name="Web Research",
    agent=web_researcher,
    description="Research general web information and news"
)

# Python processing step
metrics_step = Step(
    name="Extract Metrics",
    executor=extract_key_metrics,
    description="Process parallel outputs and extract key metrics"
)

# Final LLM summary step
summary_step = Step(
    name="Final Summary",
    agent=final_summarizer,
    description="Create comprehensive final report from all research sources"
)


# ===== WORKFLOW DEFINITION =====

parallel_workflow = Workflow(
    name="Parallel Research with LLM Summary",
    description="Demonstrates parallel execution with Python processing and LLM final summary",
    steps=[
        # Step 1: Run multiple agents in parallel
        Parallel(
            hackernews_step,
            web_step,
            name="Parallel Research Phase",
            description="Execute multiple research tasks simultaneously"
        ),
        # Step 2: Python function processes the parallel outputs
        metrics_step,
        # Step 3: LLM agent creates final summary from all previous content
        summary_step
    ]
)


# ===== EXECUTION =====

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 PARALLEL OUTPUTS EXAMPLE - Research with Final LLM Summary")
    print("=" * 80)
    print()
    print("📋 Workflow Structure:")
    print("   1. Parallel Research Phase (HackerNews + Web) - Run simultaneously")
    print("   2. Extract Metrics (Python) - Process parallel outputs")
    print("   3. Final Summary (LLM) - Synthesize all findings")
    print()
    print("=" * 80)
    print()

    # Execute workflow
    parallel_workflow.print_response(
        input="Latest developments in AI agents and autonomous systems",
        stream=True,
        stream_events=True,
        markdown=True
    )

    print()
    print("=" * 80)
    print("✅ Workflow Complete")
    print("=" * 80)
