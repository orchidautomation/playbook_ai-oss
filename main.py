"""
Octave Clone MVP - Main Entry Point
CLI for running the complete sales intelligence pipeline (all 4 phases).

Usage:
    python main.py <vendor_domain> <prospect_domain>

Examples (all formats accepted):
    python main.py octavehq.com sendoso.com
    python main.py https://octavehq.com https://sendoso.com
    python main.py www.octavehq.com www.sendoso.com

All domain formats are automatically normalized to https://
"""

import sys
import json
import os
from datetime import datetime
from agno.workflow import Workflow, Step, Parallel
from models.workflow_input import WorkflowInput

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

# Import Phase 3 step executors (Step 7)
from steps.step7_prospect_analysis import (
    analyze_company_profile,
    analyze_pain_points,
    identify_buyer_personas
)

# Import Phase 4 step executors (Step 8)
from steps.step8_playbook_generation import (
    generate_playbook_summary,
    generate_email_sequences,
    generate_talk_tracks,
    generate_battle_cards,
    assemble_final_playbook
)


# Complete Sales Intelligence Pipeline - All 4 Phases (8 Steps)
workflow = Workflow(
    name="Octave Clone - Complete Sales Intelligence Pipeline",
    description="End-to-end: Intelligence, vendor extraction, prospect analysis, and actionable playbooks",
    input_schema=WorkflowInput,  # AgentOS API support with automatic domain normalization
    steps=[
        # Phase 1: Intelligence Gathering (Steps 1-5)

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

        # Phase 2: Vendor Extraction (Step 6)

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
        ),

        # Phase 3: Prospect Analysis (Step 7)

        # Step 7a: Prospect context analysis (2 parallel analysts)
        Parallel(
            Step(name="analyze_company", executor=analyze_company_profile),
            Step(name="analyze_pain_points", executor=analyze_pain_points),
            name="prospect_context_analysis"
        ),

        # Step 7b: Buyer persona identification (uses vendor + prospect data)
        Step(name="identify_buyer_personas", executor=identify_buyer_personas),

        # Phase 4: Playbook Generation (Step 8)

        # Step 8a: Playbook summary (sequential - needs all Phase 1-3 data)
        Step(name="generate_playbook_summary", executor=generate_playbook_summary),

        # Step 8b-d: Playbook components (3 parallel specialists)
        Parallel(
            Step(name="generate_email_sequences", executor=generate_email_sequences),
            Step(name="generate_talk_tracks", executor=generate_talk_tracks),
            Step(name="generate_battle_cards", executor=generate_battle_cards),
            name="playbook_component_generation"
        ),

        # Step 8e: Final playbook assembly
        Step(name="assemble_final_playbook", executor=assemble_final_playbook)
    ]
)


