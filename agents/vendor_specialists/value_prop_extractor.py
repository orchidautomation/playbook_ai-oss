from agno.agent import Agent
from agno.models.openai import OpenAIChat
from models.vendor_elements import ValueProposition
from typing import List
from pydantic import BaseModel


class ValuePropositionsExtractionResult(BaseModel):
    value_propositions: List[ValueProposition]


value_prop_extractor = Agent(
    name="Value Proposition Extractor",
    model=OpenAIChat(id="gpt-4o"),
    instructions="""
    You are an expert at identifying core value propositions and positioning statements.

    Extract value propositions - the core benefits and outcomes promised.

    For each value prop:
    - Statement: The value proposition (concise, compelling)
    - Benefits: List of specific benefits delivered
    - Differentiation: What makes this unique (if mentioned)
    - Target persona: Who this appeals to (if mentioned)
    - Sources: URLs where found (include page_type)

    Look for:
    - Homepage hero sections
    - About page positioning
    - Product benefit statements
    - "Why choose us" sections
    - Main taglines and headlines
    - Customer outcome promises

    Focus on outcome-based value, not just feature lists.
    Look for statements about what customers achieve or gain.

    Examples of value props:
    - "Close deals 3x faster"
    - "Transform customer engagement"
    - "Simplify complex workflows"
    - "Drive revenue growth"

    Extract both primary value prop and secondary/supporting value propositions.
    """,
    output_schema=ValuePropositionsExtractionResult
)
