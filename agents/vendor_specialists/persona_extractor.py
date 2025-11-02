from agno.agent import Agent
from agno.models.openai import OpenAIChat
from models.vendor_elements import TargetPersona
from typing import List
from pydantic import BaseModel


class TargetPersonasExtractionResult(BaseModel):
    target_personas: List[TargetPersona]


persona_extractor = Agent(
    name="Target Persona Extractor",
    model=OpenAIChat(id="gpt-4o"),
    instructions="""
    You are an expert at identifying target buyer personas.

    Extract ALL personas the vendor targets - who they sell to.

    For each persona:
    - Title: Job title (e.g., "CMO", "VP Sales", "Product Manager")
    - Department: Department or function
    - Responsibilities: Key responsibilities mentioned
    - Pain points: Problems this persona faces (mentioned or implied)
    - Sources: URLs where found (include page_type)

    Look for:
    - Persona-specific landing pages
    - "For [Role]" sections
    - Testimonials with titles
    - Use cases by role
    - Product messaging by audience
    - CTA language ("For marketing teams", etc.)

    Infer personas from:
    - Who testimonials are from
    - Who use cases target
    - Job titles in case studies
    - Role-based messaging
    - Department-specific solutions

    Examples of personas:
    - Chief Marketing Officer (CMO)
    - VP of Sales
    - Revenue Operations Manager
    - Product Manager
    - Customer Success Director

    Extract both explicit personas (directly mentioned) and implicit personas (inferred from content).
    """,
    output_schema=TargetPersonasExtractionResult
)
