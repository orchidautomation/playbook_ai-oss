"""
Workflow Input Models
Pydantic models for workflow input validation with automatic domain normalization.
Supports AgentOS API integration with structured input schemas.
"""

from pydantic import BaseModel, field_validator
from utils.workflow_helpers import normalize_domain


class WorkflowInput(BaseModel):
    """
    Input model for Octave Clone sales intelligence workflow.

    Automatically normalizes domain inputs to https:// format, accepting:
    - sendoso.com
    - www.sendoso.com
    - http://sendoso.com
    - https://sendoso.com

    All formats are normalized to: https://sendoso.com

    This model enables:
    1. Flexible user input (no need to type https://)
    2. AgentOS API integration with input validation
    3. Type safety for workflow parameters
    """

    vendor_domain: str
    prospect_domain: str

    @field_validator('vendor_domain', mode='before')
    @classmethod
    def normalize_vendor_domain(cls, v):
        """Normalize vendor domain to https:// format"""
        if not v:
            raise ValueError("vendor_domain is required")
        return normalize_domain(v)

    @field_validator('prospect_domain', mode='before')
    @classmethod
    def normalize_prospect_domain(cls, v):
        """Normalize prospect domain to https:// format"""
        if not v:
            raise ValueError("prospect_domain is required")
        return normalize_domain(v)

    def to_workflow_dict(self) -> dict:
        """
        Convert to dictionary format expected by Agno workflow.

        Returns:
            Dict with vendor_domain and prospect_domain keys
        """
        return {
            "vendor_domain": self.vendor_domain,
            "prospect_domain": self.prospect_domain
        }


# Example usage:
# from models.workflow_input import WorkflowInput
#
# # User can provide flexible input
# user_input = WorkflowInput(
#     vendor_domain="sendoso.com",           # Auto-normalized to https://sendoso.com
#     prospect_domain="www.octavehq.com"     # Auto-normalized to https://octavehq.com
# )
#
# # Use with workflow
# workflow.print_response(input=user_input.to_workflow_dict(), stream=True)
