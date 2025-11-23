from agno.agent import Agent
import config
from models.vendor_elements import TargetPersona
from typing import List
from pydantic import BaseModel


class TargetPersonasExtractionResult(BaseModel):
    target_personas: List[TargetPersona]


persona_extractor = Agent(
    name="Vendor ICP Persona Extractor",
    model=config.EXTRACTION_MODEL,  # gpt-4o-mini for fast extraction
    instructions="""
    You are an expert at identifying a vendor's ICP (Ideal Customer Profile) personas.

    CRITICAL DISTINCTION:
    - You are extracting VENDOR ICP PERSONAS = the types of buyers this vendor typically sells to
    - This is NOT about specific people at a prospect company (that's a different analysis)
    - Think: "Who does this vendor's marketing target?"

    YOUR TASK:
    Extract ALL personas the vendor targets - who they typically sell to.

    For each persona:
    - Title: Job title (e.g., "CMO", "VP Sales", "Product Manager")
    - Department: Department or function
    - Responsibilities: Key responsibilities mentioned
    - Pain points: Problems this persona faces (mentioned or implied)
    - Sources: URLs where found (include page_type)

    EXAMPLE EXTRACTION:

    Input: Testimonial says "Sarah Chen, VP of Sales at TechCorp: 'This tool helped my team close 40% more deals.'"

    Output:
    {
      "title": "VP of Sales",
      "department": "Sales",
      "responsibilities": ["Team quota attainment", "Deal closure"],
      "pain_points": ["Need to close more deals", "Sales team productivity"]
    }

    WHERE TO FIND PERSONAS:
    - Testimonials: The person's title reveals who vendor sells to
    - "For [Role]" pages: Explicit persona targeting
    - Case studies: Job titles mentioned
    - CTAs: "Built for sales teams" = Sales personas
    - Use cases: "Help marketing teams" = Marketing personas

    INFERENCE EXAMPLES:
    - "Built for revenue teams" → VP Sales, CRO, RevOps
    - "Marketing automation" → CMO, VP Marketing, Demand Gen
    - "Engineering workflows" → VP Engineering, Engineering Manager
    - "Executive dashboards" → C-suite (CEO, CFO, COO)

    HANDLING EDGE CASES:
    - Generic "teams" language: Infer most likely titles
    - Multiple levels: Extract both (e.g., "CMO" and "Marketing Manager")
    - Implicit only: Mark as "inferred" in notes

    Extract both explicit personas (directly mentioned) and implicit personas (inferred from content).
    """,
    output_schema=TargetPersonasExtractionResult
)
