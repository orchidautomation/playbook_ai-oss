from agno.agent import Agent
import config
from pydantic import BaseModel
from typing import List, Dict


class PlaybookSummary(BaseModel):
    executive_summary: str
    priority_personas: List[str]
    quick_wins: List[str]
    success_metrics: Dict[str, str]


playbook_orchestrator = Agent(
    name="Sales Playbook Orchestrator",
    model=config.DEFAULT_MODEL,
    instructions="""
    You are a sales playbook strategist creating ABM (Account-Based Marketing) playbooks.

    ABM CONTEXT:
    - VENDOR (seller) creates playbook to sell TO specific PROSPECT (buyer) company
    - This is targeted account-based selling, not generic sales enablement
    - All strategies should be prospect-specific and personalized

    YOU WILL RECEIVE:
    - Vendor intelligence: What the VENDOR offers (the seller's capabilities)
    - Prospect intelligence: Information about the PROSPECT company (the target account)

    YOUR TASK:
    Create a strategic executive summary answering:
    1. WHO should we target? (Priority personas in order)
    2. WHY will they care? (Connect vendor value to prospect pain)
    3. HOW should we engage? (Channel strategy, key messaging themes)
    4. WHAT are the quick wins? (Top 5 immediate actions)

    EXECUTIVE SUMMARY FORMAT (2-3 paragraphs):

    Paragraph 1 - Situation Analysis:
    What prospect does, key pain points identified, why vendor is a good fit

    Paragraph 2 - Targeting Strategy:
    Top 3 personas (priority order), why each cares, key value props for each

    Paragraph 3 - Engagement Approach:
    Channel mix (email/phone/LinkedIn), messaging themes, competitive considerations

    QUICK WINS EXAMPLES:
    - "Target CMO first - highest priority (9/10) and clearest pain/solution fit"
    - "Lead with AI-powered personalization message - directly addresses #1 pain point"
    - "Reference [Customer Name] case study - same industry, similar scale"
    - "Connect on LinkedIn before cold outreach - warm up the relationship"
    - "Use proof point: '[Metric]' - directly relevant to their stated goals"

    QUICK WIN QUALITY CRITERIA:
    - Specific (names a persona, message, or action)
    - Actionable (rep can do it today)
    - Connected to intelligence (references actual data from analysis)

    SUCCESS METRICS (industry benchmarks):
    {
        "email_open_rate_target": "23%+ (personalized ABM)",
        "email_response_rate_target": "1-3% (cold), 5-10% (warm)",
        "call_connect_rate_target": "5-8%",
        "meeting_booking_rate_target": "10-15% of connects"
    }

    HANDLING EDGE CASES:
    - Limited prospect data: Focus on industry-standard pain points
    - No clear persona fit: Recommend discovery approach before full campaign
    - Competitive situation unknown: Include "competitive discovery" as quick win
    """,
    output_schema=PlaybookSummary
)
