"""
Advanced Parallel Outputs Example - Multiple Approaches to Access Parallel Results

This example demonstrates:
1. Accessing specific parallel step outputs by name
2. Using get_all_previous_content() for simple aggregation
3. Nested parallel steps with custom processing
4. Real-world pattern: Multi-source research → Validation → LLM synthesis
"""

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.workflow import Parallel, Step, Workflow
from agno.workflow.types import StepInput, StepOutput


# ===== AGENTS =====

tech_researcher = Agent(
    name="Tech Research Agent",
    instructions="Research technical developments and engineering trends from HackerNews.",
    tools=[HackerNewsTools()],
    markdown=True,
)

market_researcher = Agent(
    name="Market Research Agent",
    instructions="Research market trends, business news, and industry insights from the web.",
    tools=[DuckDuckGoTools()],
    markdown=True,
)

competitor_analyst = Agent(
    name="Competitor Analysis Agent",
    instructions="Research competitive landscape and market positioning from the web.",
    tools=[DuckDuckGoTools()],
    markdown=True,
)

intelligence_synthesizer = Agent(
    name="Intelligence Synthesizer",
    instructions=[
        "You are a strategic intelligence analyst who creates executive-level reports.",
        "Synthesize research from multiple sources into actionable insights.",
        "Highlight key trends, opportunities, and strategic recommendations.",
        "Structure your output for C-level executives: concise, insightful, actionable."
    ],
    markdown=True,
)


# ===== PYTHON PROCESSING FUNCTIONS =====

def validate_research_quality(step_input: StepInput) -> StepOutput:
    """
    Validation step that ensures research quality before proceeding.
    Demonstrates fail-fast pattern from your global preferences.
    """

    # Access parallel results
    parallel_results = step_input.get_step_content("Research Phase")

    if not parallel_results or not isinstance(parallel_results, dict):
        error_msg = "❌ Research validation failed - no parallel results found"
        print(f"\n{error_msg}")
        return StepOutput(content=error_msg, stop=True)

    # Validate each source
    validation_results = {}
    min_length = 100  # Minimum characters per source

    for step_name, content in parallel_results.items():
        content_length = len(content) if content else 0
        is_valid = content_length >= min_length

        validation_results[step_name] = {
            "valid": is_valid,
            "length": content_length,
            "status": "✓" if is_valid else "✗"
        }

    # Check if all sources passed validation
    all_valid = all(v["valid"] for v in validation_results.values())

    if not all_valid:
        error_msg = f"""
❌ RESEARCH QUALITY CHECK FAILED

Validation Results:
{chr(10).join(f'  {v["status"]} {name}: {v["length"]} chars (min: {min_length})' for name, v in validation_results.items())}

Cannot proceed with insufficient research data.
        """.strip()
        print(f"\n{error_msg}")
        return StepOutput(content=error_msg, stop=True)

    # Validation passed
    success_msg = f"""
✅ RESEARCH QUALITY CHECK PASSED

Validation Results:
{chr(10).join(f'  {v["status"]} {name}: {v["length"]:,} chars' for name, v in validation_results.items())}

Total Data Collected: {sum(v["length"] for v in validation_results.values()):,} characters

All sources validated - proceeding to synthesis phase.
    """.strip()

    print(f"\n{success_msg}")

    # Pass the validated data forward
    return StepOutput(
        content=success_msg,
        success=True
    )


