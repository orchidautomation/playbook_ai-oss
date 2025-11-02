from agno.agent import Agent
from agno.models.openai import OpenAIChat
from models.vendor_elements import ReferenceCustomer
from typing import List
from pydantic import BaseModel


class ReferenceCustomersExtractionResult(BaseModel):
    reference_customers: List[ReferenceCustomer]


customer_extractor = Agent(
    name="Reference Customer Extractor",
    model=OpenAIChat(id="gpt-4o"),
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

    Capture ALL companies mentioned, even if minimal info available.

    For relationship type:
    - "customer": Paying customer using the product
    - "partner": Business partner or reseller
    - "integration": Technology integration partner
    - "other": Unknown or other relationship

    Extract company size indicators like:
    - Fortune 500, Enterprise, SMB, Mid-market
    - Employee count if mentioned
    """,
    output_schema=ReferenceCustomersExtractionResult
)
