"""
Octave Clone MVP - Phase 1 & 2 Workflow
Intelligence gathering and vendor element extraction pipeline.
"""

from agno.workflow import Workflow, Step, Parallel

# Import Phase 1 step executors
from steps.step1_domain_validation import validate_vendor_domain, validate_prospect_domain
from steps.step2_homepage_scraping import scrape_vendor_homepage, scrape_prospect_homepage
from steps.step3_initial_analysis import analyze_vendor_homepage, analyze_prospect_homepage
from steps.step4_url_prioritization import prioritize_urls
from steps.step5_batch_scraping import batch_scrape_selected_pages

# Import Phase 2 step executors (Step 6)
from steps.step6_vendor_extraction import (
    extract_offerings,
    extract_case_studies,
    extract_proof_points,
    extract_value_props,
    extract_customers,
    extract_use_cases,
    extract_personas,
    extract_differentiators
)


# Phase 1 Workflow (Steps 1-5)
phase1_workflow = Workflow(
    name="Phase 1 - Intelligence Gathering",
    description="Validate domains, scrape homepages, prioritize URLs, and batch scrape content",
    steps=[
        # Step 1: Parallel domain validation
        Parallel(
            Step(name="validate_vendor", executor=validate_vendor_domain),
            Step(name="validate_prospect", executor=validate_prospect_domain),
            name="parallel_validation"
        ),

        # Step 2: Parallel homepage scraping
        Parallel(
            Step(name="scrape_vendor_home", executor=scrape_vendor_homepage),
            Step(name="scrape_prospect_home", executor=scrape_prospect_homepage),
            name="parallel_homepage_scraping"
        ),

        # Step 3: Parallel homepage analysis
        Parallel(
            Step(name="analyze_vendor_home", executor=analyze_vendor_homepage),
            Step(name="analyze_prospect_home", executor=analyze_prospect_homepage),
            name="parallel_homepage_analysis"
        ),

        # Step 4: URL prioritization
        Step(name="prioritize_urls", executor=prioritize_urls),

        # Step 5: Batch scraping
        Step(name="batch_scrape", executor=batch_scrape_selected_pages)
    ]
)


# Phase 1-2 Combined Workflow (Steps 1-6)
phase1_2_workflow = Workflow(
    name="Phase 1-2 - Intelligence Gathering & Vendor Extraction",
    description="Gather intelligence and extract vendor GTM elements with 8 parallel specialists",
    steps=[
        # Step 1: Parallel domain validation
        Parallel(
            Step(name="validate_vendor", executor=validate_vendor_domain),
            Step(name="validate_prospect", executor=validate_prospect_domain),
            name="parallel_validation"
        ),

        # Step 2: Parallel homepage scraping
        Parallel(
            Step(name="scrape_vendor_home", executor=scrape_vendor_homepage),
            Step(name="scrape_prospect_home", executor=scrape_prospect_homepage),
            name="parallel_homepage_scraping"
        ),

        # Step 3: Parallel homepage analysis
        Parallel(
            Step(name="analyze_vendor_home", executor=analyze_vendor_homepage),
            Step(name="analyze_prospect_home", executor=analyze_prospect_homepage),
            name="parallel_homepage_analysis"
        ),

        # Step 4: URL prioritization
        Step(name="prioritize_urls", executor=prioritize_urls),

        # Step 5: Batch scraping
        Step(name="batch_scrape", executor=batch_scrape_selected_pages),

        # Step 6: Vendor element extraction (8 parallel specialists)
        Parallel(
            Step(name="extract_offerings", executor=extract_offerings),
            Step(name="extract_case_studies", executor=extract_case_studies),
            Step(name="extract_proof_points", executor=extract_proof_points),
            Step(name="extract_value_props", executor=extract_value_props),
            Step(name="extract_customers", executor=extract_customers),
            Step(name="extract_use_cases", executor=extract_use_cases),
            Step(name="extract_personas", executor=extract_personas),
            Step(name="extract_differentiators", executor=extract_differentiators),
            name="vendor_element_extraction"
        )
    ]
)
