"""
Workflow Helper Functions
Helper functions for Agno workflow step validation and error handling.
Implements fail-fast validation patterns from CLAUDE.md preferences.
"""

from agno.workflow.types import StepInput, StepOutput
from typing import Dict, Tuple, Optional, Any
import ast


def get_parallel_step_content(
    step_input: StepInput,
    parallel_block_name: str,
    step_name: str
) -> Optional[Dict]:
    """
    Safely get content from a parallel block step with automatic deserialization.

    Agno stores parallel block step outputs as string representations when accessed
    by later steps, so this helper automatically deserializes them.

    Args:
        step_input: StepInput object
        parallel_block_name: Name of the parallel block (e.g., "parallel_validation")
        step_name: Name of the step within the parallel block (e.g., "validate_vendor")

    Returns:
        Dict content of the step, or None if not found

    Example:
        vendor_data = get_parallel_step_content(step_input, "parallel_validation", "validate_vendor")
    """
    # Get the parallel block
    parallel_block = step_input.get_step_content(parallel_block_name)

    if not parallel_block:
        return None

    # Handle if parallel_block itself is a string (shouldn't happen but be safe)
    if isinstance(parallel_block, str):
        try:
            parallel_block = ast.literal_eval(parallel_block)
        except (ValueError, SyntaxError):
            return None

    if not isinstance(parallel_block, dict):
        return None

    # Get the specific step content
    step_content = parallel_block.get(step_name)

    if not step_content:
        return None

    # Deserialize if it's a string (Agno stores parallel outputs as strings)
    if isinstance(step_content, str):
        try:
            step_content = ast.literal_eval(step_content)
        except (ValueError, SyntaxError, NameError, TypeError) as e:
            # If deserialization fails, log and return None
            print(f"❌ Failed to deserialize step content from {parallel_block_name}.{step_name}: {type(e).__name__}: {str(e)[:100]}")
            print(f"   Content preview: {step_content[:200]}...")
            return None

    # Ensure we're returning a dict
    if not isinstance(step_content, dict):
        print(f"❌ Step content from {parallel_block_name}.{step_name} is not a dict after deserialization: {type(step_content).__name__}")
        return None

    return step_content


def extract_domains_from_input(step_input: StepInput) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract vendor and prospect domains from workflow input.

    Args:
        step_input: StepInput object

    Returns:
        Tuple of (vendor_domain, prospect_domain)
    """
    vendor_domain = step_input.input.get("vendor_domain")
    prospect_domain = step_input.input.get("prospect_domain")
    return vendor_domain, prospect_domain


def extract_validated_urls_or_fail(
    step_input: StepInput,
    vendor_step_name: str = "validate_vendor",
    prospect_step_name: str = "validate_prospect"
) -> Tuple[Optional[Dict], Optional[Dict]]:
    """
    Extract and validate URL data from parallel domain validation steps.
    Returns None if validation fails (caller should check and fail fast).

    Args:
        step_input: StepInput object
        vendor_step_name: Name of vendor validation step
        prospect_step_name: Name of prospect validation step

    Returns:
        Tuple of (vendor_data, prospect_data) or (None, None) if validation fails
    """
    # Get data from parallel validation steps
    vendor_data = step_input.get_step_content(vendor_step_name)
    prospect_data = step_input.get_step_content(prospect_step_name)

    # Validate vendor data
    if not vendor_data or not isinstance(vendor_data, dict):
        return None, None

    if "error" in vendor_data or not vendor_data.get("vendor_urls"):
        return None, None

    # Validate prospect data
    if not prospect_data or not isinstance(prospect_data, dict):
        return None, None

    if "error" in prospect_data or not prospect_data.get("prospect_urls"):
        return None, None

    return vendor_data, prospect_data


def normalize_domain(domain: str) -> str:
    """
    Normalize domain to https:// format, accepting flexible inputs.

    Handles:
    - sendoso.com → https://sendoso.com
    - www.sendoso.com → https://sendoso.com
    - http://sendoso.com → https://sendoso.com
    - https://sendoso.com → https://sendoso.com (unchanged)

    Args:
        domain: Domain string in any format

    Returns:
        Normalized domain with https:// prefix and www. removed

    Raises:
        ValueError: If domain is invalid or empty
    """
    if not domain or not isinstance(domain, str):
        raise ValueError(f"Invalid domain: {domain}")

    domain = domain.strip()

    # After stripping, check if empty
    if not domain:
        raise ValueError(f"Invalid domain: empty or whitespace only")

    # Remove www. prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]

    # Add https:// if no protocol specified
    if not domain.startswith(('http://', 'https://')):
        domain = f'https://{domain}'

    # Upgrade http:// to https://
    elif domain.startswith('http://'):
        domain = domain.replace('http://', 'https://', 1)

    # Additional cleanup: remove www. after protocol if present
    domain = domain.replace('://www.', '://')

    return domain


def validate_single_domain(domain: str, domain_type: str = "domain") -> Tuple[bool, str]:
    """
    Validate a single domain format.

    Note: This function now accepts flexible domain formats and normalizes them.
    Use normalize_domain() first to handle user inputs like "sendoso.com".

    Args:
        domain: Domain string to validate (should be normalized first)
        domain_type: Type of domain (for error messages)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not domain:
        return False, f"No {domain_type} provided"

    if not isinstance(domain, str):
        return False, f"{domain_type} must be a string"

    # Basic URL format check
    if not domain.startswith(("http://", "https://")):
        return False, f"{domain_type} must start with http:// or https://"

    return True, ""


