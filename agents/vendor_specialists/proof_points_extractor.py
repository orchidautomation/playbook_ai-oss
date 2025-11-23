from agno.agent import Agent
import config
from models.vendor_elements import ProofPoint
from typing import List
from pydantic import BaseModel


class ProofPointsExtractionResult(BaseModel):
    proof_points: List[ProofPoint]


proof_points_extractor = Agent(
    name="Proof Points Extractor",
    model=config.EXTRACTION_MODEL,  # gpt-4o-mini for fast extraction
    instructions="""
    You are an expert at identifying credibility indicators and social proof.

    Extract ALL proof points including:
    - Testimonials: Customer quotes and endorsements
    - Statistics: Usage stats (X customers, Y% growth, Z awards)
    - Awards: Industry recognition, certifications, badges
    - Certifications: Compliance, security, industry standards

    For each proof point:
    - Type: testimonial, statistic, award, or certification
    - Content: The actual proof point text
    - Source attribution: Who said it or where from (if applicable)
    - Sources: URLs where found (include page_type)

    EXAMPLES BY TYPE:

    Testimonial:
    {
      "type": "testimonial",
      "content": "This platform transformed how our team sells. We closed 40% more deals in Q1.",
      "source_attribution": "Sarah Chen, VP Sales at TechCorp"
    }

    Statistic:
    {
      "type": "statistic",
      "content": "Trusted by 500+ companies including Fortune 500 enterprises",
      "source_attribution": null
    }

    Award:
    {
      "type": "award",
      "content": "Named Leader in Gartner Magic Quadrant 2024",
      "source_attribution": "Gartner"
    }

    Certification:
    {
      "type": "certification",
      "content": "SOC 2 Type II Certified",
      "source_attribution": "Annual audit"
    }

    WHAT MAKES A STRONG PROOF POINT:
    - Specific numbers beat vague claims ("500+ customers" > "many customers")
    - Named sources beat anonymous ("Sarah Chen, VP Sales" > "Sales Leader")
    - Third-party validation beats self-claims (Gartner > internal survey)

    HANDLING EDGE CASES:
    - Vague testimonials: Still extract, but note lack of specificity
    - Undated awards: Extract but don't assume recency
    - Logo walls without context: Extract as "customer" type statistic

    Return comprehensive list of ALL proof points.
    Capture exact wording and attribution when available.
    """,
    output_schema=ProofPointsExtractionResult
)
