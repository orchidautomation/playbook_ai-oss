from agno.agent import Agent
from agno.models.openai import OpenAIChat
from models.vendor_elements import Offering
from typing import List
from pydantic import BaseModel


class OfferingsExtractionResult(BaseModel):
    offerings: List[Offering]


offerings_extractor = Agent(
    name="Offerings Extractor",
    model=OpenAIChat(id="gpt-4o"),
    instructions="""
    You are an expert at identifying and cataloging product offerings from company content.

    Extract ALL products, services, or platform components mentioned.

    For each offering, extract:
    - Name: Official product/service name
    - Description: What it does (1-2 sentences)
    - Features: List of key capabilities or features
    - Pricing indicators: Any pricing info mentioned (free tier, enterprise, etc.)
    - Target audience: Who it's for (if mentioned)
    - Sources: URLs where this info was found (include page_type like 'homepage', 'product', 'pricing')

    Look for:
    - Product pages (/products, /platform, /solutions)
    - Feature lists
    - Pricing pages
    - Homepage offerings
    - Service descriptions

    Return comprehensive structured output with ALL offerings found.
    Be thorough - capture every distinct product or service offering.
    """,
    output_schema=OfferingsExtractionResult
)
