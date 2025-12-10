# Playbook AI - Complete Sales Intelligence Pipeline

An intelligent sales playbook generator that analyzes vendor and prospect websites to extract GTM intelligence and generate production-ready campaign strategies in minutes.

## Overview

**Complete Phase 1-4 system** that transforms company domains into personalized sales playbooks:
1. **Intelligence Gathering** - Discovers and scrapes 20-30 pages per company with AI-powered prioritization
2. **Vendor Extraction** - Analyzes your GTM strategy with 8 parallel specialist agents
3. **Prospect Analysis** - Profiles target companies with 3 intelligence analysts
4. **Playbook Generation** - Creates sequencer-ready email campaigns, talk tracks, and battle cards

**End-to-end automation**: Input two domains → Get production-ready sales playbooks in ~3 minutes

## Features

### Core Capabilities
- **Complete 4-Phase Pipeline**: Intelligence gathering → Vendor extraction → Prospect analysis → Playbook generation
- **19 Specialist AI Agents**: 8 vendor specialists, 3 prospect analysts, 4 playbook creators, 2 general agents, 2 validators
- **12-Step Workflow**: Automated end-to-end pipeline with intelligent parallel processing
- **Production-Ready Outputs**: Sequencer-compatible email campaigns (Lemlist/Smartlead/Instantly ready)