def create_structured_intelligence_brief(step_input: StepInput) -> StepOutput:
    """
    Create structured intelligence brief from parallel research outputs.
    Demonstrates accessing specific parallel steps and creating structured data.
    """

    # Access specific parallel step results
    parallel_results = step_input.get_step_content("Research Phase")
    validation_report = step_input.get_step_content("Validate Research Quality")

    if not parallel_results or not isinstance(parallel_results, dict):
        return StepOutput(
            content="❌ Cannot create brief - missing parallel results",
            stop=True
        )

    # Extract individual research components
    tech_research = parallel_results.get("Tech Research", "No tech data")
    market_research = parallel_results.get("Market Research", "No market data")
    competitor_research = parallel_results.get("Competitor Analysis", "No competitor data")

    # Create structured brief for the LLM
    intelligence_brief = f"""
# INTELLIGENCE BRIEF FOR SYNTHESIS

## Validation Status
{validation_report}

---

## Source 1: Technical Intelligence
**Source:** HackerNews Developer Community
**Focus:** Technical developments, engineering trends, developer sentiment

{tech_research[:800]}
{'...[truncated]' if len(tech_research) > 800 else ''}

---

## Source 2: Market Intelligence
**Source:** Web News & Industry Analysis
**Focus:** Market trends, business developments, industry dynamics

{market_research[:800]}
{'...[truncated]' if len(market_research) > 800 else ''}

---

## Source 3: Competitive Intelligence
**Source:** Web Research & Analysis
**Focus:** Competitive landscape, market positioning, strategic movements

{competitor_research[:800]}
{'...[truncated]' if len(competitor_research) > 800 else ''}

---

## Synthesis Instructions
Please analyze the above intelligence from all three sources and create:
1. Executive Summary (3-5 key insights)
2. Strategic Trends (technical + market + competitive)
3. Opportunities & Threats
4. Actionable Recommendations

Focus on insights that emerge from **combining** multiple sources.
    """.strip()

    return StepOutput(
        content=intelligence_brief,
        success=True
    )


# ===== WORKFLOW STEPS =====

tech_research_step = Step(
    name="Tech Research",
    agent=tech_researcher,
    description="Research technical developments from HackerNews"
)

market_research_step = Step(
    name="Market Research",
    agent=market_researcher,
    description="Research market trends and business news"
)

competitor_analysis_step = Step(
    name="Competitor Analysis",
    agent=competitor_analyst,
    description="Research competitive landscape and positioning"
)

validation_step = Step(
    name="Validate Research Quality",
    executor=validate_research_quality,
    description="Validate research quality before synthesis (fail-fast pattern)"
)

structure_brief_step = Step(
    name="Structure Intelligence Brief",
    executor=create_structured_intelligence_brief,
    description="Create structured intelligence brief from parallel outputs"
)

synthesis_step = Step(
    name="Synthesize Intelligence Report",
    agent=intelligence_synthesizer,
    description="Create final strategic intelligence report"
)


# ===== WORKFLOW =====

advanced_parallel_workflow = Workflow(
    name="Advanced Multi-Source Intelligence Workflow",
    description="Parallel research → Quality validation → Structured brief → LLM synthesis",
    steps=[
        # Step 1: Parallel research from 3 sources
        Parallel(
            tech_research_step,
            market_research_step,
            competitor_analysis_step,
            name="Research Phase",
            description="Execute multi-source research in parallel"
        ),
        # Step 2: Validate quality (fail-fast pattern)
        validation_step,
        # Step 3: Create structured brief
        structure_brief_step,
        # Step 4: LLM synthesizes final report
        synthesis_step
    ]
)


# ===== EXECUTION =====

if __name__ == "__main__":
    print("=" * 80)
    print("🧠 ADVANCED PARALLEL OUTPUTS - Multi-Source Intelligence Pipeline")
    print("=" * 80)
    print()
    print("📊 Workflow Architecture:")
    print("   Phase 1: Parallel Research (Tech + Market + Competitive)")
    print("   Phase 2: Quality Validation (Fail-Fast Pattern)")
    print("   Phase 3: Structure Intelligence Brief (Python)")
    print("   Phase 4: Synthesize Final Report (LLM)")
    print()
    print("=" * 80)
    print()

    # Execute workflow
    advanced_parallel_workflow.print_response(
        input="AI agent frameworks and autonomous system platforms",
        stream=True,
        stream_events=True,
        markdown=True
    )

    print()
    print("=" * 80)
    print("✅ Intelligence Pipeline Complete")
    print("=" * 80)
    print()
    print("💡 Key Patterns Demonstrated:")
    print("   • Accessing parallel outputs by name: get_step_content('parallel_step_name')")
    print("   • Fail-fast validation with stop=True")
    print("   • Structured data preparation for LLM synthesis")
    print("   • Multi-source intelligence aggregation")
    print("=" * 80)
