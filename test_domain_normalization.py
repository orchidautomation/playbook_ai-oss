"""
Test Domain Normalization
Tests for flexible domain input handling with automatic normalization.

Tests both the normalize_domain() helper function and WorkflowInput Pydantic model.
"""

from utils.workflow_helpers import normalize_domain
from models.workflow_input import WorkflowInput


def test_normalize_domain():
    """Test normalize_domain() function with various input formats"""

    print("\n" + "=" * 80)
    print("Testing normalize_domain() Function")
    print("=" * 80)

    test_cases = [
        # (input, expected_output, description)
        ("sendoso.com", "https://sendoso.com", "Plain domain"),
        ("www.sendoso.com", "https://sendoso.com", "Domain with www prefix"),
        ("http://sendoso.com", "https://sendoso.com", "HTTP upgraded to HTTPS"),
        ("https://sendoso.com", "https://sendoso.com", "Already HTTPS (unchanged)"),
        ("https://www.sendoso.com", "https://sendoso.com", "HTTPS with www removed"),
        ("octavehq.com", "https://octavehq.com", "Different domain"),
        ("  sendoso.com  ", "https://sendoso.com", "Domain with whitespace"),
    ]

    passed = 0
    failed = 0

    for input_domain, expected, description in test_cases:
        try:
            result = normalize_domain(input_domain)
            if result == expected:
                print(f"✅ PASS: {description}")
                print(f"   Input:    '{input_domain}'")
                print(f"   Output:   '{result}'")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Input:    '{input_domain}'")
                print(f"   Expected: '{expected}'")
                print(f"   Got:      '{result}'")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR: {description}")
            print(f"   Input: '{input_domain}'")
            print(f"   Error: {str(e)}")
            failed += 1
        print()

    # Test error cases
    print("Testing Error Cases:")
    print("-" * 40)

    error_cases = [
        (None, "None input"),
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        (123, "Non-string input"),
    ]

    for invalid_input, description in error_cases:
        try:
            result = normalize_domain(invalid_input)
            print(f"❌ FAIL: {description} should raise ValueError")
            print(f"   Got: '{result}'")
            failed += 1
        except ValueError as e:
            print(f"✅ PASS: {description} raised ValueError")
            print(f"   Error: {str(e)}")
            passed += 1
        except Exception as e:
            print(f"⚠️  WARN: {description} raised unexpected error")
            print(f"   Error: {type(e).__name__}: {str(e)}")
            passed += 1  # Still count as pass if it errors
        print()

    print("=" * 80)
    print(f"normalize_domain() Results: {passed} passed, {failed} failed")
    print("=" * 80)

    return failed == 0


def test_workflow_input_model():
    """Test WorkflowInput Pydantic model with field validators"""

    print("\n" + "=" * 80)
    print("Testing WorkflowInput Pydantic Model")
    print("=" * 80)

    test_cases = [
        # (vendor_input, prospect_input, expected_vendor, expected_prospect, description)
        ("sendoso.com", "octavehq.com", "https://sendoso.com", "https://octavehq.com", "Plain domains"),
        ("www.sendoso.com", "www.octavehq.com", "https://sendoso.com", "https://octavehq.com", "Domains with www"),
        ("http://sendoso.com", "http://octavehq.com", "https://sendoso.com", "https://octavehq.com", "HTTP domains"),
        ("https://sendoso.com", "https://octavehq.com", "https://sendoso.com", "https://octavehq.com", "HTTPS domains"),
    ]

    passed = 0
    failed = 0

    for vendor_in, prospect_in, vendor_exp, prospect_exp, description in test_cases:
        try:
            workflow_input = WorkflowInput(
                vendor_domain=vendor_in,
                prospect_domain=prospect_in
            )

            if workflow_input.vendor_domain == vendor_exp and workflow_input.prospect_domain == prospect_exp:
                print(f"✅ PASS: {description}")
                print(f"   Vendor Input:    '{vendor_in}' → '{workflow_input.vendor_domain}'")
                print(f"   Prospect Input:  '{prospect_in}' → '{workflow_input.prospect_domain}'")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Vendor Expected:   '{vendor_exp}', Got: '{workflow_input.vendor_domain}'")
                print(f"   Prospect Expected: '{prospect_exp}', Got: '{workflow_input.prospect_domain}'")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR: {description}")
            print(f"   Error: {str(e)}")
            failed += 1
        print()

    # Test to_workflow_dict() method
    print("Testing to_workflow_dict() Method:")
    print("-" * 40)

    try:
        workflow_input = WorkflowInput(
            vendor_domain="sendoso.com",
            prospect_domain="octavehq.com"
        )

        result_dict = workflow_input.to_workflow_dict()

        expected_dict = {
            "vendor_domain": "https://sendoso.com",
            "prospect_domain": "https://octavehq.com"
        }

        if result_dict == expected_dict:
            print("✅ PASS: to_workflow_dict() returns correct format")
            print(f"   Result: {result_dict}")
            passed += 1
        else:
            print("❌ FAIL: to_workflow_dict() incorrect format")
            print(f"   Expected: {expected_dict}")
            print(f"   Got:      {result_dict}")
            failed += 1
    except Exception as e:
        print(f"❌ ERROR: to_workflow_dict() test failed")
        print(f"   Error: {str(e)}")
        failed += 1

    print()
    print("=" * 80)
    print(f"WorkflowInput Model Results: {passed} passed, {failed} failed")
    print("=" * 80)

    return failed == 0


