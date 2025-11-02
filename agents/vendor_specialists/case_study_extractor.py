from agno.agent import Agent
from agno.models.openai import OpenAIChat
from models.vendor_elements import CaseStudy
from typing import List
from pydantic import BaseModel


class CaseStudiesExtractionResult(BaseModel):
    case_studies: List[CaseStudy]


case_study_extractor = Agent(
    name="Case Study Extractor",
    model=OpenAIChat(id="gpt-4o"),
    instructions="""
    You are an expert at extracting customer success stories and case studies.

    Extract ALL case studies, customer stories, and success examples.

    For each case study, extract:
    - Customer name: Company name
    - Industry: Their industry (if mentioned)
    - Company size: SMB, Mid-market, Enterprise (if mentioned)
    - Challenge: Problem they faced
    - Solution: How vendor helped
    - Results: List of outcomes achieved
    - Metrics: Quantified results (%, $, time saved, etc.)
    - Sources: URLs where found (include page_type)

    Look for:
    - /customers, /case-studies, /success-stories pages
    - Customer testimonials with details
    - Homepage customer highlights
    - "Customer stories" sections
    - Detailed success narratives

    Return all case studies found with complete details.
    Extract metrics whenever available - numbers matter.
    """,
    output_schema=CaseStudiesExtractionResult
)
