# Octave Clone MVP - Complete Implementation Plan

## Table of Contents
1. [Context Passing Mastery](#context-passing-mastery)
2. [Project Structure](#project-structure)
3. [Phase 1: Foundation](#phase-1-foundation-steps-1-5)
4. [Phase 2: Vendor Extraction](#phase-2-vendor-extraction-step-6)
5. [Phase 3: Prospect Intelligence](#phase-3-prospect-intelligence-step-7)
6. [Phase 4: Playbook Generation](#phase-4-playbook-generation-step-8)
7. [Phase 5: Polish & Testing](#phase-5-polish--testing)

---

## Context Passing Mastery

### Understanding StepInput and StepOutput

**Every Agno workflow step receives a `StepInput` and must return a `StepOutput`:**

```python
from agno.workflow.types import StepInput, StepOutput

def my_step_function(step_input: StepInput) -> StepOutput:
    """
    StepInput contains:
    - step_input.input: Original workflow input
    - step_input.previous_step_content: Content from immediately previous step
    - step_input.get_step_content("step_name"): Content from specific named step
    - step_input.get_all_previous_content(): All previous step outputs
    """

    # Do work here
    result = {"my_data": "value"}

    return StepOutput(
        content=result,  # This becomes available to next steps
        success=True,
        stop=False
    )
```

### Pattern 1: Sequential Steps (Simple Chain)

```python
# Step 1 → Step 2 → Step 3

# Step 1
def step1(step_input: StepInput) -> StepOutput:
    # Access original workflow input
    vendor_domain = step_input.input.get("vendor_domain")

    result = {"vendor_urls": ["url1", "url2"]}
    return StepOutput(content=result)

# Step 2 (accesses Step 1)
def step2(step_input: StepInput) -> StepOutput:
    # Get content from Step 1 (previous step)
    step1_data = step_input.previous_step_content
    vendor_urls = step1_data.get("vendor_urls", [])

    # Or access original input
    vendor_domain = step_input.input.get("vendor_domain")

    result = {"homepage_content": "..."}
    return StepOutput(content=result)

# Step 3 (accesses Step 2 or Step 1)
def step3(step_input: StepInput) -> StepOutput:
    # Get content from Step 2 (immediately previous)
    homepage = step_input.previous_step_content.get("homepage_content")

    # Or get content from Step 1 by name
    step1_data = step_input.get_step_content("step1_name")
    vendor_urls = step1_data.get("vendor_urls", [])

    return StepOutput(content={"analysis": "..."})
```

### Pattern 2: Parallel Steps → Sequential Step ⭐ CRITICAL

**This is where it gets tricky! When you have parallel steps, the NEXT step receives them differently:**

```python
from agno.workflow import Parallel, Step

# Workflow definition
workflow = Workflow(
    steps=[
        # Step 1: Parallel execution
        Parallel(
            Step(name="validate_vendor", executor=validate_vendor_domain),
            Step(name="validate_prospect", executor=validate_prospect_domain),
            name="parallel_validation"  # Give the Parallel block a name!
        ),

        # Step 2: Uses both parallel outputs
        Step(name="scrape_homepages", executor=scrape_both_homepages)
    ]
)

# Step 1A: Validate vendor
def validate_vendor_domain(step_input: StepInput) -> StepOutput:
    vendor_domain = step_input.input.get("vendor_domain")
    # Validate and map
    result = {
        "vendor_domain": vendor_domain,
        "vendor_urls": ["url1", "url2", "url3"]
    }
    return StepOutput(content=result)

# Step 1B: Validate prospect (runs in parallel)
def validate_prospect_domain(step_input: StepInput) -> StepOutput:
    prospect_domain = step_input.input.get("prospect_domain")
    # Validate and map
    result = {
        "prospect_domain": prospect_domain,
        "prospect_urls": ["url1", "url2", "url3"]
    }
    return StepOutput(content=result)

# Step 2: Access BOTH parallel outputs by name ⭐
def scrape_both_homepages(step_input: StepInput) -> StepOutput:
    """
    After parallel steps, you MUST access by step name.
    step_input.previous_step_content will be the Parallel block's combined output.
    """

    # METHOD 1: Access by step name (RECOMMENDED)
    vendor_data = step_input.get_step_content("validate_vendor")
    prospect_data = step_input.get_step_content("validate_prospect")

    vendor_domain = vendor_data.get("vendor_domain")
    vendor_urls = vendor_data.get("vendor_urls", [])

    prospect_domain = prospect_data.get("prospect_domain")
    prospect_urls = prospect_data.get("prospect_urls", [])

    # METHOD 2: Access from previous_step_content (it's a dict of all parallel outputs)
    # previous_step_content structure:
    # {
    #   "validate_vendor": {"vendor_domain": "...", "vendor_urls": [...]},
    #   "validate_prospect": {"prospect_domain": "...", "prospect_urls": [...]}
    # }
    all_parallel_data = step_input.previous_step_content
    vendor_data_alt = all_parallel_data.get("validate_vendor", {})

    # Now scrape both
    vendor_homepage = scrape_url(vendor_domain)
    prospect_homepage = scrape_url(prospect_domain)

    return StepOutput(content={
        "vendor_homepage": vendor_homepage,
        "prospect_homepage": prospect_homepage
    })
```

### Pattern 3: Multiple Parallel Blocks → Access Specific Steps

```python
workflow = Workflow(
    steps=[
        # Parallel Block 1
        Parallel(
            Step(name="validate_vendor", executor=...),
            Step(name="validate_prospect", executor=...),
            name="parallel_validation"
        ),

        # Parallel Block 2
        Parallel(
            Step(name="analyze_vendor", executor=...),
            Step(name="analyze_prospect", executor=...),
            name="parallel_analysis"
        ),

        # Step accessing BOTH parallel blocks
        Step(name="combine_results", executor=combine_all_data)
    ]
)

def combine_all_data(step_input: StepInput) -> StepOutput:
    """Access outputs from multiple previous parallel blocks"""

    # From Parallel Block 1
    vendor_validation = step_input.get_step_content("validate_vendor")
    prospect_validation = step_input.get_step_content("validate_prospect")

    # From Parallel Block 2 (most recent)
    vendor_analysis = step_input.previous_step_content.get("analyze_vendor")
    prospect_analysis = step_input.previous_step_content.get("analyze_prospect")

    # Or use get_step_content for clarity
    vendor_analysis_alt = step_input.get_step_content("analyze_vendor")

    # Combine everything
    combined = {
        "vendor": {
            "validation": vendor_validation,
            "analysis": vendor_analysis
        },
        "prospect": {
            "validation": prospect_validation,
            "analysis": prospect_analysis
        }
    }

    return StepOutput(content=combined)
```

### Pattern 4: Agents as Steps (they return RunOutput, need wrapping)

```python
from agno.agent import Agent

# Define an agent
my_agent = Agent(
    name="My Analyzer",
    instructions="Analyze the content..."
)

# Option 1: Use agent directly in workflow (Agno handles it)
workflow = Workflow(
    steps=[
        Step(name="analyze", agent=my_agent)
    ]
)

# Option 2: Wrap agent in executor function for more control
def analyze_with_agent(step_input: StepInput) -> StepOutput:
    """Custom executor wrapping an agent"""

    # Get previous step content
    content_to_analyze = step_input.previous_step_content

    # Run agent
    agent_response = my_agent.run(
        input=f"Analyze this content: {content_to_analyze}"
    )

    # Extract response
    analysis_result = agent_response.content

    # Return as StepOutput
    return StepOutput(content=analysis_result)

# Use in workflow
workflow = Workflow(
    steps=[
        Step(name="analyze", executor=analyze_with_agent)
    ]
)
```

### Common Context Passing Pitfalls & Solutions

#### ❌ PITFALL 1: Trying to access parallel outputs without step names
```python
# WRONG - This won't work reliably
def bad_function(step_input: StepInput) -> StepOutput:
    data = step_input.previous_step_content  # Dict of all parallel outputs
    vendor_urls = data.get("vendor_urls")  # ❌ Won't work! Not at top level
```

#### ✅ SOLUTION: Access by step name
```python
# CORRECT
def good_function(step_input: StepInput) -> StepOutput:
    vendor_data = step_input.get_step_content("validate_vendor")
    vendor_urls = vendor_data.get("vendor_urls")  # ✅ Works!
```

#### ❌ PITFALL 2: Forgetting to name parallel steps
```python
# WRONG - Can't access unnamed steps
Parallel(
    Step(executor=func1),  # ❌ No name!
    Step(executor=func2)   # ❌ No name!
)
```

#### ✅ SOLUTION: Always name your steps
```python
# CORRECT
Parallel(
    Step(name="step1", executor=func1),  # ✅ Named!
    Step(name="step2", executor=func2),  # ✅ Named!
    name="parallel_block"                # ✅ Name the parallel block too!
)
```

#### ❌ PITFALL 3: Not handling missing data
```python
# WRONG - Will crash if data doesn't exist
def bad_function(step_input: StepInput) -> StepOutput:
    data = step_input.get_step_content("some_step")
    value = data["key"]  # ❌ KeyError if "key" doesn't exist
```

#### ✅ SOLUTION: Use .get() with defaults
```python
# CORRECT
def good_function(step_input: StepInput) -> StepOutput:
    data = step_input.get_step_content("some_step")
    value = data.get("key", "default_value")  # ✅ Safe!

    # Or check if None
    if data is None:
        return StepOutput(
            content={"error": "Previous step failed"},
            success=False,
            stop=True
        )
```

### Debug Pattern: Print Available Context

```python
def debug_context(step_input: StepInput) -> StepOutput:
    """Helper function to see what context is available"""

    print("=" * 60)
    print("AVAILABLE CONTEXT")
    print("=" * 60)

    print("\n1. Original Workflow Input:")
    print(step_input.input)

    print("\n2. Previous Step Content:")
    print(step_input.previous_step_content)

    print("\n3. All Previous Content:")
    print(step_input.get_all_previous_content())

    print("=" * 60)

    return StepOutput(content={"debug": "complete"})
```

---

## Project Structure

```
octave-clone/
├── .env                          # API keys
├── .gitignore
├── README.md
├── IMPLEMENTATION_PLAN.md        # This file
├── requirements.txt
│
├── main.py                       # Entry point
├── workflow.py                   # Workflow definition
├── config.py                     # Configuration
│
├── agents/                       # All agent definitions
│   ├── __init__.py
│   ├── vendor_specialists/
│   │   ├── __init__.py
│   │   ├── offerings_extractor.py
│   │   ├── case_study_extractor.py
│   │   ├── proof_points_extractor.py
│   │   ├── value_prop_extractor.py
│   │   ├── customer_extractor.py
│   │   ├── use_case_extractor.py
│   │   ├── persona_extractor.py
│   │   └── differentiator_extractor.py
│   │
│   ├── prospect_specialists/
│   │   ├── __init__.py
│   │   ├── company_analyst.py
│   │   ├── pain_point_analyst.py
│   │   ├── leadership_analyst.py      # Uses FirecrawlTools
│   │   ├── tech_stack_analyst.py      # Uses FirecrawlTools
│   │   └── customer_analyst.py
│   │
│   └── playbook_generator.py     # Step 8 agent
│
├── steps/                        # Step executor functions
│   ├── __init__.py
│   ├── step1_domain_validation.py
│   ├── step2_homepage_scraping.py
│   ├── step3_initial_analysis.py
│   ├── step4_url_prioritization.py
│   ├── step5_batch_scraping.py
│   ├── step6_vendor_extraction.py
│   ├── step7_prospect_analysis.py
│   └── step8_playbook_generation.py
│
├── models/                       # Pydantic schemas
│   ├── __init__.py
│   ├── vendor_elements.py
│   ├── prospect_intelligence.py
│   ├── playbook.py
│   └── common.py
│
├── utils/                        # Helper functions
│   ├── __init__.py
│   └── firecrawl_helpers.py
│
└── tests/                        # Tests for each phase
    ├── __init__.py
    ├── test_phase1.py
    ├── test_phase2.py
    ├── test_phase3.py
    ├── test_phase4.py
    └── fixtures/
        ├── sample_vendor_content.md
        └── sample_prospect_content.md
```

---

## Phase 1: Foundation (Steps 1-5)
**Goal:** Build intelligence gathering pipeline with Firecrawl Python SDK

### Atomic Tasks Checklist

#### Setup & Configuration
- [ ] Create project directory structure
- [ ] Create `requirements.txt` with dependencies:
  ```txt
  agno>=0.11.0
  firecrawl-py>=1.0.0
  python-dotenv>=1.0.0
  pydantic>=2.0.0
  anthropic>=0.40.0
  ```
- [ ] Create `.env` file with:
  ```
  FIRECRAWL_API_KEY=fc-your-key
  OPENAI_API_KEY=your-key  # or ANTHROPIC_API_KEY
  ```
- [ ] Create `.gitignore`:
  ```
  .env
  __pycache__/
  *.pyc
  .pytest_cache/
  .venv/
  venv/
  ```
- [ ] Create `config.py`:
  ```python
  import os
  from dotenv import load_dotenv

  load_dotenv()

  FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
  OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
  ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

  # Workflow settings
  MAX_URLS_TO_SCRAPE = 50  # 25 vendor + 25 prospect
  BATCH_SCRAPE_TIMEOUT = 180  # 3 minutes
  ```

#### Step 1: Domain Validation
- [ ] Create `utils/firecrawl_helpers.py`:
  ```python
  from firecrawl import Firecrawl
  from typing import Dict, List
  import config

  # Initialize Firecrawl client
  fc = Firecrawl(api_key=config.FIRECRAWL_API_KEY)

  def map_website(domain: str, limit: int = 100) -> Dict:
      """Map website to discover all URLs"""
      try:
          result = fc.map(url=domain, limit=limit)
          return {
              "success": True,
              "domain": domain,
              "urls": result.get("links", []),
              "total_urls": len(result.get("links", []))
          }
      except Exception as e:
          return {
              "success": False,
              "domain": domain,
              "error": str(e),
              "urls": [],
              "total_urls": 0
          }

  def scrape_url(url: str, formats: List[str] = None) -> Dict:
      """Scrape a single URL"""
      if formats is None:
          formats = ['markdown', 'html']

      try:
          result = fc.scrape(url, formats=formats, wait_for=2000)
          return {
              "success": True,
              "url": url,
              "markdown": result.get("markdown", ""),
              "html": result.get("html", ""),
              "metadata": result.get("metadata", {})
          }
      except Exception as e:
          return {
              "success": False,
              "url": url,
              "error": str(e),
              "markdown": "",
              "html": ""
          }

  def batch_scrape_urls(urls: List[str], formats: List[str] = None) -> Dict[str, Dict]:
      """Batch scrape multiple URLs"""
      if formats is None:
          formats = ['markdown']

      try:
          job = fc.batch_scrape(
              urls,
              formats=formats,
              poll_interval=2,
              timeout=config.BATCH_SCRAPE_TIMEOUT
          )

          # Convert to dict keyed by URL
          results = {}
          for doc in job.data:
              url = doc.metadata.source_url if doc.metadata else "unknown"
              results[url] = {
                  "markdown": doc.markdown,
                  "metadata": doc.metadata.__dict__ if doc.metadata else {}
              }

          return {
              "success": True,
              "results": results,
              "total_scraped": len(results)
          }
      except Exception as e:
          return {
              "success": False,
              "error": str(e),
              "results": {},
              "total_scraped": 0
          }
  ```

- [ ] Create `steps/step1_domain_validation.py`:
  ```python
  from agno.workflow.types import StepInput, StepOutput
  from utils.firecrawl_helpers import map_website

  def validate_vendor_domain(step_input: StepInput) -> StepOutput:
      """Validate vendor domain and map all URLs"""
      # Get vendor domain from workflow input
      vendor_domain = step_input.input.get("vendor_domain")

      if not vendor_domain:
          return StepOutput(
              content={"error": "No vendor_domain provided"},
              success=False,
              stop=True
          )

      # Map the website
      print(f"🔍 Mapping vendor domain: {vendor_domain}")
      result = map_website(vendor_domain, limit=100)

      if not result["success"]:
          return StepOutput(
              content=result,
              success=False,
              stop=True
          )

      print(f"✅ Found {result['total_urls']} URLs for vendor")

      return StepOutput(
          content={
              "vendor_domain": vendor_domain,
              "vendor_urls": result["urls"],
              "vendor_total_urls": result["total_urls"]
          },
          success=True
      )

  def validate_prospect_domain(step_input: StepInput) -> StepOutput:
      """Validate prospect domain and map all URLs"""
      # Get prospect domain from workflow input
      prospect_domain = step_input.input.get("prospect_domain")

      if not prospect_domain:
          return StepOutput(
              content={"error": "No prospect_domain provided"},
              success=False,
              stop=True
          )

      # Map the website
      print(f"🔍 Mapping prospect domain: {prospect_domain}")
      result = map_website(prospect_domain, limit=100)

      if not result["success"]:
          return StepOutput(
              content=result,
              success=False,
              stop=True
          )

      print(f"✅ Found {result['total_urls']} URLs for prospect")

      return StepOutput(
          content={
              "prospect_domain": prospect_domain,
              "prospect_urls": result["urls"],
              "prospect_total_urls": result["total_urls"]
          },
          success=True
      )
  ```

- [ ] Test Step 1 in isolation:
  ```python
  # tests/test_phase1.py
  from agno.workflow.types import StepInput
  from steps.step1_domain_validation import validate_vendor_domain

  def test_step1_vendor():
      step_input = StepInput(
          input={"vendor_domain": "https://octavehq.com"}
      )
      result = validate_vendor_domain(step_input)

      assert result.success == True
      assert "vendor_urls" in result.content
      assert len(result.content["vendor_urls"]) > 0
      print("✅ Step 1 (vendor) passed!")

  if __name__ == "__main__":
      test_step1_vendor()
  ```

#### Step 2: Homepage Scraping
- [ ] Create `steps/step2_homepage_scraping.py`:
  ```python
  from agno.workflow.types import StepInput, StepOutput
  from utils.firecrawl_helpers import scrape_url

  def scrape_vendor_homepage(step_input: StepInput) -> StepOutput:
      """Scrape vendor homepage"""
      # Get vendor domain from Step 1 output
      vendor_data = step_input.get_step_content("validate_vendor")

      if not vendor_data:
          return StepOutput(
              content={"error": "No vendor data from Step 1"},
              success=False,
              stop=True
          )

      vendor_domain = vendor_data.get("vendor_domain")

      print(f"📄 Scraping vendor homepage: {vendor_domain}")
      result = scrape_url(vendor_domain, formats=['markdown', 'html'])

      if not result["success"]:
          return StepOutput(
              content=result,
              success=False,
              stop=True
          )

      print(f"✅ Scraped vendor homepage ({len(result['markdown'])} chars)")

      return StepOutput(
          content={
              "vendor_domain": vendor_domain,
              "vendor_homepage_markdown": result["markdown"],
              "vendor_homepage_html": result["html"],
              "vendor_homepage_metadata": result["metadata"]
          },
          success=True
      )

  def scrape_prospect_homepage(step_input: StepInput) -> StepOutput:
      """Scrape prospect homepage"""
      # Get prospect domain from Step 1 output
      prospect_data = step_input.get_step_content("validate_prospect")

      if not prospect_data:
          return StepOutput(
              content={"error": "No prospect data from Step 1"},
              success=False,
              stop=True
          )

      prospect_domain = prospect_data.get("prospect_domain")

      print(f"📄 Scraping prospect homepage: {prospect_domain}")
      result = scrape_url(prospect_domain, formats=['markdown', 'html'])

      if not result["success"]:
          return StepOutput(
              content=result,
              success=False,
              stop=True
          )

      print(f"✅ Scraped prospect homepage ({len(result['markdown'])} chars)")

      return StepOutput(
          content={
              "prospect_domain": prospect_domain,
              "prospect_homepage_markdown": result["markdown"],
              "prospect_homepage_html": result["html"],
              "prospect_homepage_metadata": result["metadata"]
          },
          success=True
      )
  ```

#### Step 3: Initial Analysis (AI)
- [ ] Create `agents/homepage_analyst.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat

  homepage_analyst = Agent(
      name="Homepage Analyst",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are a B2B company analyst specializing in homepage analysis.

      Analyze the homepage content and extract:

      1. COMPANY BASICS
         - Company name
         - Tagline/positioning statement
         - Primary value proposition
         - Industry/market category

      2. OFFERINGS
         - Main products or services mentioned
         - Key features highlighted
         - Target audience indicators

      3. TRUST SIGNALS
         - Customer logos visible
         - Testimonials or quotes
         - Statistics or metrics
         - Notable achievements

      4. CALL TO ACTION
         - Primary CTA (demo, trial, contact, etc.)
         - Target personas implied by CTAs

      Return a structured analysis focusing on what this company does and who they serve.
      Keep it concise but comprehensive.
      """,
      markdown=True,
      structured_output=False
  )
  ```

- [ ] Create `steps/step3_initial_analysis.py`:
  ```python
  from agno.workflow.types import StepInput, StepOutput
  from agents.homepage_analyst import homepage_analyst

  def analyze_vendor_homepage(step_input: StepInput) -> StepOutput:
      """Analyze vendor homepage with AI"""
      # Get vendor homepage content from Step 2
      vendor_homepage_data = step_input.get_step_content("scrape_vendor_home")

      if not vendor_homepage_data:
          return StepOutput(
              content={"error": "No vendor homepage data"},
              success=False,
              stop=True
          )

      markdown_content = vendor_homepage_data.get("vendor_homepage_markdown", "")

      print(f"🤖 Analyzing vendor homepage with AI...")

      # Run agent
      response = homepage_analyst.run(
          input=f"Analyze this homepage:\n\n{markdown_content}"
      )

      analysis = response.content

      print(f"✅ Vendor homepage analyzed")

      return StepOutput(
          content={
              "vendor_homepage_analysis": analysis
          },
          success=True
      )

  def analyze_prospect_homepage(step_input: StepInput) -> StepOutput:
      """Analyze prospect homepage with AI"""
      # Get prospect homepage content from Step 2
      prospect_homepage_data = step_input.get_step_content("scrape_prospect_home")

      if not prospect_homepage_data:
          return StepOutput(
              content={"error": "No prospect homepage data"},
              success=False,
              stop=True
          )

      markdown_content = prospect_homepage_data.get("prospect_homepage_markdown", "")

      print(f"🤖 Analyzing prospect homepage with AI...")

      # Run agent
      response = homepage_analyst.run(
          input=f"Analyze this homepage:\n\n{markdown_content}"
      )

      analysis = response.content

      print(f"✅ Prospect homepage analyzed")

      return StepOutput(
          content={
              "prospect_homepage_analysis": analysis
          },
          success=True
      )
  ```

#### Step 4: URL Prioritization
- [ ] Create `agents/url_prioritizer.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from pydantic import BaseModel, Field
  from typing import List

  class PrioritizedURL(BaseModel):
      url: str
      page_type: str = Field(description="e.g., 'about', 'case_study', 'pricing', 'blog'")
      priority: int = Field(description="1 (highest) to 10 (lowest)")
      reasoning: str

  class URLPrioritizationResult(BaseModel):
      vendor_selected_urls: List[PrioritizedURL]
      prospect_selected_urls: List[PrioritizedURL]

  url_prioritizer = Agent(
      name="Strategic URL Selector",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are a content strategist selecting the most valuable pages for B2B sales intelligence.

      Given lists of URLs from vendor and prospect websites, select the TOP 10-15 MOST VALUABLE pages for each.

      PRIORITIZE:
      - /about, /about-us, /company, /team, /leadership
      - /products, /solutions, /platform, /features
      - /customers, /case-studies, /success-stories, /testimonials
      - /pricing, /plans
      - /blog (recent posts with dates in URL)
      - /industries, /use-cases, /resources

      AVOID:
      - Legal pages (/privacy, /terms, /legal, /cookies)
      - Career pages (/careers, /jobs, /join-us)
      - Support docs (/help, /docs, /support, /faq)
      - Login/signup pages (/login, /signup, /register)
      - Media/press pages (unless highly relevant)

      For each selected URL, provide:
      - page_type: Category of the page
      - priority: 1 (must have) to 10 (nice to have)
      - reasoning: Why this page is valuable for sales intelligence

      Return top 10-15 URLs per company, prioritized.
      """,
      structured_output=True,
      output_schema=URLPrioritizationResult
  )
  ```

- [ ] Create `steps/step4_url_prioritization.py`:
  ```python
  from agno.workflow.types import StepInput, StepOutput
  from agents.url_prioritizer import url_prioritizer

  def prioritize_urls(step_input: StepInput) -> StepOutput:
      """Prioritize URLs from both companies"""
      # Get URLs from Step 1
      vendor_data = step_input.get_step_content("validate_vendor")
      prospect_data = step_input.get_step_content("validate_prospect")

      if not vendor_data or not prospect_data:
          return StepOutput(
              content={"error": "Missing URL data from Step 1"},
              success=False,
              stop=True
          )

      vendor_urls = vendor_data.get("vendor_urls", [])
      prospect_urls = prospect_data.get("prospect_urls", [])

      print(f"🎯 Prioritizing {len(vendor_urls)} vendor URLs and {len(prospect_urls)} prospect URLs...")

      # Prepare input for agent
      prompt = f"""
      VENDOR URLs ({len(vendor_urls)} total):
      {chr(10).join(vendor_urls[:200])}  # Limit to first 200

      PROSPECT URLs ({len(prospect_urls)} total):
      {chr(10).join(prospect_urls[:200])}  # Limit to first 200

      Select the top 10-15 most valuable URLs from each company for sales intelligence gathering.
      """

      # Run agent
      response = url_prioritizer.run(input=prompt)

      result = response.content

      # Extract URLs
      vendor_selected = [item.url for item in result.vendor_selected_urls]
      prospect_selected = [item.url for item in result.prospect_selected_urls]

      print(f"✅ Selected {len(vendor_selected)} vendor URLs and {len(prospect_selected)} prospect URLs")

      return StepOutput(
          content={
              "vendor_selected_urls": vendor_selected,
              "prospect_selected_urls": prospect_selected,
              "vendor_url_details": [item.dict() for item in result.vendor_selected_urls],
              "prospect_url_details": [item.dict() for item in result.prospect_selected_urls]
          },
          success=True
      )
  ```

#### Step 5: Batch Scraping
- [ ] Create `steps/step5_batch_scraping.py`:
  ```python
  from agno.workflow.types import StepInput, StepOutput
  from utils.firecrawl_helpers import batch_scrape_urls
  import config

  def batch_scrape_selected_pages(step_input: StepInput) -> StepOutput:
      """Batch scrape all selected URLs from vendor and prospect"""
      # Get selected URLs from Step 4
      url_data = step_input.previous_step_content

      if not url_data:
          return StepOutput(
              content={"error": "No URL data from Step 4"},
              success=False,
              stop=True
          )

      vendor_urls = url_data.get("vendor_selected_urls", [])
      prospect_urls = url_data.get("prospect_selected_urls", [])

      # Combine and limit total URLs
      all_urls = vendor_urls + prospect_urls

      if len(all_urls) > config.MAX_URLS_TO_SCRAPE:
          print(f"⚠️  Too many URLs ({len(all_urls)}), limiting to {config.MAX_URLS_TO_SCRAPE}")
          # Take proportionally from each
          vendor_limit = int(config.MAX_URLS_TO_SCRAPE * len(vendor_urls) / len(all_urls))
          prospect_limit = config.MAX_URLS_TO_SCRAPE - vendor_limit
          vendor_urls = vendor_urls[:vendor_limit]
          prospect_urls = prospect_urls[:prospect_limit]
          all_urls = vendor_urls + prospect_urls

      print(f"📚 Batch scraping {len(all_urls)} URLs ({len(vendor_urls)} vendor + {len(prospect_urls)} prospect)...")

      # Batch scrape
      result = batch_scrape_urls(all_urls, formats=['markdown'])

      if not result["success"]:
          return StepOutput(
              content=result,
              success=False,
              stop=True
          )

      scraped_results = result["results"]

      # Separate vendor and prospect content
      vendor_content = {}
      prospect_content = {}

      for url, data in scraped_results.items():
          if url in vendor_urls:
              vendor_content[url] = data["markdown"]
          elif url in prospect_urls:
              prospect_content[url] = data["markdown"]

      print(f"✅ Scraped {len(vendor_content)} vendor pages and {len(prospect_content)} prospect pages")

      return StepOutput(
          content={
              "vendor_content": vendor_content,
              "prospect_content": prospect_content,
              "vendor_urls_scraped": list(vendor_content.keys()),
              "prospect_urls_scraped": list(prospect_content.keys()),
              "total_scraped": len(scraped_results)
          },
          success=True
      )
  ```

#### Create Phase 1 Workflow
- [ ] Create `workflow.py` (Phase 1 version):
  ```python
  from agno.workflow import Workflow, Step, Parallel
  from steps.step1_domain_validation import validate_vendor_domain, validate_prospect_domain
  from steps.step2_homepage_scraping import scrape_vendor_homepage, scrape_prospect_homepage
  from steps.step3_initial_analysis import analyze_vendor_homepage, analyze_prospect_homepage
  from steps.step4_url_prioritization import prioritize_urls
  from steps.step5_batch_scraping import batch_scrape_selected_pages

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
  ```

- [ ] Create `main.py` (Phase 1 version):
  ```python
  from workflow import phase1_workflow
  import json

  def main():
      print("=" * 60)
      print("OCTAVE CLONE MVP - PHASE 1 TEST")
      print("=" * 60)

      # Test with two real companies
      workflow_input = {
          "vendor_domain": "https://octavehq.com",
          "prospect_domain": "https://sendoso.com"
      }

      print(f"\nVendor: {workflow_input['vendor_domain']}")
      print(f"Prospect: {workflow_input['prospect_domain']}\n")

      # Run workflow
      result = phase1_workflow.run(input=workflow_input)

      print("\n" + "=" * 60)
      print("PHASE 1 COMPLETE")
      print("=" * 60)

      # Save results
      with open("phase1_output.json", "w") as f:
          json.dump(result.content, f, indent=2)

      print("\n✅ Results saved to phase1_output.json")

      # Print summary
      content = result.content
      print(f"\nVendor URLs scraped: {len(content.get('vendor_content', {}))}")
      print(f"Prospect URLs scraped: {len(content.get('prospect_content', {}))}")

  if __name__ == "__main__":
      main()
  ```

#### Phase 1 Testing
- [ ] Test each step individually
- [ ] Test Steps 1-2 together
- [ ] Test Steps 1-3 together
- [ ] Test Steps 1-4 together
- [ ] Test complete Phase 1 workflow end-to-end
- [ ] Validate output format
- [ ] Check error handling (invalid domains, network errors, etc.)

---

## Phase 2: Vendor Extraction (Step 6)
**Goal:** Extract all GTM elements from vendor content with 8 parallel specialists

### Atomic Tasks Checklist

#### Pydantic Models
- [ ] Create `models/common.py`:
  ```python
  from pydantic import BaseModel, Field
  from typing import List, Optional

  class Source(BaseModel):
      """Reference to where information was found"""
      url: str
      page_type: str  # e.g., "homepage", "case_study", "about"
      excerpt: Optional[str] = None
  ```

- [ ] Create `models/vendor_elements.py`:
  ```python
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
  ```

#### Vendor Specialist Agents (8 total)
- [ ] Create `agents/vendor_specialists/offerings_extractor.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from models.vendor_elements import Offering
  from typing import List
  from pydantic import BaseModel

  class OfferingsExtractionResult(BaseModel):
      offerings: List[Offering]

  offerings_extractor = Agent(
      name="Offerings Extractor",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are an expert at identifying and cataloging product offerings from company content.

      Extract ALL products, services, or platform components mentioned.

      For each offering, extract:
      - Name: Official product/service name
      - Description: What it does (1-2 sentences)
      - Features: List of key capabilities or features
      - Pricing indicators: Any pricing info mentioned (free tier, enterprise, etc.)
      - Target audience: Who it's for (if mentioned)
      - Sources: URLs where this info was found

      Look for:
      - Product pages (/products, /platform, /solutions)
      - Feature lists
      - Pricing pages
      - Homepage offerings

      Return comprehensive structured output with ALL offerings found.
      """,
      structured_output=True,
      output_schema=OfferingsExtractionResult
  )
  ```

- [ ] Create `agents/vendor_specialists/case_study_extractor.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from models.vendor_elements import CaseStudy
  from typing import List
  from pydantic import BaseModel

  class CaseStudiesExtractionResult(BaseModel):
      case_studies: List[CaseStudy]

  case_study_extractor = Agent(
      name="Case Study Extractor",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are an expert at extracting customer success stories and case studies.

      Extract ALL case studies, customer stories, and success examples.

      For each case study, extract:
      - Customer name: Company name
      - Industry: Their industry (if mentioned)
      - Company size: SMB, Mid-market, Enterprise (if mentioned)
      - Challenge: Problem they faced
      - Solution: How vendor helped
      - Results: List of outcomes achieved
      - Metrics: Quantified results (%, $, time saved, etc.)
      - Sources: URLs where found

      Look for:
      - /customers, /case-studies, /success-stories pages
      - Customer testimonials with details
      - Homepage customer highlights

      Return all case studies found with complete details.
      """,
      structured_output=True,
      output_schema=CaseStudiesExtractionResult
  )
  ```

- [ ] Create `agents/vendor_specialists/proof_points_extractor.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from models.vendor_elements import ProofPoint
  from typing import List
  from pydantic import BaseModel

  class ProofPointsExtractionResult(BaseModel):
      proof_points: List[ProofPoint]

  proof_points_extractor = Agent(
      name="Proof Points Extractor",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are an expert at identifying credibility indicators and social proof.

      Extract ALL proof points including:
      - Testimonials: Customer quotes and endorsements
      - Statistics: Usage stats (X customers, Y% growth, Z awards)
      - Awards: Industry recognition, certifications, badges
      - Certifications: Compliance, security, industry standards

      For each proof point:
      - Type: testimonial, statistic, award, or certification
      - Content: The actual proof point text
      - Source attribution: Who said it or where from (if applicable)
      - Sources: URLs where found

      Look across all pages for credibility indicators.
      Return comprehensive list of ALL proof points.
      """,
      structured_output=True,
      output_schema=ProofPointsExtractionResult
  )
  ```

- [ ] Create `agents/vendor_specialists/value_prop_extractor.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from models.vendor_elements import ValueProposition
  from typing import List
  from pydantic import BaseModel

  class ValuePropositionsExtractionResult(BaseModel):
      value_propositions: List[ValueProposition]

  value_prop_extractor = Agent(
      name="Value Proposition Extractor",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are an expert at identifying core value propositions and positioning statements.

      Extract value propositions - the core benefits and outcomes promised.

      For each value prop:
      - Statement: The value proposition (concise)
      - Benefits: List of specific benefits
      - Differentiation: What makes this unique (if mentioned)
      - Target persona: Who this appeals to (if mentioned)
      - Sources: URLs where found

      Look for:
      - Homepage hero sections
      - About page positioning
      - Product benefit statements
      - "Why choose us" sections

      Focus on outcome-based value, not feature lists.
      """,
      structured_output=True,
      output_schema=ValuePropositionsExtractionResult
  )
  ```

- [ ] Create `agents/vendor_specialists/customer_extractor.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from models.vendor_elements import ReferenceCustomer
  from typing import List
  from pydantic import BaseModel

  class ReferenceCustomersExtractionResult(BaseModel):
      reference_customers: List[ReferenceCustomer]

  customer_extractor = Agent(
      name="Reference Customer Extractor",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are an expert at identifying customer references and logos.

      Extract ALL customer references, logos, and company mentions.

      For each reference:
      - Name: Company name
      - Logo URL: If visible (extract from page)
      - Industry: If mentioned or inferable
      - Company size: SMB/Mid-market/Enterprise if mentioned
      - Relationship: customer, partner, integration, or other
      - Sources: URLs where found

      Look for:
      - Customer logo walls
      - "Trusted by" sections
      - Partner pages
      - Integration pages
      - Case study customer names

      Capture ALL companies mentioned, even if minimal info.
      """,
      structured_output=True,
      output_schema=ReferenceCustomersExtractionResult
  )
  ```

- [ ] Create `agents/vendor_specialists/use_case_extractor.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from models.vendor_elements import UseCase
  from typing import List
  from pydantic import BaseModel

  class UseCasesExtractionResult(BaseModel):
      use_cases: List[UseCase]

  use_case_extractor = Agent(
      name="Use Case Extractor",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are an expert at identifying use cases and workflow solutions.

      Extract ALL use cases - specific ways customers use the product.

      For each use case:
      - Title: Name of the use case
      - Description: What this use case accomplishes
      - Target persona: Who uses this (if mentioned)
      - Target industry: Industry focus (if mentioned)
      - Problems solved: List of problems addressed
      - Key features used: Features relevant to this use case
      - Sources: URLs where found

      Look for:
      - /use-cases pages
      - /solutions pages
      - /industries pages
      - Workflow descriptions
      - "How to" sections

      Capture both broad and specific use cases.
      """,
      structured_output=True,
      output_schema=UseCasesExtractionResult
  )
  ```

- [ ] Create `agents/vendor_specialists/persona_extractor.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from models.vendor_elements import TargetPersona
  from typing import List
  from pydantic import BaseModel

  class TargetPersonasExtractionResult(BaseModel):
      target_personas: List[TargetPersona]

  persona_extractor = Agent(
      name="Target Persona Extractor",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are an expert at identifying target buyer personas.

      Extract ALL personas the vendor targets - who they sell to.

      For each persona:
      - Title: Job title (e.g., "CMO", "VP Sales", "Product Manager")
      - Department: Department or function
      - Responsibilities: Key responsibilities mentioned
      - Pain points: Problems this persona faces (mentioned)
      - Sources: URLs where found

      Look for:
      - Persona-specific landing pages
      - "For [Role]" sections
      - Testimonials with titles
      - Use cases by role
      - Product messaging by audience

      Infer personas from:
      - Who testimonials are from
      - Who use cases target
      - CTA language ("For marketing teams", etc.)
      """,
      structured_output=True,
      output_schema=TargetPersonasExtractionResult
  )
  ```

- [ ] Create `agents/vendor_specialists/differentiator_extractor.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from models.vendor_elements import Differentiator
  from typing import List
  from pydantic import BaseModel

  class DifferentiatorsExtractionResult(BaseModel):
      differentiators: List[Differentiator]

  differentiator_extractor = Agent(
      name="Competitive Differentiator Extractor",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are an expert at identifying competitive differentiation.

      Extract statements about what makes the vendor unique or better.

      For each differentiator:
      - Category: feature, approach, market_position, or technology
      - Statement: The differentiation claim
      - vs_alternative: What they're comparing against (if mentioned)
      - Evidence: Supporting points or proof
      - Sources: URLs where found

      Look for:
      - "Unlike other solutions..."
      - "The only platform that..."
      - "First to market..."
      - Unique feature claims
      - Proprietary technology mentions
      - Market positioning statements

      Capture both explicit comparisons and implied differentiation.
      """,
      structured_output=True,
      output_schema=DifferentiatorsExtractionResult
  )
  ```

#### Step 6 Executor
- [ ] Create `steps/step6_vendor_extraction.py`:
  ```python
  from agno.workflow.types import StepInput, StepOutput
  from agents.vendor_specialists.offerings_extractor import offerings_extractor
  from agents.vendor_specialists.case_study_extractor import case_study_extractor
  from agents.vendor_specialists.proof_points_extractor import proof_points_extractor
  from agents.vendor_specialists.value_prop_extractor import value_prop_extractor
  from agents.vendor_specialists.customer_extractor import customer_extractor
  from agents.vendor_specialists.use_case_extractor import use_case_extractor
  from agents.vendor_specialists.persona_extractor import persona_extractor
  from agents.vendor_specialists.differentiator_extractor import differentiator_extractor
  from models.vendor_elements import VendorElements

  def extract_offerings(step_input: StepInput) -> StepOutput:
      """Extract all product/service offerings"""
      # Get vendor content from Step 5
      scrape_data = step_input.get_step_content("batch_scrape")
      vendor_content = scrape_data.get("vendor_content", {})

      # Combine all content
      full_content = "\n\n---\n\n".join([
          f"URL: {url}\n\n{content}"
          for url, content in vendor_content.items()
      ])

      print("🔍 Extracting offerings...")
      response = offerings_extractor.run(
          input=f"Extract all offerings from this content:\n\n{full_content}"
      )

      offerings = response.content.offerings
      print(f"✅ Found {len(offerings)} offerings")

      return StepOutput(content={"offerings": [o.dict() for o in offerings]})

  def extract_case_studies(step_input: StepInput) -> StepOutput:
      """Extract all case studies"""
      scrape_data = step_input.get_step_content("batch_scrape")
      vendor_content = scrape_data.get("vendor_content", {})

      full_content = "\n\n---\n\n".join([
          f"URL: {url}\n\n{content}"
          for url, content in vendor_content.items()
      ])

      print("📚 Extracting case studies...")
      response = case_study_extractor.run(
          input=f"Extract all case studies:\n\n{full_content}"
      )

      case_studies = response.content.case_studies
      print(f"✅ Found {len(case_studies)} case studies")

      return StepOutput(content={"case_studies": [cs.dict() for cs in case_studies]})

  # Similar pattern for remaining extractors...
  def extract_proof_points(step_input: StepInput) -> StepOutput:
      """Extract all proof points"""
      scrape_data = step_input.get_step_content("batch_scrape")
      vendor_content = scrape_data.get("vendor_content", {})

      full_content = "\n\n---\n\n".join([
          f"URL: {url}\n\n{content}"
          for url, content in vendor_content.items()
      ])

      print("🏆 Extracting proof points...")
      response = proof_points_extractor.run(
          input=f"Extract all proof points:\n\n{full_content}"
      )

      proof_points = response.content.proof_points
      print(f"✅ Found {len(proof_points)} proof points")

      return StepOutput(content={"proof_points": [pp.dict() for pp in proof_points]})

  # Continue for all 8 extractors...
  ```

#### Update Workflow for Phase 2
- [ ] Update `workflow.py` to add Step 6:
  ```python
  from steps.step6_vendor_extraction import (
      extract_offerings,
      extract_case_studies,
      extract_proof_points,
      # ... import all 8
  )

  # Add to workflow after Step 5:
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
  ```

#### Phase 2 Testing
- [ ] Test each extractor agent individually with sample content
- [ ] Test Step 6 with Phase 1 output
- [ ] Validate Pydantic models
- [ ] Check extraction quality (precision and recall)
- [ ] Test with 3+ different vendor websites

---

## Phase 3: Prospect Intelligence (Step 7)
**Goal:** Extract prospect intelligence with 5 specialists (2 with FirecrawlTools)

### Atomic Tasks Checklist

#### Pydantic Models
- [ ] Create `models/prospect_intelligence.py`:
  ```python
  from pydantic import BaseModel, Field
  from typing import List, Optional
  from models.common import Source

  class CompanyProfile(BaseModel):
      """Basic company information"""
      company_name: str
      industry: Optional[str] = None
      company_size: Optional[str] = None
      business_model: Optional[str] = None
      products_services: List[str] = Field(default_factory=list)
      geographic_presence: List[str] = Field(default_factory=list)
      mission_statement: Optional[str] = None
      sources: List[Source] = Field(default_factory=list)

  class PainPoint(BaseModel):
      """Identified pain point or challenge"""
      description: str
      category: str = Field(description="operational, strategic, technical, market")
      evidence: str = Field(description="Why we think this is a pain")
      confidence: str = Field(description="high, medium, low")
      sources: List[Source] = Field(default_factory=list)

  class DecisionMaker(BaseModel):
      """Leadership/decision maker"""
      name: str
      title: str
      department: Optional[str] = None
      bio: Optional[str] = None
      linkedin_url: Optional[str] = None
      sources: List[Source] = Field(default_factory=list)

  class TechSignal(BaseModel):
      """Technology stack indicator"""
      technology: str
      category: str = Field(description="crm, marketing, data, communication, etc.")
      evidence: str
      confidence: str = Field(description="confirmed, likely, possible")
      sources: List[Source] = Field(default_factory=list)

  class ProspectCustomerProof(BaseModel):
      """Their customers/case studies (shows what matters to them)"""
      customer_name: Optional[str] = None
      customer_type: Optional[str] = None
      outcome_highlighted: str
      metrics_shown: List[str] = Field(default_factory=list)
      sources: List[Source] = Field(default_factory=list)

  class ProspectIntelligence(BaseModel):
      """Complete prospect intelligence package"""
      company_profile: CompanyProfile
      pain_points: List[PainPoint] = Field(default_factory=list)
      decision_makers: List[DecisionMaker] = Field(default_factory=list)
      tech_signals: List[TechSignal] = Field(default_factory=list)
      customer_proof: List[ProspectCustomerProof] = Field(default_factory=list)
  ```

#### Prospect Specialist Agents (5 total)
- [ ] Create `agents/prospect_specialists/company_analyst.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from models.prospect_intelligence import CompanyProfile
  from pydantic import BaseModel

  class CompanyProfileResult(BaseModel):
      company_profile: CompanyProfile

  company_analyst = Agent(
      name="Company Profile Analyst",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are a B2B company analyst extracting basic company information.

      Extract from prospect website:
      - Company name
      - Industry and market category
      - Company size indicators (employee count, customer count, etc.)
      - Business model (SaaS, Services, Product, etc.)
      - Products/services they offer
      - Geographic presence (headquarters, offices, markets served)
      - Mission statement or positioning

      Look in:
      - Homepage
      - About page
      - Product pages
      - Footer information

      Be factual. Only include what's explicitly stated.
      """,
      structured_output=True,
      output_schema=CompanyProfileResult
  )
  ```

- [ ] Create `agents/prospect_specialists/pain_point_analyst.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from models.prospect_intelligence import PainPoint
  from typing import List
  from pydantic import BaseModel

  class PainPointsResult(BaseModel):
      pain_points: List[PainPoint]

  pain_point_analyst = Agent(
      name="Pain Point Analyst",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are an expert at inferring company challenges from their content.

      APPROACH:
      - Look at what problems they solve for THEIR customers
      - Infer: If they solve X, they likely struggle with Y
      - Industry-common pain points for their market
      - Gaps or emphasis in their messaging

      For each pain point:
      - Description: The challenge/pain
      - Category: operational, strategic, technical, or market
      - Evidence: Why you believe this is a pain
      - Confidence: high (explicit), medium (implied), low (inferred)

      Examples:
      - If they emphasize "easy integration", they likely had integration pain
      - If they're in regulated industry, compliance is likely a pain
      - If they show fast growth, scaling is likely a pain

      Be specific and evidence-based.
      """,
      structured_output=True,
      output_schema=PainPointsResult
  )
  ```

- [ ] Create `agents/prospect_specialists/leadership_analyst.py` (WITH TOOLS):
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from agno.tools.firecrawl import FirecrawlTools
  from models.prospect_intelligence import DecisionMaker
  from typing import List
  from pydantic import BaseModel

  class LeadershipResult(BaseModel):
      decision_makers: List[DecisionMaker]

  leadership_analyst = Agent(
      name="Leadership & Decision Maker Analyst",
      model=OpenAIChat(id="gpt-4o"),
      tools=[FirecrawlTools(search=True, scrape=True)],
      instructions="""
      You are an expert at identifying company leadership and decision makers.

      STEP 1: Extract from scraped content
      - Check About page, Team page, Leadership page
      - Extract names, titles, bios
      - Look for C-suite, VPs, Directors

      STEP 2: If needed, use search tool
      - Search "[Company Name] leadership team"
      - Search "[Company Name] executive team"
      - Scrape LinkedIn company page if found

      For each decision maker:
      - Name: Full name
      - Title: Job title
      - Department: Department or function
      - Bio: Brief bio if available
      - LinkedIn URL: If found

      Focus on:
      - C-suite (CEO, CFO, CTO, CMO, etc.)
      - VPs (Sales, Marketing, Product, Engineering)
      - Directors in key functions

      Return comprehensive list of decision makers.
      """,
      structured_output=True,
      output_schema=LeadershipResult
  )
  ```

- [ ] Create `agents/prospect_specialists/tech_stack_analyst.py` (WITH TOOLS):
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from agno.tools.firecrawl import FirecrawlTools
  from models.prospect_intelligence import TechSignal
  from typing import List
  from pydantic import BaseModel

  class TechStackResult(BaseModel):
      tech_signals: List[TechSignal]

  tech_stack_analyst = Agent(
      name="Technology Stack Analyst",
      model=OpenAIChat(id="gpt-4o"),
      tools=[FirecrawlTools(search=True, scrape=True)],
      instructions="""
      You are an expert at identifying technology stack and integrations.

      STEP 1: Extract from scraped content
      - Integrations page (look for partner logos, API docs)
      - Technology partnerships mentioned
      - Platform/stack mentions in content
      - "Built with" or "Powered by" mentions

      STEP 2: Use search if needed
      - Search "[Company Name] technology stack"
      - Search "[Company Name] integrations"
      - Look for BuiltWith or similar data

      For each tech signal:
      - Technology: Name of the tool/platform
      - Category: CRM, marketing, data, communication, infrastructure, etc.
      - Evidence: Where/how you found this
      - Confidence: confirmed (on their site), likely (strong signal), possible (weak signal)

      Categories to look for:
      - CRM (Salesforce, HubSpot, etc.)
      - Marketing (Marketo, Pardot, etc.)
      - Communication (Slack, Teams, etc.)
      - Data (Snowflake, Databricks, etc.)
      - Infrastructure (AWS, Azure, GCP)
      - Other business tools

      Be evidence-based. Don't guess without signals.
      """,
      structured_output=True,
      output_schema=TechStackResult
  )
  ```

- [ ] Create `agents/prospect_specialists/customer_analyst.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat
  from models.prospect_intelligence import ProspectCustomerProof
  from typing import List
  from pydantic import BaseModel

  class CustomerProofResult(BaseModel):
      customer_proof: List[ProspectCustomerProof]

  customer_analyst = Agent(
      name="Customer & Proof Point Analyst",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are an expert at analyzing what the prospect values based on their own customer proof.

      Extract from prospect's website:
      - Their customer logos, case studies, testimonials
      - What outcomes they highlight with their customers
      - What metrics they showcase

      WHY THIS MATTERS:
      - What they highlight with THEIR customers shows what THEY value
      - If they show "50% time saved", they care about efficiency
      - If they show "2x revenue growth", they care about revenue impact

      For each customer proof element:
      - Customer name (if visible)
      - Customer type (industry, size if mentioned)
      - Outcome highlighted (the benefit they emphasize)
      - Metrics shown (specific numbers)

      This tells us what messaging will resonate with this prospect.
      """,
      structured_output=True,
      output_schema=CustomerProofResult
  )
  ```

#### Step 7 Executor
- [ ] Create `steps/step7_prospect_analysis.py`:
  ```python
  from agno.workflow.types import StepInput, StepOutput
  from agents.prospect_specialists.company_analyst import company_analyst
  from agents.prospect_specialists.pain_point_analyst import pain_point_analyst
  from agents.prospect_specialists.leadership_analyst import leadership_analyst
  from agents.prospect_specialists.tech_stack_analyst import tech_stack_analyst
  from agents.prospect_specialists.customer_analyst import customer_analyst

  def analyze_company_profile(step_input: StepInput) -> StepOutput:
      """Analyze prospect company profile"""
      scrape_data = step_input.get_step_content("batch_scrape")
      prospect_content = scrape_data.get("prospect_content", {})

      full_content = "\n\n---\n\n".join([
          f"URL: {url}\n\n{content}"
          for url, content in prospect_content.items()
      ])

      print("🏢 Analyzing company profile...")
      response = company_analyst.run(
          input=f"Extract company profile:\n\n{full_content}"
      )

      profile = response.content.company_profile
      print(f"✅ Company profile extracted")

      return StepOutput(content={"company_profile": profile.dict()})

  def analyze_pain_points(step_input: StepInput) -> StepOutput:
      """Infer prospect pain points"""
      scrape_data = step_input.get_step_content("batch_scrape")
      prospect_content = scrape_data.get("prospect_content", {})

      full_content = "\n\n---\n\n".join([
          f"URL: {url}\n\n{content}"
          for url, content in prospect_content.items()
      ])

      print("💡 Analyzing pain points...")
      response = pain_point_analyst.run(
          input=f"Infer pain points:\n\n{full_content}"
      )

      pains = response.content.pain_points
      print(f"✅ Found {len(pains)} pain points")

      return StepOutput(content={"pain_points": [p.dict() for p in pains]})

  def find_decision_makers(step_input: StepInput) -> StepOutput:
      """Find leadership team (uses FirecrawlTools)"""
      scrape_data = step_input.get_step_content("batch_scrape")
      prospect_content = scrape_data.get("prospect_content", {})
      prospect_domain = step_input.input.get("prospect_domain")

      full_content = "\n\n---\n\n".join([
          f"URL: {url}\n\n{content}"
          for url, content in prospect_content.items()
      ])

      print("👥 Finding decision makers (may search web)...")
      response = leadership_analyst.run(
          input=f"Find decision makers for {prospect_domain}:\n\n{full_content}"
      )

      decision_makers = response.content.decision_makers
      print(f"✅ Found {len(decision_makers)} decision makers")

      return StepOutput(content={"decision_makers": [dm.dict() for dm in decision_makers]})

  def analyze_tech_stack(step_input: StepInput) -> StepOutput:
      """Analyze tech stack (uses FirecrawlTools)"""
      scrape_data = step_input.get_step_content("batch_scrape")
      prospect_content = scrape_data.get("prospect_content", {})
      prospect_domain = step_input.input.get("prospect_domain")

      full_content = "\n\n---\n\n".join([
          f"URL: {url}\n\n{content}"
          for url, content in prospect_content.items()
      ])

      print("🔧 Analyzing tech stack (may search web)...")
      response = tech_stack_analyst.run(
          input=f"Analyze tech stack for {prospect_domain}:\n\n{full_content}"
      )

      tech_signals = response.content.tech_signals
      print(f"✅ Found {len(tech_signals)} tech signals")

      return StepOutput(content={"tech_signals": [ts.dict() for ts in tech_signals]})

  def analyze_customer_proof(step_input: StepInput) -> StepOutput:
      """Analyze their customer proof points"""
      scrape_data = step_input.get_step_content("batch_scrape")
      prospect_content = scrape_data.get("prospect_content", {})

      full_content = "\n\n---\n\n".join([
          f"URL: {url}\n\n{content}"
          for url, content in prospect_content.items()
      ])

      print("🎯 Analyzing their customer proof...")
      response = customer_analyst.run(
          input=f"Extract their customer proof:\n\n{full_content}"
      )

      proof = response.content.customer_proof
      print(f"✅ Found {len(proof)} customer proof points")

      return StepOutput(content={"customer_proof": [cp.dict() for cp in proof]})
  ```

#### Update Workflow for Phase 3
- [ ] Update `workflow.py` to add Step 7:
  ```python
  from steps.step7_prospect_analysis import (
      analyze_company_profile,
      analyze_pain_points,
      find_decision_makers,
      analyze_tech_stack,
      analyze_customer_proof
  )

  # Add after Step 6:
  Parallel(
      Step(name="analyze_company", executor=analyze_company_profile),
      Step(name="analyze_pain_points", executor=analyze_pain_points),
      Step(name="find_decision_makers", executor=find_decision_makers),
      Step(name="analyze_tech_stack", executor=analyze_tech_stack),
      Step(name="analyze_customer_proof", executor=analyze_customer_proof),
      name="prospect_intelligence"
  )
  ```

#### Phase 3 Testing
- [ ] Test each analyst individually
- [ ] Test agents with FirecrawlTools search capability
- [ ] Validate search quality
- [ ] Test with Phase 1-2 output
- [ ] Test with 3+ different prospect websites

---

## Phase 4: Playbook Generation (Step 8)
**Goal:** Generate Octave-style campaign playbook

### Atomic Tasks Checklist

#### Playbook Generator Agent
- [ ] Create `agents/playbook_generator.py`:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIChat

  playbook_generator = Agent(
      name="Playbook Generator",
      model=OpenAIChat(id="gpt-4o"),
      instructions="""
      You are a GTM strategist creating an Octave-style campaign playbook.

      You will receive:
      - VENDOR ELEMENTS: All GTM assets (offerings, case studies, proof points, etc.)
      - PROSPECT INTELLIGENCE: Company profile, pain points, decision makers, etc.

      Generate a campaign playbook in THIS EXACT FORMAT:

      # [Campaign Title]

      **Campaign Focus:** [One-sentence strategic angle]

      **Source:** [Vendor name] Playbook - [Strategic theme]

      ---

      ## Description

      [2-3 paragraphs explaining how vendor solves prospect's specific challenges.
      Include context about prospect's industry, stage, and key challenges.
      Explain why this is timely and relevant.]

      ---

      ## Target Personas

      [List 3-5 specific personas AT THE PROSPECT COMPANY]

      1. **[Title]** - [Why they care, their responsibilities]
      2. **[Title]** - [Why they care, their responsibilities]
      ...

      ---

      ## Executive Summary

      **Key Challenges:**
      - [Challenge → Solution bullet. Format: "When [situation], [approach] [outcome]."]
      - [Challenge → Solution bullet]
      - [Challenge → Solution bullet]
      - [Challenge → Solution bullet]

      ---

      ## Key Insights

      [4-6 strategic insights about the vendor-prospect fit]

      1. **[Insight title in bold]** - [1-2 sentences elaborating on the strategic insight]

      2. **[Insight title]** - [Elaboration]

      ...

      ---

      ## Approach Angle

      **Strategic Positioning:**

      1. **[Position 1 title]** - [How to lead this aspect of the conversation, what to emphasize]

      2. **[Position 2 title]** - [Strategic approach]

      3. **[Position 3 title]** - [Strategic approach]

      4. **[Position 4 title]** - [Strategic approach]

      ---

      ## Value Propositions (6-8 Total)

      ### For [Persona 1]:

      **1. [Value Prop Title]**
      [2-3 sentences detailing the value proposition. Tie to specific pain point.
      Back with vendor proof points. Make it persona-specific.]

      **2. [Value Prop Title]**
      [Detail]

      ### For [Persona 2]:

      **3. [Value Prop Title]**
      [Detail]

      ...

      ---

      ## Linked Elements

      **Offerings:**
      - [Product/Service 1]
      - [Product/Service 2]

      **Personas:**
      - [Persona 1]
      - [Persona 2]

      **Use Cases:**
      - [Use Case 1]
      - [Use Case 2]

      **Reference Customers:**
      - [Customer 1]
      - [Customer 2]

      ---

      **Last Updated:** [Today's date]
      **Campaign Owner:** [Vendor name]
      **Target:** [Prospect name]


      CRITICAL REQUIREMENTS:
      - Use SPECIFIC details from vendor elements (actual product names, case study results, etc.)
      - Use SPECIFIC details from prospect intelligence (actual pain points, decision makers, etc.)
      - Map vendor strengths to prospect needs explicitly
      - Make value props persona-specific
      - Back claims with proof points
      - Be strategic and actionable
      """,
      markdown=True,
      structured_output=False  # Returns markdown text
  )
  ```

#### Step 8 Executor
- [ ] Create `steps/step8_playbook_generation.py`:
  ```python
  from agno.workflow.types import StepInput, StepOutput
  from agents.playbook_generator import playbook_generator
  import json
  from datetime import datetime

  def generate_playbook(step_input: StepInput) -> StepOutput:
      """Generate complete campaign playbook"""

      print("📋 Generating campaign playbook...")

      # Collect ALL vendor elements from Step 6
      offerings_data = step_input.get_step_content("extract_offerings")
      case_studies_data = step_input.get_step_content("extract_case_studies")
      proof_points_data = step_input.get_step_content("extract_proof_points")
      value_props_data = step_input.get_step_content("extract_value_props")
      customers_data = step_input.get_step_content("extract_customers")
      use_cases_data = step_input.get_step_content("extract_use_cases")
      personas_data = step_input.get_step_content("extract_personas")
      differentiators_data = step_input.get_step_content("extract_differentiators")

      vendor_elements = {
          "offerings": offerings_data.get("offerings", []),
          "case_studies": case_studies_data.get("case_studies", []),
          "proof_points": proof_points_data.get("proof_points", []),
          "value_propositions": value_props_data.get("value_propositions", []),
          "reference_customers": customers_data.get("reference_customers", []),
          "use_cases": use_cases_data.get("use_cases", []),
          "target_personas": personas_data.get("target_personas", []),
          "differentiators": differentiators_data.get("differentiators", [])
      }

      # Collect ALL prospect intelligence from Step 7
      company_data = step_input.get_step_content("analyze_company")
      pains_data = step_input.get_step_content("analyze_pain_points")
      decision_makers_data = step_input.get_step_content("find_decision_makers")
      tech_stack_data = step_input.get_step_content("analyze_tech_stack")
      customer_proof_data = step_input.get_step_content("analyze_customer_proof")

      prospect_intelligence = {
          "company_profile": company_data.get("company_profile", {}),
          "pain_points": pains_data.get("pain_points", []),
          "decision_makers": decision_makers_data.get("decision_makers", []),
          "tech_signals": tech_stack_data.get("tech_signals", []),
          "customer_proof": customer_proof_data.get("customer_proof", [])
      }

      # Get vendor and prospect domains
      vendor_domain = step_input.input.get("vendor_domain")
      prospect_domain = step_input.input.get("prospect_domain")

      # Prepare comprehensive prompt
      prompt = f"""
      Generate an Octave-style campaign playbook for this vendor-prospect pairing.

      VENDOR: {vendor_domain}
      PROSPECT: {prospect_domain}
      TODAY'S DATE: {datetime.now().strftime("%B %d, %Y")}

      ===== VENDOR ELEMENTS =====

      {json.dumps(vendor_elements, indent=2)}

      ===== PROSPECT INTELLIGENCE =====

      {json.dumps(prospect_intelligence, indent=2)}

      =====

      Create a strategic campaign playbook following the EXACT format in your instructions.
      Make it specific, actionable, and backed by the data provided.
      """

      # Run agent
      response = playbook_generator.run(input=prompt)

      playbook_markdown = response.content

      print("✅ Playbook generated!")

      # Save to file
      filename = f"playbook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
      with open(filename, "w") as f:
          f.write(playbook_markdown)

      print(f"💾 Saved to {filename}")

      return StepOutput(
          content={
              "playbook_markdown": playbook_markdown,
              "filename": filename,
              "vendor_domain": vendor_domain,
              "prospect_domain": prospect_domain
          },
          success=True
      )
  ```

#### Update Workflow for Phase 4
- [ ] Update `workflow.py` to add Step 8:
  ```python
  from steps.step8_playbook_generation import generate_playbook

  # Add after Step 7:
  Step(name="generate_playbook", executor=generate_playbook)
  ```

#### Complete Workflow (All Phases)
- [ ] Final `workflow.py`:
  ```python
  from agno.workflow import Workflow, Step, Parallel

  # Import all step executors
  from steps.step1_domain_validation import validate_vendor_domain, validate_prospect_domain
  from steps.step2_homepage_scraping import scrape_vendor_homepage, scrape_prospect_homepage
  from steps.step3_initial_analysis import analyze_vendor_homepage, analyze_prospect_homepage
  from steps.step4_url_prioritization import prioritize_urls
  from steps.step5_batch_scraping import batch_scrape_selected_pages
  from steps.step6_vendor_extraction import (
      extract_offerings, extract_case_studies, extract_proof_points,
      extract_value_props, extract_customers, extract_use_cases,
      extract_personas, extract_differentiators
  )
  from steps.step7_prospect_analysis import (
      analyze_company_profile, analyze_pain_points, find_decision_makers,
      analyze_tech_stack, analyze_customer_proof
  )
  from steps.step8_playbook_generation import generate_playbook

  # Complete 8-step workflow
  octave_workflow = Workflow(
      name="Octave Clone - Complete Playbook Generator",
      description="Generate Octave-style campaign playbooks from vendor and prospect domains",
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

          # Step 6: Vendor element extraction (8 parallel)
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

          # Step 7: Prospect intelligence (5 parallel, 2 with tools)
          Parallel(
              Step(name="analyze_company", executor=analyze_company_profile),
              Step(name="analyze_pain_points", executor=analyze_pain_points),
              Step(name="find_decision_makers", executor=find_decision_makers),
              Step(name="analyze_tech_stack", executor=analyze_tech_stack),
              Step(name="analyze_customer_proof", executor=analyze_customer_proof),
              name="prospect_intelligence"
          ),

          # Step 8: Playbook generation
          Step(name="generate_playbook", executor=generate_playbook)
      ]
  )
  ```

#### Final Main Script
- [ ] Update `main.py`:
  ```python
  from workflow import octave_workflow
  import sys

  def main():
      if len(sys.argv) < 3:
          print("Usage: python main.py <vendor_domain> <prospect_domain>")
          print("Example: python main.py https://octavehq.com https://sendoso.com")
          sys.exit(1)

      vendor_domain = sys.argv[1]
      prospect_domain = sys.argv[2]

      print("=" * 80)
      print("OCTAVE CLONE MVP - PLAYBOOK GENERATOR")
      print("=" * 80)
      print(f"\nVendor:   {vendor_domain}")
      print(f"Prospect: {prospect_domain}\n")
      print("=" * 80)

      # Run workflow
      result = octave_workflow.run(input={
          "vendor_domain": vendor_domain,
          "prospect_domain": prospect_domain
      })

      print("\n" + "=" * 80)
      print("✅ PLAYBOOK GENERATION COMPLETE!")
      print("=" * 80)

      # Get result
      playbook_file = result.content.get("filename")
      print(f"\n📄 Playbook saved to: {playbook_file}")
      print("\nOpen the file to view your campaign playbook!")

  if __name__ == "__main__":
      main()
  ```

#### Phase 4 Testing
- [ ] Test playbook generation with Phase 1-3 output
- [ ] Validate markdown formatting
- [ ] Check that all sections are populated
- [ ] Verify vendor elements are referenced
- [ ] Verify prospect intelligence is used
- [ ] Test with 3+ different company pairs

---

## Phase 5: Polish & Testing
**Goal:** Production-ready MVP

### Atomic Tasks Checklist

#### Error Handling
- [ ] Add try-except blocks to all step executors
- [ ] Add validation for missing data
- [ ] Add graceful degradation for optional data
- [ ] Add retry logic for Firecrawl API calls
- [ ] Add timeout handling

#### Progress Indicators
- [ ] Add step completion messages
- [ ] Add progress percentages
- [ ] Add time estimates
- [ ] Add error/warning messages

#### Testing
- [ ] Create test suite with pytest
- [ ] Test each step individually
- [ ] Test workflow end-to-end
- [ ] Test with 10+ company pairs
- [ ] Test error scenarios
- [ ] Test edge cases (small sites, large sites, etc.)

#### Documentation
- [ ] Complete README.md
- [ ] Add usage examples
- [ ] Add configuration guide
- [ ] Add troubleshooting section
- [ ] Add API documentation

#### Optimization
- [ ] Profile workflow performance
- [ ] Optimize Firecrawl usage
- [ ] Optimize agent prompts
- [ ] Add caching where appropriate
- [ ] Reduce token usage

---

## Summary: Context Passing Quick Reference

### ✅ DO THIS
```python
# Access parallel outputs by name
vendor_data = step_input.get_step_content("validate_vendor")
prospect_data = step_input.get_step_content("validate_prospect")

# Always name your steps
Step(name="my_step", executor=my_function)

# Use .get() for safe access
value = data.get("key", "default")

# Check for None
if data is None:
    return StepOutput(content={"error": "..."}, success=False, stop=True)
```

### ❌ DON'T DO THIS
```python
# Don't access without step names after parallel
data = step_input.previous_step_content["vendor_urls"]  # ❌ Won't work

# Don't create unnamed steps
Step(executor=my_function)  # ❌ Can't access later

# Don't use direct dict access
value = data["key"]  # ❌ Will crash if missing
```

---

## Next Steps

1. **Start with Phase 1** - Get the foundation working
2. **Test incrementally** - Don't wait until the end
3. **Validate output** - Check data quality at each step
4. **Iterate on prompts** - Agent instructions are key
5. **Document issues** - Track what works and what doesn't

Good luck! 🚀