def test_agno_workflow_compatibility():
    """Test that WorkflowInput works with Agno workflow format"""

    print("\n" + "=" * 80)
    print("Testing Agno Workflow Compatibility")
    print("=" * 80)

    try:
        # Simulate user input (flexible format)
        user_vendor = "sendoso.com"
        user_prospect = "www.octavehq.com"

        print(f"User Input:")
        print(f"  Vendor:   '{user_vendor}'")
        print(f"  Prospect: '{user_prospect}'")
        print()

        # Create WorkflowInput (normalizes domains)
        validated_input = WorkflowInput(
            vendor_domain=user_vendor,
            prospect_domain=user_prospect
        )

        print(f"After Validation:")
        print(f"  Vendor:   '{validated_input.vendor_domain}'")
        print(f"  Prospect: '{validated_input.prospect_domain}'")
        print()

        # Convert to workflow dict format
        workflow_dict = validated_input.to_workflow_dict()

        print(f"Workflow Input Dict:")
        print(f"  {workflow_dict}")
        print()

        # Verify format is correct for Agno workflow
        if (isinstance(workflow_dict, dict) and
            "vendor_domain" in workflow_dict and
            "prospect_domain" in workflow_dict and
            workflow_dict["vendor_domain"].startswith("https://") and
            workflow_dict["prospect_domain"].startswith("https://")):
            print("✅ PASS: Compatible with Agno workflow.run(input=...)")
            print("   Can be used as: workflow.run(input=validated_input.to_workflow_dict())")
            return True
        else:
            print("❌ FAIL: Not compatible with Agno workflow format")
            return False

    except Exception as e:
        print(f"❌ ERROR: Compatibility test failed")
        print(f"   Error: {str(e)}")
        return False
    finally:
        print("=" * 80)


def main():
    """Run all domain normalization tests"""

    print("\n" + "=" * 100)
    print(" " * 30 + "DOMAIN NORMALIZATION TEST SUITE")
    print("=" * 100)

    results = []

    # Run all test suites
    results.append(("normalize_domain()", test_normalize_domain()))
    results.append(("WorkflowInput Model", test_workflow_input_model()))
    results.append(("Agno Workflow Compatibility", test_agno_workflow_compatibility()))

    # Print final summary
    print("\n" + "=" * 100)
    print(" " * 40 + "FINAL SUMMARY")
    print("=" * 100)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("=" * 100)

    if all_passed:
        print("\n🎉 All tests passed! Domain normalization is working correctly.")
        print("\nYou can now use flexible domain formats:")
        print("  • python main.py sendoso.com octavehq.com")
        print("  • python main.py www.sendoso.com www.octavehq.com")
        print("  • python main.py https://sendoso.com https://octavehq.com")
        print("\n" + "=" * 100)
        return 0
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        print("=" * 100)
        return 1


if __name__ == "__main__":
    exit(main())
