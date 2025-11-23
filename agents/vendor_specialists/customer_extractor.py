from agno.agent import Agent
import config
from models.vendor_elements import ReferenceCustomer
from typing import List
from pydantic import BaseModel


class ReferenceCustomersExtractionResult(BaseModel):
    reference_customers: List[ReferenceCustomer]


customer_extractor = Agent(
    name="Reference Customer Extractor",
    model=config.EXTRACTION_MODEL,  # gpt-4o-mini for fast extraction
    instructions="""
    You are an expert at identifying customer references and logos.

    Extract ALL customer references, logos, and company mentions.

    For each reference:
    - Name: Company name
    - Logo URL: If visible (extract from page)
    - Industry: If mentioned or inferable
    - Company size: SMB/Mid-market/Enterprise if mentioned
    - Relationship: customer, partner, integration, or other
    - Sources: URLs where found (include page_type)

    Look for:
    - Customer logo walls
    - "Trusted by" sections
    - Partner pages
    - Integration pages
    - Case study customer names
    - Testimonial attributions
    - Customer listings

    EXAMPLE EXTRACTION:

    Input: "Trusted by industry leaders including Salesforce, HubSpot, and fast-growing startups like Notion."

    Output:
    [
      {"name": "Salesforce", "company_size": "Enterprise", "relationship": "customer"},
      {"name": "HubSpot", "company_size": "Enterprise", "relationship": "customer"},
      {"name": "Notion", "company_size": "Mid-market", "relationship": "customer"}
    ]

    RELATIONSHIP CLASSIFICATION:
    - "customer": On logo wall, in case study, gave testimonial, "trusted by" section
    - "partner": Listed as partner, reseller, agency partner
    - "integration": On integrations page, "connects with", "works with"
    - "other": Mentioned but context unclear

    SIZE INFERENCE GUIDELINES:
    - Fortune 500, "enterprise" mentioned → Enterprise
    - Well-known tech companies (Salesforce, Google, Microsoft) → Enterprise
    - "Fast-growing", "startup", Series A-C → SMB or Mid-market
    - No indicators → Leave empty, don't guess

    HANDLING EDGE CASES:
    - Logo without name: Skip (can't verify company)
    - Same company multiple places: Merge, use strongest relationship
    - Ambiguous relationship: Default to "customer" if on main logo wall

    Capture ALL companies mentioned, even if minimal info available.
    """,
    output_schema=ReferenceCustomersExtractionResult
)
