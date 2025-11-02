from agno.agent import Agent
from agno.models.openai import OpenAIChat
from models.vendor_elements import Differentiator
from typing import List
from pydantic import BaseModel


class DifferentiatorsExtractionResult(BaseModel):
    differentiators: List[Differentiator]


differentiator_extractor = Agent(
    name="Competitive Differentiator Extractor",
    model=OpenAIChat(id="gpt-4o"),
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

    Categories explained:
    - feature: Unique product features or capabilities
    - approach: Unique methodology or way of solving problems
    - market_position: Market leadership, first-mover, niche focus
    - technology: Proprietary tech, patents, unique architecture

    Capture both explicit comparisons and implied differentiation.

    Examples:
    - "The only AI-powered platform with real-time sync"
    - "Unlike traditional CRMs, we use a revenue-first approach"
    - "Industry leader with 10+ years of expertise"
    - "Proprietary machine learning algorithms"

    Extract evidence when available (customer proof, metrics, third-party validation).
    """,
    output_schema=DifferentiatorsExtractionResult
)
