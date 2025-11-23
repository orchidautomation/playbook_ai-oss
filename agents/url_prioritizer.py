"""
URL Prioritizer Agent
Selects the most valuable pages from vendor and prospect websites for intelligence gathering.
Uses OpenAI GPT-4o-mini for fast URL filtering (40-60% faster than gpt-4o).
"""

from agno.agent import Agent
from pydantic import BaseModel, Field
from typing import List
import config


class PrioritizedURL(BaseModel):
    """Single prioritized URL with metadata"""
    url: str
    page_type: str = Field(description="e.g., 'about', 'case_study', 'pricing', 'blog'")
    priority: int = Field(description="1 (highest) to 10 (lowest)")
    reasoning: str


class URLPrioritizationResult(BaseModel):
    """Result containing prioritized URLs for both vendor and prospect"""
    vendor_selected_urls: List[PrioritizedURL]
    prospect_selected_urls: List[PrioritizedURL]


url_prioritizer = Agent(
    name="Strategic URL Selector",
    model=config.FAST_MODEL,  # gpt-4o-mini: 40-60% faster!
    instructions="""
    You are a content strategist selecting the most valuable pages for B2B sales intelligence.

    Given lists of URLs from vendor and prospect websites, select the TOP 10-15 MOST VALUABLE pages for each.

    PRIORITIZE (with priority scores):
    - /about, /about-us, /company, /team, /leadership → Priority 1-2 (company context)
    - /products, /solutions, /platform, /features → Priority 1-2 (core offerings)
    - /customers, /case-studies, /success-stories → Priority 1-3 (social proof)
    - /pricing, /plans → Priority 2-3 (business model)
    - /industries, /use-cases → Priority 3-4 (market focus)
    - /blog (recent posts with dates) → Priority 5-7 (thought leadership)
    - /resources, /guides → Priority 6-8 (supplementary)

    AVOID:
    - Legal pages (/privacy, /terms, /legal, /cookies)
    - Career pages (/careers, /jobs, /join-us)
    - Support docs (/help, /docs, /support, /faq)
    - Login/signup pages (/login, /signup, /register)
    - Media/press pages (unless highly relevant)

    EXAMPLE PRIORITIZATION:
    Input URL: "https://acme.com/customers/enterprise-case-studies"
    Output:
    - page_type: "case_study"
    - priority: 2
    - reasoning: "Enterprise case studies provide proof points, metrics, and customer names for sales conversations"

    HANDLING EDGE CASES:
    - Small URL list (<10): Include all non-excluded pages
    - Ambiguous paths: Infer from URL structure (e.g., /solutions/sales likely = product page)
    - Duplicate content: Prefer specific pages over landing pages (e.g., /products/crm over /products)

    For each selected URL, provide:
    - page_type: Category of the page
    - priority: 1 (must have) to 10 (nice to have)
    - reasoning: Why this page is valuable for sales intelligence

    Return top 10-15 URLs per company, prioritized by value for sales conversations.
    """,
    output_schema=URLPrioritizationResult
)
