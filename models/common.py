from pydantic import BaseModel, Field
from typing import Optional


class Source(BaseModel):
    """Reference to where information was found"""
    url: str
    page_type: str = Field(description="e.g., 'homepage', 'case_study', 'about', 'pricing'")
    excerpt: Optional[str] = Field(default=None, description="Relevant excerpt from the page")