def main():
    """Main entry point for complete sales intelligence pipeline."""

    # Parse command line arguments
    if len(sys.argv) < 3:
        print("=" * 80)
        print("OCTAVE CLONE MVP - COMPLETE SALES INTELLIGENCE PIPELINE")
        print("=" * 80)
        print("\nUsage: python main.py <vendor_domain> <prospect_domain>")
        print("\nExamples (all formats work):")
        print("  python main.py octavehq.com sendoso.com")
        print("  python main.py https://octavehq.com https://sendoso.com")
        print("  python main.py www.octavehq.com www.sendoso.com")
        print("\nThis runs all 4 phases:")
        print("  Phase 1: Intelligence Gathering (Steps 1-5)")
        print("  Phase 2: Vendor GTM Extraction (Step 6)")
        print("  Phase 3: Prospect Analysis (Step 7)")
        print("  Phase 4: Sales Playbook Generation (Step 8)")
        print("\n" + "=" * 80)
        sys.exit(1)

    # Normalize domains using Pydantic validation
    # This accepts flexible inputs: sendoso.com, www.sendoso.com, https://sendoso.com
    try:
        validated_input = WorkflowInput(
            vendor_domain=sys.argv[1],
            prospect_domain=sys.argv[2]
        )
        vendor_domain = validated_input.vendor_domain
        prospect_domain = validated_input.prospect_domain
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ INVALID DOMAIN INPUT")
        print("=" * 80)
        print(f"\nError: {str(e)}")
        print("\nPlease provide valid domain names.")
        print("\nExamples:")
        print("  python main.py octavehq.com sendoso.com")
        print("  python main.py https://octavehq.com https://sendoso.com")
        print("=" * 80)
        sys.exit(1)

    # Display header
    print("\n" + "=" * 80)
    print("OCTAVE CLONE MVP - COMPLETE SALES INTELLIGENCE PIPELINE")
    print("=" * 80)
    print(f"\n📊 Vendor:   {vendor_domain}")
    print(f"🎯 Prospect: {prospect_domain}\n")
    print("=" * 80)
    print("\n🚀 Starting Complete Workflow (All 4 Phases)...")
    print("   Phase 1: Intelligence Gathering")
    print("   Phase 2: Vendor GTM Extraction")
    print("   Phase 3: Prospect Analysis")
    print("   Phase 4: Sales Playbook Generation")
    print("\n" + "=" * 80 + "\n")

    # Prepare workflow input
    workflow_input = {
        "vendor_domain": vendor_domain,
        "prospect_domain": prospect_domain
    }

    try:
        # Run workflow with Agno TUI and streaming
        print("🔥 Workflow executing with real-time visualization...\n")
        workflow.print_response(input=workflow_input, stream=True)

        # Also get the result for saving
        result = workflow.run(input=workflow_input)

        # Check if workflow was successful
        if not result or not result.content:
            print("\n" + "=" * 80)
            print("❌ WORKFLOW FAILED")
            print("=" * 80)
            print("\nNo result returned from workflow.")
            sys.exit(1)

        # Save results in organized directory structure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = f"output/runs/{timestamp}"
        os.makedirs(run_dir, exist_ok=True)

        # Save metadata about the run
        metadata = {
            "timestamp": timestamp,
            "vendor_domain": vendor_domain,
            "prospect_domain": prospect_domain,
            "workflow_name": workflow.name,
            "completed_at": datetime.now().isoformat()
        }

        with open(f"{run_dir}/metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Save Step 6: Vendor element extraction (all 8 extractors)
        try:
            step6_outputs = {}
            extractor_names = [
                "extract_offerings",
                "extract_case_studies",
                "extract_proof_points",
                "extract_value_props",
                "extract_customers",
                "extract_use_cases",
                "extract_personas",
                "extract_differentiators"
            ]

            for extractor_name in extractor_names:
                try:
                    content = result.get_parallel_step_content("vendor_element_extraction", extractor_name)
                    if content:
                        step6_outputs[extractor_name] = content
                except:
                    pass

            if step6_outputs:
                with open(f"{run_dir}/step6_vendor_extraction.json", "w") as f:
                    json.dump(step6_outputs, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save Step 6 output: {e}")

        # Save Step 7: Prospect analysis (all 3 analysts)
        try:
            step7_outputs = {}

            # Step 7a: Parallel analysts
            analyst_names = ["analyze_company", "analyze_pain_points"]
            for analyst_name in analyst_names:
                try:
                    content = result.get_parallel_step_content("prospect_context_analysis", analyst_name)
                    if content:
                        step7_outputs[analyst_name] = content
                except:
                    pass

            # Step 7b: Buyer personas (sequential)
            try:
                personas_content = result.get_step_content("identify_buyer_personas")
                if personas_content:
                    step7_outputs["identify_buyer_personas"] = personas_content
            except:
                pass

            if step7_outputs:
                with open(f"{run_dir}/step7_prospect_analysis.json", "w") as f:
                    json.dump(step7_outputs, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save Step 7 output: {e}")

        # Save Step 8: Playbook generation (all components)
        try:
            step8_outputs = {}

            # Step 8a: Summary
            try:
                summary = result.get_step_content("generate_playbook_summary")
                if summary:
                    step8_outputs["playbook_summary"] = summary
            except:
                pass

            # Step 8b-d: Parallel components
            component_names = [
                "generate_email_sequences",
                "generate_talk_tracks",
                "generate_battle_cards"
            ]
            for component_name in component_names:
                try:
                    content = result.get_parallel_step_content("playbook_component_generation", component_name)
                    if content:
                        step8_outputs[component_name] = content
                except:
                    pass

            # Step 8e: Final assembly
            try:
                final_playbook = result.get_step_content("assemble_final_playbook")
                if final_playbook:
                    step8_outputs["final_playbook"] = final_playbook
            except:
                pass

            if step8_outputs:
                with open(f"{run_dir}/step8_playbook_generation.json", "w") as f:
                    json.dump(step8_outputs, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save Step 8 output: {e}")

        # Also save the complete final output for backwards compatibility
        output_filename = f"{run_dir}/complete_output.json"
        with open(output_filename, "w") as f:
            json.dump(result.content, f, indent=2)

        # Display success message
        print("\n" + "=" * 80)
        print("✅ COMPLETE WORKFLOW FINISHED!")
        print("=" * 80)

        # Print summary
        content = result.content
        print(f"\n📁 All outputs saved to: {run_dir}/")
        print(f"   • metadata.json - Run information")
        print(f"   • step6_vendor_extraction.json - Vendor GTM elements")
        print(f"   • step7_prospect_analysis.json - Prospect insights")
        print(f"   • step8_playbook_generation.json - Playbook components")
        print(f"   • complete_output.json - Final assembled output\n")
        print("📊 Pipeline Summary:")

        # Phase 1 stats
        print("\n  Phase 1 - Intelligence Gathering:")
        print(f"    • Vendor URLs scraped: {len(content.get('vendor_content', {}))} pages")
        print(f"    • Prospect URLs scraped: {len(content.get('prospect_content', {}))} pages")

        stats = content.get('stats', {})
        if stats:
            print(f"    • Vendor content: {stats.get('vendor_chars', 0):,} characters")
            print(f"    • Prospect content: {stats.get('prospect_chars', 0):,} characters")

        # Phase 2-4 indicators
        if 'vendor_elements' in content:
            print("\n  Phase 2 - Vendor GTM Extraction:")
            print(f"    • Extracted {len(content.get('vendor_elements', {}))} GTM elements")

        if 'buyer_personas' in content:
            print("\n  Phase 3 - Prospect Analysis:")
            print(f"    • Identified {len(content.get('buyer_personas', []))} buyer personas")

        if 'sales_playbook' in content:
            print("\n  Phase 4 - Sales Playbook:")
            playbook = content.get('sales_playbook', {})
            if 'battle_cards' in playbook:
                print(f"    • Battle cards: ✅")
            if 'email_sequences' in playbook:
                print(f"    • Email sequences: ✅")
            if 'talk_tracks' in playbook:
                print(f"    • Talk tracks: ✅")

        print("\n" + "=" * 80)
        print("🎉 All phases complete! Sales playbook ready.")
        print("=" * 80 + "\n")

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ WORKFLOW ERROR")
        print("=" * 80)
        print(f"\nError: {str(e)}")
        print("\nPlease check your API keys in .env and try again.")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
