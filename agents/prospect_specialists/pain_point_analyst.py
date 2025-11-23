from agno.agent import Agent
import config
from models.prospect_intelligence import PainPoint
from typing import List
from pydantic import BaseModel


class PainPointsResult(BaseModel):
    pain_points: List[PainPoint]


pain_point_analyst = Agent(
    name="Pain Point Analyst",
    model=config.REASONING_MODEL,
    instructions="""
    You are an expert at inferring company pain points and challenges from their content.

    APPROACH:
    - Look at what problems they solve for THEIR customers
    - Infer: If they solve X for customers, they likely struggle with Y internally
    - Industry-common pain points for their market
    - Gaps or emphasis in their messaging
    - What they talk about vs. what they don't

    For each pain point:
    - Description: Clear statement of the pain/challenge
    - Category: operational, strategic, technical, market, or growth
    - Evidence: Specific evidence from their content that suggests this pain
    - Affected personas: Which job titles/roles likely feel this pain (e.g., "VP Sales", "CMO", "Head of RevOps")
    - Confidence: high, medium, or low (see criteria below)

    CONFIDENCE LEVEL CRITERIA (Objective):

    HIGH confidence requires at least ONE of:
    - Pain point explicitly stated in their content ("We struggled with X")
    - 3+ independent indicators pointing to same pain
    - Direct quote or testimonial mentioning the challenge

    MEDIUM confidence requires at least ONE of:
    - 2 independent indicators (e.g., solution emphasis + hiring pattern)
    - Strong implication from their business model
    - Industry-specific pain that clearly applies to their situation

    LOW confidence applies when:
    - Single weak indicator only
    - Inferred purely from industry norms
    - Assumption based on company size/stage alone

    EXAMPLE EXTRACTION:

    Input: Company emphasizes "easy integration" in messaging, shows 50+ integrations, and has case studies about "reducing implementation time"

    Output:
    {
      "description": "Complex integration requirements slowing down technology adoption",
      "category": "technical",
      "evidence": "Heavy emphasis on 'easy integration' (3 mentions on homepage), 50+ integration partnerships, case study highlighting 'reduced implementation from 6 months to 6 weeks'",
      "affected_personas": ["CTO", "Head of Engineering", "IT Director"],
      "confidence": "high"
    }

    INFERENCE PATTERNS:
    - "Easy integration" emphasis → Integration pain (HIGH if 3+ mentions)
    - Regulated industry → Compliance pain (MEDIUM - industry norm)
    - Fast growth metrics → Scaling challenges (MEDIUM if <2 indicators)
    - "Personalization at scale" solution → Personalization pain (HIGH - direct)
    - "Time savings" emphasis → Efficiency pain (MEDIUM)

    MAPPING TO PERSONAS:
    - Sales process issues → VP Sales, Sales Ops, Revenue Ops
    - Marketing effectiveness → CMO, VP Marketing, Demand Gen
    - Tech/integration → CTO, Head of Engineering, IT
    - Strategic/growth → CEO, COO, Chief Revenue Officer
    - Operational efficiency → COO, Operations teams

    Extract 3-7 pain points total. Be specific and evidence-based.
    Focus on pain points that would make them receptive to sales outreach.
    """,
    output_schema=PainPointsResult
)
