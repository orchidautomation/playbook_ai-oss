# Playbook AI

**Turn any two websites into a complete sales playbook in minutes.**

Give Playbook AI your company's website and your prospect's website. It researches both, finds the perfect angles, and generates ready-to-use emails, call scripts, and battle cards.

## What You Get

For every prospect, Playbook AI creates:

| Output | What's Inside |
|--------|---------------|
| **Email Sequences** | 12 personalized emails (4 touches × 3 buyer personas) ready to import into Outreach, Salesloft, Apollo, or any sequencer |
| **Talk Tracks** | Cold call openers, discovery questions, and demo talking points tailored to each persona |
| **Battle Cards** | "Why We Win" differentiators, objection responses with proof points, and competitive positioning |
| **Buyer Personas** | 3-4 decision makers identified with their pain points, goals, and what messaging resonates |

**Example**: You sell Gong → You want to sell to Outreach → Playbook AI scrapes both sites, extracts Gong's case studies and value props, identifies Outreach's pain points and key buyers, then generates emails like:

> *"Hey {{first_name}}, noticed Outreach is scaling its pipeline management. Uber Freight faced similar challenges before improving their forecast accuracy by 30% with our platform..."*

## Quick Start

### 1. Install

```bash
git clone https://github.com/orchidautomation/playbook_ai-oss.git
cd playbook_ai-oss
pip install -r requirements.txt
```

### 2. Add your API keys

Create a `.env` file:
```
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
```

Need a Firecrawl key? [Get one free here](https://firecrawl.dev)

### 3. Run it

```bash
python main.py gong.io outreach.io
```

That's it. In ~3 minutes you'll have a complete playbook in `output/runs/{timestamp}/playbook.json`.

## How It Works

```
Your Website → [Playbook AI] → Complete Sales Playbook
Prospect's Website ↗
```

**Behind the scenes:**

1. **Discovers** 100+ pages on each website
2. **Prioritizes** the 20-30 most valuable pages (case studies, pricing, about, solutions)
3. **Extracts** your GTM elements: offerings, proof points, case studies, differentiators
4. **Analyzes** your prospect: company profile, pain points, key decision makers
5. **Generates** personalized playbook content mapped to each buyer persona

19 AI agents work in parallel to do in minutes what would take a sales team hours.

## Output Structure

```
output/runs/{timestamp}/
├── playbook.json          ← Everything you need (start here)
├── metadata.json          ← Run stats and timing
└── research/
    ├── vendor/            ← Raw intel about your company
    └── prospect/          ← Raw intel about prospect
```

The `playbook.json` file contains:

- **Executive Summary** - Strategic overview and recommended approach
- **Quick Wins** - Top 5 actions to take immediately
- **Email Sequences** - Copy/paste into your sequencer
- **Talk Tracks** - Scripts for cold calls, discovery, demos
- **Battle Cards** - Handle objections and position vs. competitors

## API Mode

Want to integrate this into your own tools? Run as an API:

```bash
python serve.py
```

Then call it:
```bash
curl -X POST 'http://localhost:8080/workflows/playbook-ai---sales-intelligence-pipeline/runs' \
  --data-urlencode 'message={"vendor_domain":"gong.io","prospect_domain":"outreach.io"}' \
  --data 'stream=false'
```

**Note**: The workflow ID uses three hyphens (`---`) and the API uses form-urlencoded data (not JSON).

- Control Plane UI at `http://localhost:8080`
- Swagger docs at `http://localhost:8080/docs`
- Health check at `http://localhost:8080/health`

## Requirements

- Python 3.9+
- OpenAI API key (uses GPT-4o)
- Firecrawl API key (for web scraping)

## Common Issues

**"FIRECRAWL_API_KEY not found"**
→ Make sure your `.env` file exists and has the key

**"Timeout during scraping"**
→ Some sites are slow. Increase `BATCH_SCRAPE_TIMEOUT` in `config.py`

**"No content extracted"**
→ Site might be blocking scrapers. Try a different prospect.

## License

**Business Source License 1.1** - Free for development, testing, and internal use. Commercial license required for SaaS/reselling.

| Use Case | Allowed? |
|----------|----------|
| Learning & development | ✅ Free |
| Internal sales teams | ✅ Free |
| Building a SaaS product | ❌ Contact us |

Converts to Apache 2.0 on December 9, 2029.

**Commercial licensing**: brandon@orchidautomation.com

---

Built by [Orchid Automation](https://orchidautomation.com)
