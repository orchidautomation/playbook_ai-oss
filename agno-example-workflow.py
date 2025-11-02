from agno.agent import Agent
from agno.workflow import Workflow, Step, Parallel, StepInput, StepOutput
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Define structured output model
class FinalReport(BaseModel):
    summary: str = Field(description="Executive summary")
    key_findings: List[str] = Field(description="Main findings")
    recommendations: List[str] = Field(description="Action items")

# Python function step 1
def preprocess_data(step_input: StepInput) -> StepOutput:
    topic = step_input.input
    processed = f"Preprocessed topic: {topic}"
    return StepOutput(content=processed)

# Python function step 2
def analyze_results(step_input: StepInput) -> StepOutput:
    # Access specific parallel step outputs
    research_a = step_input.get_step_content("research_a")
    research_b = step_input.get_step_content("research_b")
    
    analysis = f"Analysis:\nSource A: {research_a}...\nSource B: {research_b}..."
    return StepOutput(content=analysis)

# Define agents
agent_a = Agent(
    name="Researcher A",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions="Research from perspective A"
)

agent_b = Agent(
    name="Researcher B", 
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions="Research from perspective B"
)

# AI agent with structured output and explicit step references
final_agent = Agent(
    name="Report Generator",
    model=OpenAIChat(id="gpt-4o"),
    output_schema=FinalReport,
    instructions="""Generate a comprehensive report using ALL previous step outputs:
    
    1. PREPROCESSED DATA: {preprocess}
    2. RESEARCH A FINDINGS: {research_a}
    3. RESEARCH B FINDINGS: {research_b}
    4. ANALYSIS RESULTS: {analyze}
    
    Synthesize all this information into a structured report with summary, key findings, and recommendations."""
)

# Build workflow
workflow = Workflow(
    name="Complete Example",
    steps=[
        Step(name="preprocess", executor=preprocess_data),
        Parallel(
            Step(name="research_a", agent=agent_a),
            Step(name="research_b", agent=agent_b),
            name="parallel_research"
        ),
        Step(name="analyze", executor=analyze_results),
        Step(name="final_report", agent=final_agent)
    ]
)

# Run workflow
workflow.print_response("AI trends 2025", markdown=True)

