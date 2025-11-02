from agno.agent import Agent
from agno.models.openai import OpenAIChat
from models.vendor_elements import ProofPoint
from typing import List
from pydantic import BaseModel


class ProofPointsExtractionResult(BaseModel):
    proof_points: List[ProofPoint]


proof_points_extractor = Agent(
    name="Proof Points Extractor",
    model=OpenAIChat(id="gpt-4o"),
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

    Look across all pages for credibility indicators:
    - Customer testimonials and quotes
    - "Trusted by X companies"
    - Industry awards and recognition
    - Compliance badges (SOC2, GDPR, etc.)
    - Usage statistics
    - Growth metrics
    - Customer satisfaction scores

    Return comprehensive list of ALL proof points.
    Capture exact wording and attribution when available.
    """,
    output_schema=ProofPointsExtractionResult
)
