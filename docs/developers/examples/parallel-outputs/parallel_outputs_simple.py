"""
SIMPLE PARALLEL OUTPUTS EXAMPLE - Start Here!

This is the simplest possible example of parallel outputs with LLM summary.
Run this first to understand the basic pattern.

Pattern: 2 Parallel Steps → LLM Summary
"""

from agno.agent import Agent
from agno.workflow import Parallel, Step, Workflow

# ===== STEP 1: Define Agents =====

# Two simple agents that will run in parallel
agent1 = Agent(
    name="Research Agent 1",
    instructions="You are a researcher. Find 3-5 key facts about the topic.",
    markdown=True,
)

agent2 = Agent(
    name="Research Agent 2",
    instructions="You are a trend analyst. Identify 3-5 current trends about the topic.",
    markdown=True,
)

# An agent that will summarize both outputs
summarizer = Agent(
    name="Summary Agent",
    instructions="Combine the research and trends into a concise executive summary with bullet points.",
    markdown=True,
)

# ===== STEP 2: Create Steps =====

research_step = Step(name="Key Facts", agent=agent1)
trends_step = Step(name="Current Trends", agent=agent2)
summary_step = Step(name="Executive Summary", agent=summarizer)

# ===== STEP 3: Build Workflow =====

simple_workflow = Workflow(
    name="Simple Parallel to Summary",
    steps=[
        # These two run at the same time
        Parallel(
            research_step,
            trends_step,
            name="Research Phase"
        ),
        # This runs after both parallel steps complete
        summary_step
    ]
)

# ===== STEP 4: Run It! =====

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 SIMPLE PARALLEL OUTPUTS EXAMPLE")
    print("="*60)
    print("\nWorkflow: Research (parallel) → Summary\n")
    print("="*60 + "\n")

    # Execute the workflow
    simple_workflow.print_response(
        input="artificial intelligence in healthcare",
        markdown=True
    )

    print("\n" + "="*60)
    print("✅ Complete! The summary combined both parallel outputs.")
    print("="*60 + "\n")


"""
WHAT HAPPENED:

1. Two agents ran IN PARALLEL (simultaneously):
   - Agent 1: Researched key facts
   - Agent 2: Analyzed trends

2. Both outputs were automatically passed to the summary step

3. Summary agent received BOTH outputs and created final summary

NEXT STEPS:

- Run this file: python parallel_outputs_simple.py
- See parallel_outputs_example.py for Python processing step
- See parallel_outputs_advanced.py for validation & structure
- Read PARALLEL_OUTPUTS_GUIDE.md for comprehensive docs
"""