def create_error_response(error_msg: str, stop: bool = True) -> StepOutput:
    """
    Create a standardized error StepOutput.

    Args:
        error_msg: Error message
        stop: Whether to stop the workflow (default: True for fail-fast)

    Returns:
        StepOutput with error content
    """
    print(f"\n❌ {error_msg}")
    return StepOutput(
        content={"error": error_msg},
        success=False,
        stop=stop
    )


def create_success_response(content: Dict[str, Any], success_msg: str = None) -> StepOutput:
    """
    Create a standardized success StepOutput.

    Args:
        content: Content dictionary to return
        success_msg: Optional success message to print

    Returns:
        StepOutput with content
    """
    if success_msg:
        print(f"\n✅ {success_msg}")

    return StepOutput(
        content=content,
        success=True,
        stop=False
    )


def validate_previous_step_data(
    step_input: StepInput,
    required_keys: list,
    step_name: str = "previous step"
) -> Tuple[bool, Optional[Dict], str]:
    """
    Validate data from previous step contains required keys.

    Args:
        step_input: StepInput object
        required_keys: List of required keys in previous step content
        step_name: Name of the step being validated (for error messages)

    Returns:
        Tuple of (is_valid, data, error_message)
    """
    previous_data = step_input.previous_step_content

    if not previous_data or not isinstance(previous_data, dict):
        return False, None, f"No valid data from {step_name}"

    # Check for error in previous step
    if "error" in previous_data:
        return False, None, f"{step_name} returned error: {previous_data['error']}"

    # Check for required keys
    missing_keys = [key for key in required_keys if key not in previous_data]
    if missing_keys:
        return False, None, f"{step_name} missing required fields: {', '.join(missing_keys)}"

    return True, previous_data, ""


def safe_get_step_content(
    step_input: StepInput,
    step_name: str,
    required_keys: list = None
) -> Tuple[bool, Optional[Dict], str]:
    """
    Safely get content from a named step with validation.

    Args:
        step_input: StepInput object
        step_name: Name of step to get content from
        required_keys: Optional list of required keys

    Returns:
        Tuple of (is_valid, data, error_message)
    """
    data = step_input.get_step_content(step_name)

    if not data or not isinstance(data, dict):
        return False, None, f"No valid data from step '{step_name}'"

    # Check for error in step
    if "error" in data:
        return False, None, f"Step '{step_name}' returned error: {data['error']}"

    # Check for required keys if provided
    if required_keys:
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            return False, None, f"Step '{step_name}' missing required fields: {', '.join(missing_keys)}"

    return True, data, ""
