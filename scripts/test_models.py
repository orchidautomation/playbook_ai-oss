"""
Quick Model Access Test
Tests if your API keys can access the required models.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_models():
    """Test OpenAI model access"""
    print("=" * 80)
    print("TESTING OPENAI MODEL ACCESS")
    print("=" * 80)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return False

    print(f"✅ OpenAI API Key found: {api_key[:20]}...")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # Test gpt-4o
        print("\n📝 Testing gpt-4o...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Say 'test successful'"}],
                max_tokens=10
            )
            print(f"✅ gpt-4o accessible: {response.choices[0].message.content}")
        except Exception as e:
            print(f"❌ gpt-4o failed: {str(e)}")
            return False

        # Test gpt-4o-mini (optional - config already uses gpt-4o as fallback)
        print("\n📝 Testing gpt-4o-mini (optional)...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'test successful'"}],
                max_tokens=10
            )
            print(f"✅ gpt-4o-mini accessible: {response.choices[0].message.content}")
            print("   💡 Consider updating config.py to use gpt-4o-mini for cost savings")
        except Exception as e:
            print(f"⚠️  gpt-4o-mini not accessible (using gpt-4o as configured)")
            print(f"   Note: config.py already set to use gpt-4o for all models")

        print("\n✅ OpenAI configuration: All models using gpt-4o")
        return True

    except ImportError:
        print("❌ OpenAI library not installed. Run: pip install openai")
        return False
    except Exception as e:
        print(f"❌ OpenAI test failed: {str(e)}")
        return False


def test_anthropic():
    """Test Anthropic API (if used)"""
    print("\n" + "=" * 80)
    print("TESTING ANTHROPIC API ACCESS (OPTIONAL)")
    print("=" * 80)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not found (optional)")
        return True

    print(f"✅ Anthropic API Key found: {api_key[:20]}...")

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        print("\n📝 Testing Claude Sonnet...")
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say 'test successful'"}]
            )
            print(f"✅ Claude Sonnet accessible: {response.content[0].text}")
        except Exception as e:
            print(f"❌ Claude Sonnet failed: {str(e)}")
            return False

        return True

    except ImportError:
        print("⚠️  Anthropic library not installed (optional)")
        return True
    except Exception as e:
        print(f"❌ Anthropic test failed: {str(e)}")
        return False


def test_firecrawl():
    """Test Firecrawl API"""
    print("\n" + "=" * 80)
    print("TESTING FIRECRAWL API ACCESS")
    print("=" * 80)

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("❌ FIRECRAWL_API_KEY not found in .env")
        return False

    print(f"✅ Firecrawl API Key found: {api_key[:20]}...")

    try:
        from firecrawl import Firecrawl
        fc = Firecrawl(api_key=api_key)

        print("\n📝 Testing Firecrawl with simple scrape...")
        try:
            # Simple test scrape
            result = fc.scrape("https://example.com", formats=["markdown"])
            if result and hasattr(result, 'markdown'):
                markdown_len = len(result.markdown) if result.markdown else 0
                print(f"✅ Firecrawl accessible (scraped {markdown_len} chars)")
            else:
                print("⚠️  Firecrawl responded but format unexpected")
        except Exception as e:
            print(f"❌ Firecrawl failed: {str(e)}")
            return False

        return True

    except ImportError:
        print("❌ Firecrawl library not installed. Run: pip install firecrawl-py")
        return False
    except Exception as e:
        print(f"❌ Firecrawl test failed: {str(e)}")
        return False


def main():
    print("\n🧪 PLAYBOOK AI - MODEL ACCESS TEST")
    print("Testing all required APIs and models...\n")

    results = {
        "OpenAI": test_openai_models(),
        "Firecrawl": test_firecrawl(),
        "Anthropic": test_anthropic()
    }

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for service, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {service}")

    if all(results.values()):
        print("\n🎉 All tests passed! You're ready to run the workflow.")
        print("\nRun: python main.py <vendor_domain> <prospect_domain>")
    else:
        print("\n⚠️  Some tests failed. Fix the issues above before running.")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
