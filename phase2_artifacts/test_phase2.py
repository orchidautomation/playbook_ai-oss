"""
Test Phase 2 - Vendor Element Extraction
Run Phase 1-2 combined workflow end-to-end
"""

from workflow import phase1_2_workflow
import json
from datetime import datetime


def main():
    print("=" * 80)
    print("OCTAVE CLONE MVP - PHASE 1-2 TEST")
    print("Intelligence Gathering + Vendor Element Extraction")
    print("=" * 80)

    # Test with Octave (vendor) and Sendoso (prospect)
    workflow_input = {
        "vendor_domain": "https://octavehq.com",
        "prospect_domain": "https://sendoso.com"
    }

    print(f"\nVendor:   {workflow_input['vendor_domain']}")
    print(f"Prospect: {workflow_input['prospect_domain']}\n")
    print("=" * 80)
    print("\nStarting workflow execution...\n")

    # Run workflow
    start_time = datetime.now()
    result = phase1_2_workflow.run(input=workflow_input)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 80)
    print("PHASE 1-2 COMPLETE")
    print("=" * 80)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"phase2_output_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(result.content, f, indent=2)

    print(f"\n✅ Results saved to {output_file}")
    print(f"⏱️  Total execution time: {duration:.1f} seconds")

    # Print extraction summary
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)

    content = result.content

    # Phase 1 stats
    vendor_urls_scraped = len(content.get("vendor_content", {}).get("vendor_content", {}))
    prospect_urls_scraped = len(content.get("prospect_content", {}).get("prospect_content", {}))

    print(f"\n📊 Phase 1 (Intelligence Gathering):")
    print(f"   Vendor URLs scraped: {vendor_urls_scraped}")
    print(f"   Prospect URLs scraped: {prospect_urls_scraped}")

    # Phase 2 stats
    print(f"\n📊 Phase 2 (Vendor Element Extraction):")

    # Get extraction results from parallel block
    offerings = content.get("extract_offerings", {}).get("offerings", [])
    case_studies = content.get("extract_case_studies", {}).get("case_studies", [])
    proof_points = content.get("extract_proof_points", {}).get("proof_points", [])
    value_props = content.get("extract_value_props", {}).get("value_propositions", [])
    customers = content.get("extract_customers", {}).get("reference_customers", [])
    use_cases = content.get("extract_use_cases", {}).get("use_cases", [])
    personas = content.get("extract_personas", {}).get("target_personas", [])
    differentiators = content.get("extract_differentiators", {}).get("differentiators", [])

    print(f"   🔍 Offerings extracted: {len(offerings)}")
    print(f"   📚 Case studies extracted: {len(case_studies)}")
    print(f"   🏆 Proof points extracted: {len(proof_points)}")
    print(f"   💎 Value propositions extracted: {len(value_props)}")
    print(f"   🏢 Reference customers extracted: {len(customers)}")
    print(f"   🎯 Use cases extracted: {len(use_cases)}")
    print(f"   👥 Target personas extracted: {len(personas)}")
    print(f"   ⚡ Differentiators extracted: {len(differentiators)}")

    total_elements = (
        len(offerings) + len(case_studies) + len(proof_points) +
        len(value_props) + len(customers) + len(use_cases) +
        len(personas) + len(differentiators)
    )
    print(f"\n   📊 Total vendor elements extracted: {total_elements}")

    print("\n" + "=" * 80)
    print(f"✅ Phase 2 test complete! Review results in {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
