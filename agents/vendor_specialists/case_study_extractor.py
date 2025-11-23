from agno.agent import Agent
import config
from models.vendor_elements import CaseStudy
from typing import List
from pydantic import BaseModel


class CaseStudiesExtractionResult(BaseModel):
    case_studies: List[CaseStudy]


case_study_extractor = Agent(
    name="Case Study Extractor",
    model=config.EXTRACTION_MODEL,  # gpt-4o-mini for fast extraction
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

    EXAMPLE EXTRACTION:

    Input: "TechCorp, a mid-market SaaS company, struggled with low email response rates. After implementing our platform, they saw reply rates jump from 1.2% to 3.8% in 60 days, generating $2M in new pipeline."

    Output:
    {
      "customer_name": "TechCorp",
      "industry": "SaaS",
      "company_size": "Mid-market",
      "challenge": "Low email response rates",
      "solution": "Implemented messaging platform",
      "results": ["Improved reply rates", "Generated new pipeline"],
      "metrics": ["Reply rates: 1.2% → 3.8%", "60 days to results", "$2M new pipeline"]
    }

    METRIC EXTRACTION PRIORITY:
    1. Percentage improvements (3x, 200%, etc.)
    2. Dollar amounts ($2M pipeline, $500K saved)
    3. Time metrics (60 days, 50% faster)
    4. Volume metrics (10,000 leads, 500 customers)

    HANDLING PARTIAL CASE STUDIES:
    - Missing metrics: Extract qualitative results instead
    - No company name: Use "Unnamed [Industry] Customer"
    - Brief mention: Still extract, mark as partial in notes

    Return all case studies found with complete details.
    Extract metrics whenever available - numbers are gold for sales conversations.
    """,
    output_schema=CaseStudiesExtractionResult
)
