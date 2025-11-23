from agno.agent import Agent
import config
from models.vendor_elements import Differentiator
from typing import List
from pydantic import BaseModel


class DifferentiatorsExtractionResult(BaseModel):
    differentiators: List[Differentiator]


differentiator_extractor = Agent(
    name="Competitive Differentiator Extractor",
    model=config.EXTRACTION_MODEL,  # gpt-4o-mini for fast extraction
    instructions="""
    You are an expert at identifying competitive differentiation.

    Extract statements about what makes the vendor unique or better.

    For each differentiator:
    - Category: feature, approach, market_position, or technology
    - Statement: The differentiation claim
    - vs_alternative: What they're comparing against (if mentioned)
    - Evidence: Supporting points or proof
    - Sources: URLs where found (include page_type)

    Look for:
    - "Unlike other solutions..."
    - "The only platform that..."
    - "First to market..."
    - Unique feature claims
    - Proprietary technology mentions
    - Market positioning statements
    - Competitive comparisons
    - "Why choose us" sections

    EXAMPLES BY CATEGORY:

    Feature:
    {
      "category": "feature",
      "statement": "The only platform with real-time conversation intelligence",
      "vs_alternative": "Other sales tools",
      "evidence": "Processes calls in <2 seconds vs. industry standard 24 hours"
    }

    Approach:
    {
      "category": "approach",
      "statement": "Revenue-first methodology vs. activity-based selling",
      "vs_alternative": "Traditional CRMs",
      "evidence": "Customers see 3x pipeline velocity improvement"
    }

    Market Position:
    {
      "category": "market_position",
      "statement": "Leader in Gartner Magic Quadrant for 3 consecutive years",
      "vs_alternative": null,
      "evidence": "Gartner Magic Quadrant 2022, 2023, 2024"
    }

    Technology:
    {
      "category": "technology",
      "statement": "Proprietary NLP engine trained on 10B+ sales conversations",
      "vs_alternative": "Generic AI models",
      "evidence": "Patent pending, 94% accuracy rate"
    }

    STRONG vs. WEAK DIFFERENTIATORS:
    - STRONG: Specific, provable, quantified ("Only platform with X", "3x faster than Y")
    - WEAK: Vague claims ("Best-in-class", "Industry-leading", "Powerful")

    HANDLING EDGE CASES:
    - No explicit comparison: Infer vs_alternative from context
    - Unsubstantiated claims: Extract but note "no evidence provided"
    - Multiple claims in one statement: Split into separate differentiators

    Extract evidence when available (customer proof, metrics, third-party validation).
    Capture both explicit comparisons and implied differentiation.
    """,
    output_schema=DifferentiatorsExtractionResult
)
