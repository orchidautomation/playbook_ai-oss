from agno.agent import Agent
from agno.models.openai import OpenAIChat
from models.vendor_elements import UseCase
from typing import List
from pydantic import BaseModel


class UseCasesExtractionResult(BaseModel):
    use_cases: List[UseCase]


use_case_extractor = Agent(
    name="Use Case Extractor",
    model=OpenAIChat(id="gpt-4o"),
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

    Capture both broad and specific use cases.

    Examples:
    - "Lead qualification automation"
    - "Customer onboarding workflows"
    - "Sales forecasting"
    - "Marketing campaign attribution"

    For each use case, identify:
    - What workflow or process it addresses
    - What problem it solves
    - Who typically uses it
    - What product features enable it
    """,
    output_schema=UseCasesExtractionResult
)
