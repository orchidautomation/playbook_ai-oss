from agno.agent import Agent
import config
from models.vendor_elements import Offering
from typing import List
from pydantic import BaseModel


class OfferingsExtractionResult(BaseModel):
    offerings: List[Offering]


offerings_extractor = Agent(
    name="Offerings Extractor",
    model=config.EXTRACTION_MODEL,  # gpt-4o-mini for fast extraction
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

    EXAMPLE EXTRACTION:

    Input: "Our AI Sales Platform helps teams close more deals with intelligent lead scoring and automated follow-ups. Starting at $99/user/month. Perfect for growing sales teams."

    Output:
    {
      "name": "AI Sales Platform",
      "description": "Helps sales teams close more deals using intelligent automation for lead management",
      "features": ["Intelligent lead scoring", "Automated follow-ups"],
      "pricing_indicators": "Starting at $99/user/month",
      "target_audience": "Growing sales teams"
    }

    WHAT TO EXTRACT vs. SKIP:
    - DO extract: Named products, platforms, services, distinct modules
    - DON'T extract: Generic capabilities without product names, marketing fluff

    HANDLING EDGE CASES:
    - Overlapping products: Create separate entries, note relationships
    - Unnamed features: Group under parent product
    - No pricing: Leave field empty, don't guess
    - Vague descriptions: Use exact wording from source

    Return comprehensive structured output with ALL offerings found.
    Be thorough - capture every distinct product or service offering.
    """,
    output_schema=OfferingsExtractionResult
)
