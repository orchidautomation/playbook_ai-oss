from agno.agent import Agent
import config
from models.vendor_elements import UseCase
from typing import List
from pydantic import BaseModel


class UseCasesExtractionResult(BaseModel):
    use_cases: List[UseCase]


use_case_extractor = Agent(
    name="Use Case Extractor",
    model=config.EXTRACTION_MODEL,  # gpt-4o-mini for fast extraction
    instructions="""
    You are an expert at identifying use cases and workflow solutions.

    Extract ALL use cases - specific ways customers use the product.

    For each use case:
    - Title: Name of the use case
    - Description: What this use case accomplishes
    - Target persona: Who uses this (if mentioned)
    - Target industry: Industry focus (if mentioned)
    - Problems solved: List of problems addressed
    - Key features used: Features relevant to this use case
    - Sources: URLs where found (include page_type)

    Look for:
    - /use-cases pages
    - /solutions pages
    - /industries pages
    - Workflow descriptions
    - "How to" sections
    - Problem-solution narratives
    - Industry-specific solutions

    EXAMPLE EXTRACTION:

    Input: "For Sales Teams: Automate lead qualification to focus on high-intent prospects. Our AI scoring identifies ready-to-buy signals so your reps stop wasting time on cold leads."

    Output:
    {
      "title": "Lead Qualification Automation",
      "description": "AI-powered lead scoring that identifies high-intent prospects automatically",
      "target_persona": "Sales Teams",
      "target_industry": null,
      "problems_solved": ["Reps wasting time on cold leads", "Manual lead qualification"],
      "key_features_used": ["AI scoring", "Intent signal detection"]
    }

    USE CASE vs. FEATURE:
    - USE CASE: "Automate lead qualification" (workflow/outcome)
    - NOT a use case: "AI-powered scoring" (feature)

    INFERRING PERSONAS/INDUSTRIES:
    - "For enterprise teams" → Target persona: Enterprise teams
    - "Healthcare solutions" → Target industry: Healthcare
    - No explicit mention → Infer from context or leave empty

    HANDLING EDGE CASES:
    - Overlapping use cases: Create separate entries if different personas/industries
    - Vague use cases: Extract if actionable, skip pure marketing fluff
    - Industry pages: One use case per industry with specific problems

    Capture both broad and specific use cases.
    """,
    output_schema=UseCasesExtractionResult
)
