# Octave Clone MVP - Phase 1

An intelligent sales playbook generator that analyzes vendor and prospect websites to extract GTM intelligence and generate personalized campaign strategies.

## Overview

**Phase 1** implements the foundation intelligence gathering pipeline:
1. Domain validation and URL discovery
2. Homepage scraping and analysis
3. Strategic URL prioritization
4. Batch content scraping

## Features

- **Parallel Processing**: Vendor and prospect analysis run simultaneously
- **Fail-Fast Validation**: Workflow stops immediately on critical errors
- **AI-Powered**: Uses OpenAI GPT-4o for homepage analysis and URL prioritization
- **Firecrawl Integration**: Enterprise-grade web scraping with markdown output
- **Structured Output**: Pydantic models for type-safe data extraction

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

### CLI Usage

Run the complete workflow via command line:

```bash
python main.py https://octavehq.com https://sendoso.com
```

### API Usage (NEW!)

Serve the workflow as a REST API endpoint using AgentOS:

```bash
python serve.py
```

Access the API at:
- **API Endpoint**: `POST http://localhost:7777/workflows/octave-clone-complete-sales-intelligence-pipeline/runs`
- **Control Plane UI**: `http://localhost:7777`
- **OpenAPI Docs**: `http://localhost:7777/docs`

**Example API Call**:
```bash
curl -X POST 'http://localhost:7777/workflows/octave-clone-complete-sales-intelligence-pipeline/runs' \
  -H 'Content-Type: application/json' \
  -d '{
    "vendor_domain": "octavehq.com",
    "prospect_domain": "sendoso.com"
  }'
```

See [API Serving Guide](docs/API_SERVING_GUIDE.md) for complete API documentation.

### What Happens

The workflow executes 5 steps:

1. **Step 1**: Maps both domains to discover all URLs (~100 per site)
2. **Step 2**: Scrapes homepages for both companies
3. **Step 3**: AI analysis of homepages (company basics, offerings, CTAs)
4. **Step 4**: Selects top 10-15 most valuable URLs per company
5. **Step 5**: Batch scrapes all selected pages

### Output

Results are saved to `phase1_output_[timestamp].json` containing:

```json
{
  "vendor_content": {
    "https://example.com/about": "markdown content...",
    "https://example.com/products": "markdown content..."
  },
  "prospect_content": {
    "https://prospect.com/about": "markdown content..."
  },
  "vendor_urls_scraped": [...],
  "prospect_urls_scraped": [...],
  "stats": {
    "vendor_pages": 12,
    "prospect_pages": 14,
    "vendor_chars": 45000,
    "prospect_chars": 52000
  }
}
```

## Architecture

### Project Structure

```
octave-clone/
├── config.py                    # Configuration and environment variables
├── main.py                      # CLI entry point
├── serve.py                     # API server (AgentOS) - NEW!
├── workflow.py                  # Complete workflow definition (all phases)
│
├── agents/
│   ├── homepage_analyst.py      # Analyzes homepage content
│   └── url_prioritizer.py       # Selects top URLs to scrape
│
├── steps/
│   ├── step1_domain_validation.py    # Maps domains (parallel)
│   ├── step2_homepage_scraping.py    # Scrapes homepages (parallel)
│   ├── step3_initial_analysis.py     # AI analysis (parallel)
│   ├── step4_url_prioritization.py   # Selects URLs (sequential)
│   ├── step5_batch_scraping.py       # Batch scrapes (sequential)
│   ├── step6_vendor_extraction.py    # 8 parallel vendor specialists
│   ├── step7_prospect_analysis.py    # Prospect analysis (3 agents)
│   └── step8_playbook_generation.py  # Sales playbook generation
│
├── docs/
│   ├── API_SERVING_GUIDE.md         # API documentation - NEW!
│   └── AGENTOS_IMPLEMENTATION_GUIDE.md  # AgentOS details - NEW!
│
└── utils/
    ├── firecrawl_helpers.py     # Firecrawl SDK wrappers
    └── workflow_helpers.py      # Validation and error handling
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

## Next Phases

**Phase 2**: Vendor extraction with 8 parallel specialist agents
- Offerings, case studies, proof points, value propositions
- Reference customers, use cases, personas, differentiators

**Phase 3**: Prospect intelligence with 5 analysts
- Company profile, pain points, decision makers
- Tech stack (with search), customer proof analysis

**Phase 4**: Playbook generation
- Strategic campaign playbook in Octave format
- Persona-specific value propositions
- Linked elements and approach angles

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