### Technical Features
- **Parallel Processing**: Vendor and prospect analysis run simultaneously across all phases
- **Fail-Fast Validation**: Workflow stops immediately on critical errors
- **AI-Powered**: Uses OpenAI GPT-4o across all specialist agents for deep analysis
- **Firecrawl Integration**: Enterprise-grade web scraping with markdown output and caching
- **Structured Output**: Pydantic models for type-safe data extraction and validation
- **Flexible Deployment**: CLI or REST API via AgentOS integration
- **Domain Normalization**: Handles various input formats (sendoso.com, www.sendoso.com, https://sendoso.com)

## Installation

### Prerequisites

- Python 3.9+
- Firecrawl API key ([get one here](https://firecrawl.dev))
- OpenAI API key

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd octave-clone
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys:**

   Your API keys are already in `.env`. Verify they are set:
   ```bash
   cat .env | grep -E "(FIRECRAWL|OPENAI)_API_KEY"
   ```

## Usage

### CLI Usage (Recommended for Testing)

Run the complete Phase 1-4 workflow via command line:

```bash
python main.py https://octavehq.com https://sendoso.com
```

This executes all 12 steps and saves the complete playbook output to `phase1_output_[timestamp].json`.

**Domain flexibility**: Accepts any format (`octavehq.com`, `www.octavehq.com`, or `https://octavehq.com`)

### API Usage (Production Deployment)

Serve the workflow as a REST API endpoint using **AgentOS integration**:

```bash
python serve.py
```

Access the API at:
- **API Endpoint**: `POST http://localhost:7777/workflows/octave-clone-complete-sales-intelligence-pipeline/runs`
- **Control Plane UI**: `http://localhost:7777` (real-time workflow monitoring)
- **OpenAPI Docs**: `http://localhost:7777/docs` (interactive API documentation)

**Example API Call**:
```bash
curl -X POST 'http://localhost:7777/workflows/octave-clone-complete-sales-intelligence-pipeline/runs' \
  -H 'Content-Type: application/json' \
  -d '{
    "vendor_domain": "octavehq.com",
    "prospect_domain": "sendoso.com"
  }'
```

**API Features**:
- Streaming support (Server-Sent Events)
- Input validation with Pydantic
- Health check endpoint (`/health`)
- Production deployment guides (Docker, AWS, GCP, Azure)

📚 **See [API Serving Guide](docs/API_SERVING_GUIDE.md) for complete documentation and deployment instructions.**

### What Happens

The complete workflow executes **12 steps across 4 phases**:

#### Phase 1: Intelligence Gathering (Steps 1-5)
1. **Domain Validation**: Maps both domains in parallel to discover ~100 URLs per site
2. **Homepage Scraping**: Scrapes homepages for both companies in parallel
3. **Initial Analysis**: AI analyzes homepages (company basics, offerings, CTAs) in parallel
4. **URL Prioritization**: AI strategist selects top 10-15 most valuable URLs per company
5. **Batch Scraping**: Scrapes all prioritized pages (~20-30 pages per company)

#### Phase 2: Vendor Extraction (Step 6)
**8 Parallel Specialist Agents** extract GTM intelligence:
- Offerings & solutions
- Case studies & customer stories
- Proof points & results
- Value propositions
- Reference customers
- Use cases
- Target personas
- Competitive differentiators

#### Phase 3: Prospect Analysis (Step 7)
**3 Intelligence Analysts** profile the prospect:
- **Company Profile**: Industry, size, business model, key initiatives
- **Pain Points**: Challenges, priorities, decision drivers (with confidence scoring)
- **Buyer Personas**: 3-5 key decision makers with roles, priorities, and talking points

#### Phase 4: Playbook Generation (Step 8)
**5-Step Playbook Creation** process:
- **Step 8a**: Playbook summary and strategic overview
- **Step 8b-d**: Parallel generation of emails, talk tracks, and battle cards
- **Step 8e**: Final assembly and formatting

**Outputs**:
- **12 emails**: 4-touch sequences × 3 personas (sequencer-ready with subject/body)
- **3 talk tracks**: Elevator pitch, cold call script, discovery framework
- **3 battle cards**: Why We Win, Objection Handling, Competitive Positioning

### Output

Results are saved to `phase1_output_[timestamp].json` containing complete Phase 1-4 intelligence:

```json
{
  "phase1_scraped_content": {
    "vendor_content": {
      "https://octavehq.com/about": "markdown content...",
      "https://octavehq.com/platform": "markdown content..."
    },
    "prospect_content": {
      "https://sendoso.com/about": "markdown content..."
    },
    "stats": {
      "vendor_pages": 14,
      "prospect_pages": 18
    }
  },

  "phase2_vendor_elements": {
    "offerings": [
      {"name": "Product", "description": "...", "value_delivered": "...", "source": "URL"}
    ],
    "case_studies": [...],
    "proof_points": [...],
    "value_propositions": [...],
    "reference_customers": [...],
    "use_cases": [...],
    "target_personas": [...],
    "differentiators": [...]
  },

  "phase3_prospect_intelligence": {
    "company_profile": {
      "name": "Sendoso",
      "industry": "B2B SaaS",
      "employee_count": "200-500",
      "business_model": "SaaS gifting platform",
      "key_initiatives": [...]
    },
    "pain_points": [
      {
        "pain_point": "Low cold outreach response rates",
        "priority": 9,
        "confidence": 8,
        "suggested_talking_points": [...]
      }
    ],
    "buyer_personas": [
      {
        "title": "VP of Sales",
        "priority_score": 9,
        "key_priorities": [...],
        "talking_points": [...]
      }
    ]
  },

  "phase4_sales_playbook": {
    "playbook_summary": {
      "vendor_name": "Octave",
      "prospect_name": "Sendoso",
      "top_value_propositions": [...],
      "recommended_approach": "..."
    },
    "email_sequences": [
      {
        "persona_title": "VP of Sales",
        "touches": [
          {
            "touch_number": 1,
            "subject": "{{first_name}}, quick question about Sendoso's outbound strategy",
            "body": "Hi {{first_name}},\n\n..."
          }
        ]
      }
    ],
    "talk_tracks": {
      "elevator_pitch": "...",
      "cold_call_script": {...},
      "discovery_framework": {...}
    },
    "battle_cards": {
      "why_we_win": {...},
      "objection_handling": {...},
      "competitive_positioning": {...}
    },
    "quick_wins": [
      "Top 5 immediate actions to engage prospect"
    ]
  }
}
```

**Output Formats**:
- **JSON**: Complete structured data for programmatic use
- **Sequencer-Ready**: Email sequences can be directly imported to Lemlist/Smartlead/Instantly
- **Production-Ready**: Talk tracks and battle cards ready for sales team use

## Architecture

### Project Structure

```
octave-clone/
├── config.py                           # Configuration and environment variables
├── main.py                             # CLI entry point (runs complete Phase 1-4)
├── serve.py                            # AgentOS API server (production deployment)
├── workflow.py                         # 4 workflow definitions (phase1, phase1_2, phase1_2_3, phase1_2_3_4)
│
├── agents/                             # 19 Specialist AI Agents
│   ├── homepage_analyst.py             # Homepage content analyzer
│   ├── url_prioritizer.py              # Strategic URL selector
│   │
│   ├── vendor_specialists/             # Phase 2: 8 Parallel Specialists
│   │   ├── offerings_extractor.py
│   │   ├── case_study_extractor.py
│   │   ├── proof_points_extractor.py
│   │   ├── value_prop_extractor.py
│   │   ├── customer_extractor.py
│   │   ├── use_case_extractor.py
│   │   ├── persona_extractor.py
│   │   └── differentiator_extractor.py
│   │
│   ├── prospect_specialists/           # Phase 3: 3 Prospect Analysts
│   │   ├── company_analyst.py
│   │   ├── pain_point_analyst.py
│   │   └── buyer_persona_analyst.py
│   │
│   └── playbook_specialists/           # Phase 4: 4 Playbook Specialists
│       ├── playbook_orchestrator.py
│       ├── email_sequence_writer.py
│       ├── talk_track_creator.py
│       └── battle_card_builder.py
│
├── steps/                              # 8 Workflow Steps (12 total execution steps)
│   ├── step1_domain_validation.py      # Phase 1: Maps domains (2 parallel validators)
│   ├── step2_homepage_scraping.py      # Phase 1: Scrapes homepages (2 parallel scrapers)
│   ├── step3_initial_analysis.py       # Phase 1: AI analysis (2 parallel analyzers)
│   ├── step4_url_prioritization.py     # Phase 1: URL selection (1 AI strategist)
│   ├── step5_batch_scraping.py         # Phase 1: Batch scraping (1 scraper)
│   ├── step6_vendor_extraction.py      # Phase 2: 8 parallel vendor specialists
│   ├── step7_prospect_analysis.py      # Phase 3: 3 prospect analysts (2 parallel + 1 sequential)
│   └── step8_playbook_generation.py    # Phase 4: 5-step playbook creation
│
├── models/                             # 6 Pydantic Model Files (Type-Safe)
│   ├── common.py                       # Source model
│   ├── workflow_input.py               # Input validation with domain normalization
│   ├── vendor_elements.py              # 8 vendor element models
│   ├── prospect_intelligence.py        # Prospect analysis models
│   ├── playbook.py                     # 6 sequencer-ready playbook models
│   └── __init__.py
│
├── utils/                              # Helper Functions
│   ├── firecrawl_helpers.py            # 3 Firecrawl SDK wrappers
│   └── workflow_helpers.py             # 10+ validation and error handling helpers
│
└── docs/                               # Comprehensive Documentation
    ├── API_SERVING_GUIDE.md            # Complete API documentation (387 lines)
    ├── AGENTOS_IMPLEMENTATION_GUIDE.md # Production deployment guide (1,297 lines)
    └── phases/                         # Phase completion summaries
        ├── PHASE4_COMPLETION_SUMMARY.md
        └── ...
```

### Context Passing Pattern

The workflow uses Agno's context passing with proper step naming:

```python
# Parallel steps (Step 1)
Parallel(
    Step(name="validate_vendor", executor=validate_vendor_domain),
    Step(name="validate_prospect", executor=validate_prospect_domain),
    name="parallel_validation"
)

# Accessing parallel outputs (Step 2)
vendor_data = step_input.get_step_content("validate_vendor")
prospect_data = step_input.get_step_content("validate_prospect")
```

## Configuration

Edit `config.py` or set environment variables:

- `MAX_URLS_TO_SCRAPE`: Maximum URLs to batch scrape (default: 50)
- `BATCH_SCRAPE_TIMEOUT`: Timeout in seconds for batch scraping (default: 180)
- `MAX_URLS_TO_MAP`: Maximum URLs to discover per domain (default: 100)

## Testing

### Test Individual Steps

```bash
python tests/test_phase1.py
```

### Test End-to-End

```bash
python main.py https://octavehq.com https://sendoso.com
```

## Production Features

### Sequencer-Ready Email Campaigns
Email sequences are formatted for direct import to sales engagement platforms:
- **Format**: Each touch has `subject` and `body` fields
- **Personalization tokens**: `{{first_name}}`, `{{company_name}}`, `{{title}}`
- **Compatible with**: Lemlist, Smartlead, Instantly, Outreach, Salesloft
- **Structure**: 4-touch sequences × 3 personas = 12 emails per playbook

**Example Output**:
```json
{
  "touch_number": 1,
  "subject": "{{first_name}}, quick question about {{company_name}}'s outbound strategy",
  "body": "Hi {{first_name}},\n\nI noticed {{company_name}} is..."
}
```

### Battle Cards & Talk Tracks
Production-ready sales enablement materials:

**Talk Tracks**:
- **Elevator Pitch**: 30-second value proposition
- **Cold Call Script**: Opening, value prop, qualification questions, close
- **Discovery Framework**: 15-20 questions organized by category

**Battle Cards**:
- **Why We Win**: Top 5 competitive advantages with proof points
- **Objection Handling**: Common objections with responses (FIA framework)
- **Competitive Positioning**: Head-to-head comparison with alternatives

### Domain Normalization
Flexible input handling for various domain formats:
- ✅ `sendoso.com`
- ✅ `www.sendoso.com`
- ✅ `https://sendoso.com`
- ✅ `HTTPS://WWW.SENDOSO.COM/`

All normalized to: `https://sendoso.com`

## Documentation

### Comprehensive Guides
- **[API Serving Guide](docs/API_SERVING_GUIDE.md)** (387 lines)
  - Complete API documentation
  - Request/response formats
  - Production deployment options (Docker, AWS, GCP, Azure)
  - Security middleware (JWT, CORS, rate limiting)
  - Monitoring and health checks

- **[AgentOS Implementation Guide](docs/AGENTOS_IMPLEMENTATION_GUIDE.md)** (1,297 lines)
  - Architecture deep dive
  - Workflow patterns and best practices
  - Step-by-step implementation walkthrough
  - Troubleshooting and debugging
  - Production deployment checklist

### Phase Completion Summaries
- **Phase 2 Completion**: Vendor extraction implementation
- **Phase 3 Completion**: Prospect analysis implementation
- **Phase 4 Completion**: Playbook generation (November 2, 2025)

## Troubleshooting

### "FIRECRAWL_API_KEY not found"
- Check `.env` file exists and contains `FIRECRAWL_API_KEY=fc-...`
- Run: `source .env` (not needed in Python, but verifies file)

### "Batch scraping timeout"
- Increase `BATCH_SCRAPE_TIMEOUT` in `config.py`
- Reduce `MAX_URLS_TO_SCRAPE` to scrape fewer pages

### "AI analysis failed"
- Verify `OPENAI_API_KEY` is valid
- Check OpenAI API status: https://status.openai.com

## License

This project is licensed under the **Business Source License 1.1** (BSL 1.1).

### What this means:

- **Free for**: Development, testing, personal use, internal business use
- **Requires commercial license for**:
  - Offering this as a service to third parties
  - Incorporating into commercial products for sale
  - Reselling or white-labeling
- **Converts to Apache 2.0**: Four years after each release

### Commercial Licensing

For production commercial use, SaaS offerings, or enterprise deployments, contact:

**Brandon Guerrero**
Orchid Automation
Email: brandon@orchidautomation.com

See [LICENSE](LICENSE) for full terms.

## Support

For issues or questions, please open an issue on GitHub.

---

*Built by [Orchid Automation](https://orchidautomation.com) - GTM Engineering & Sales Intelligence*
