from pydantic import BaseModel, Field
from typing import List, Optional
from models.common import Source


class Offering(BaseModel):
    """Product or service offering"""
    name: str
    description: str
    features: List[str] = Field(default_factory=list)
    pricing_indicators: Optional[str] = None
    target_audience: Optional[str] = None
    sources: List[Source] = Field(default_factory=list)


class CaseStudy(BaseModel):
    """Customer success story"""
    customer_name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    challenge: str
    solution: str
    results: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)


class ProofPoint(BaseModel):
    """Testimonial, stat, or credibility indicator"""
    type: str = Field(description="testimonial, statistic, award, certification")
    content: str
    source_attribution: Optional[str] = None
    sources: List[Source] = Field(default_factory=list)


class ValueProposition(BaseModel):
    """Core value proposition"""
    statement: str
    benefits: List[str] = Field(default_factory=list)
    differentiation: Optional[str] = None
    target_persona: Optional[str] = None
    sources: List[Source] = Field(default_factory=list)


class ReferenceCustomer(BaseModel):
    """Customer reference"""
    name: str
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    relationship: str = Field(description="customer, partner, integration")
    sources: List[Source] = Field(default_factory=list)


class UseCase(BaseModel):
    """Use case or workflow solution"""
    title: str
    description: str
    target_persona: Optional[str] = None
    target_industry: Optional[str] = None
    problems_solved: List[str] = Field(default_factory=list)
    key_features_used: List[str] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)


class TargetPersona(BaseModel):
    """Target buyer persona"""
    title: str
    department: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)


class Differentiator(BaseModel):
    """Competitive differentiator"""
    category: str = Field(description="feature, approach, market_position, technology")
    statement: str
    vs_alternative: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)


class VendorElements(BaseModel):
    """Complete vendor GTM element library"""
    offerings: List[Offering] = Field(default_factory=list)
    case_studies: List[CaseStudy] = Field(default_factory=list)
    proof_points: List[ProofPoint] = Field(default_factory=list)
    value_propositions: List[ValueProposition] = Field(default_factory=list)
    reference_customers: List[ReferenceCustomer] = Field(default_factory=list)
    use_cases: List[UseCase] = Field(default_factory=list)
    target_personas: List[TargetPersona] = Field(default_factory=list)
    differentiators: List[Differentiator] = Field(default_factory=list)
