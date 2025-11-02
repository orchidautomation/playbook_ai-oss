# Architecture Documentation

## Overview

Octave is a sales intelligence gathering platform built on the Agno workflow framework. It automates the process of collecting, analyzing, and prioritizing web content from both vendor (your company) and prospect (target customer) websites to generate actionable sales insights.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT LAYER                              │
│                    (vendor_domain, prospect_domain)                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                       AGNO WORKFLOW ORCHESTRATOR                        │
│                                                                         │
│  • Manages step execution (parallel/sequential)                        │
│  • Handles state management and data flow                              │
│  • Enforces fail-fast validation patterns                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         PROCESSING PIPELINE                             │
│                                                                         │
│  Phase 1: Discovery (Parallel)                                         │
│  ├─ Domain Validation                                                  │
│  ├─ Homepage Scraping                                                  │
│  └─ Initial Analysis                                                   │
│                                                                         │
│  Phase 2: Intelligence Gathering (Sequential)                          │
│  ├─ URL Prioritization                                                 │
│  └─ Batch Scraping                                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL SERVICES LAYER                           │
│                                                                         │
│  ├─ Firecrawl API (Web scraping & URL mapping)                        │
│  ├─ OpenAI API (AI analysis via Agno agents)                          │
│  └─ MCP Servers (Perplexity, Exa, others)                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                           OUTPUT LAYER                                  │
│                  (Structured sales intelligence data)                   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Workflow Steps (`/steps`)

The pipeline consists of 5 main steps organized into 2 phases:

#### Phase 1: Discovery (Parallel Execution)

**Step 1: Domain Validation** (`step1_domain_validation.py`)
- **Purpose**: Validate domains and discover all URLs
- **Execution**: Parallel (vendor + prospect)
- **Functions**:
  - `validate_vendor_domain()` - Validates and maps vendor domain
  - `validate_prospect_domain()` - Validates and maps prospect domain
- **Output**: Domain URLs (up to 5000 per domain)
- **Key Logic**: Uses Firecrawl map API to discover all site URLs

**Step 2: Homepage Scraping** (`step2_homepage_scraping.py`)
- **Purpose**: Scrape homepage content in multiple formats
- **Execution**: Parallel (vendor + prospect)
- **Functions**:
  - `scrape_vendor_homepage()` - Scrapes vendor homepage
  - `scrape_prospect_homepage()` - Scrapes prospect homepage
- **Output**: Markdown, HTML, and metadata
- **Key Logic**: Uses Firecrawl scrape API with multiple format support

**Step 3: Initial Analysis** (`step3_initial_analysis.py`)
- **Purpose**: AI-powered homepage analysis
- **Execution**: Parallel (vendor + prospect)
- **Functions**:
  - `analyze_vendor_homepage()` - Analyzes vendor content
  - `analyze_prospect_homepage()` - Analyzes prospect content
- **Output**: Structured homepage analysis
- **Key Logic**: Uses `homepage_analyst` agent for content analysis

#### Phase 2: Intelligence Gathering (Sequential Execution)

**Step 4: URL Prioritization** (`step4_url_prioritization.py`)
- **Purpose**: Select most valuable URLs for deep scraping
- **Execution**: Sequential
- **Functions**:
  - `prioritize_urls()` - AI-powered URL selection
- **Output**: Top 10-15 URLs per company with reasoning
- **Key Logic**: Uses `url_prioritizer` agent to select high-value URLs

**Step 5: Batch Scraping** (`step5_batch_scraping.py`)
- **Purpose**: Scrape all selected URLs in batch
- **Execution**: Sequential
- **Functions**:
  - `batch_scrape_selected_pages()` - Batch scrapes selected URLs
- **Output**: Complete markdown content for all selected pages
- **Key Logic**: Uses Firecrawl batch API with proportional limiting

### 2. AI Agents (`/agents`)

**Homepage Analyst** (`homepage_analyst.py`)
- **Model**: GPT-4
- **Purpose**: Analyze homepage content for key business information
- **Output**: Structured analysis of company offerings, value props, etc.

**URL Prioritizer** (`url_prioritizer.py`)
- **Model**: GPT-4
- **Purpose**: Select most valuable URLs for sales intelligence
- **Output**: Structured list of URLs with selection reasoning
- **Structured Output**: Uses Pydantic models for type safety

### 3. Utility Modules (`/utils`)

**Firecrawl Helpers** (`firecrawl_helpers.py`)
- `map_website()` - Discovers all URLs on a domain
- `scrape_url()` - Scrapes single URL with multiple formats
- `batch_scrape_urls()` - Batch scrapes multiple URLs efficiently

**Workflow Helpers** (`workflow_helpers.py`)
- `validate_single_domain()` - Domain format validation
- `validate_previous_step_data()` - Extracts and validates step outputs
- `create_error_response()` - Standardized error handling
- `create_success_response()` - Standardized success responses

### 4. Configuration (`config.py`)

Central configuration for all pipeline settings:
- API keys and endpoints
- Rate limiting and timeouts
- URL mapping and scraping limits
- Batch processing constraints

### 5. Data Models (`/models`)

**Common Models** (`common.py`)
- Shared Pydantic models for type safety
- Validation schemas for workflow inputs/outputs

**Vendor Element Models** (`vendor_elements.py`)
- Domain-specific models for vendor data structures
- Type definitions for sales intelligence entities

## Data Flow Architecture

### Parallel Block Pattern

```python
# Step 1: Parallel validation
parallel_validation = {
    "validate_vendor": validate_vendor_domain(),
    "validate_prospect": validate_prospect_domain()
}

# Accessing in Step 2
parallel_results = step_input.get_step_content("parallel_validation")
vendor_data = parallel_results.get("validate_vendor")
```

### Sequential Data Access Pattern

```python
# Step 4: Sequential access to previous step
url_data = validate_previous_step_data(
    step_input,
    required_keys=["vendor_selected_urls", "prospect_selected_urls"],
    step_name="Step 4 (URL prioritization)"
)
```

### Fail-Fast Validation Pattern

Every step implements fail-fast validation:

```python
def step_function(step_input: StepInput) -> StepOutput:
    # 1. Validate previous step data
    if not previous_data or not has_required_fields(previous_data):
        return create_error_response("Previous step failed", stop=True)

    # 2. Validate environment/config
    if not required_env_var:
        return create_error_response("Config missing", stop=True)

    # 3. Process step
    result = process_data()

    # 4. Return success or fail
    if result["success"]:
        return create_success_response(data)
    else:
        return create_error_response(error, stop=True)
```

## Design Patterns

### 1. Fail-Fast Validation
- No graceful degradation for critical data
- All analysis is mandatory
- Stop workflow immediately on any failure
- Clear error messages with context

### 2. Parallel Processing
- Vendor and prospect operations run simultaneously
- Reduces total pipeline execution time
- Independent data paths until aggregation phase

### 3. Structured Outputs
- Pydantic models for type safety
- Consistent response formats
- Easy data extraction and validation

### 4. Progressive Refinement
- Map all URLs → Prioritize → Deep scrape
- Reduces unnecessary API calls
- Focuses compute on high-value pages

### 5. Internal Validation
- Validation logic embedded in steps
- No separate validation gate steps
- Cleaner workflow structure

## External Dependencies

### Required Services

1. **Firecrawl API**
   - URL mapping and discovery
   - Web scraping with multiple formats
   - Batch scraping capabilities
   - Rate limiting: Configurable via `config.py`

2. **OpenAI API**
   - Powers Agno agents (homepage_analyst, url_prioritizer)
   - Model: GPT-4
   - Structured output support

3. **Agno Framework**
   - Workflow orchestration
   - Step execution management
   - Agent runtime

### Optional Services (MCP)

- **Perplexity MCP**: Web search augmentation
- **Exa MCP**: Company research and LinkedIn search
- **Firecrawl MCP**: Enhanced scraping capabilities

## Environment Configuration

Required environment variables:

```bash
# Core APIs
OPENAI_API_KEY=<your-key>
FIRECRAWL_API_KEY=<your-key>

# Optional MCP services
PERPLEXITY_API_KEY=<your-key>  # If using Perplexity MCP
EXA_API_KEY=<your-key>         # If using Exa MCP
```

Configuration file: `config.py`

## Error Handling Strategy

### Three-Level Error Handling

1. **Step-Level Validation**
   - Domain format validation
   - Previous step data validation
   - Environment variable checks

2. **API-Level Error Handling**
   - Firecrawl API failures
   - OpenAI API failures
   - Rate limiting and timeouts

3. **Workflow-Level Propagation**
   - Errors return `StepOutput(stop=True)`
   - Workflow halts immediately
   - Clear error messages in output

### Error Response Format

```python
{
    "error": "Clear error message with context",
    "stop": True  # Halts workflow
}
```

## Performance Characteristics

### Execution Time Estimates

- **Step 1** (Domain Validation): 10-30s per domain (parallel)
- **Step 2** (Homepage Scraping): 5-15s per homepage (parallel)
- **Step 3** (Initial Analysis): 10-20s per analysis (parallel)
- **Step 4** (URL Prioritization): 15-30s (sequential)
- **Step 5** (Batch Scraping): 60-300s depending on URL count

**Total Pipeline**: ~2-6 minutes for typical execution

### Resource Limits

- **URL Mapping**: 5000 URLs per domain (configurable)
- **URL Prioritization**: First 200 URLs processed
- **Batch Scraping**: Configurable max (proportionally distributed)
- **Batch Timeout**: 300 seconds default

## Extension Points

### Adding New Steps

1. Create step file in `/steps/`
2. Define step function(s) with `StepInput` → `StepOutput`
3. Implement fail-fast validation
4. Add to workflow in main execution file
5. Update this documentation

### Adding New Agents

1. Create agent file in `/agents/`
2. Define agent with Agno framework
3. Specify model, instructions, and structured outputs
4. Import and use in relevant steps

### Adding New Data Models

1. Define Pydantic models in `/models/`
2. Use for type validation in agents
3. Import in steps for validation

## Security Considerations

1. **API Key Management**
   - Store in environment variables
   - Never commit to version control
   - Use `.env` file locally

2. **Input Validation**
   - Domain format validation
   - URL sanitization
   - Content size limits

3. **Rate Limiting**
   - Respect API rate limits
   - Implement backoff strategies
   - Monitor usage

## Monitoring & Debugging

### Logging Strategy

- Step-level progress indicators (emoji-based)
- Detailed error messages with context
- Character counts for content validation
- URL counts at each stage

### Debug Points

1. Check `parallel_validation` output after Step 1
2. Verify homepage content length in Step 2
3. Inspect AI analysis quality in Step 3
4. Review URL selection reasoning in Step 4
5. Monitor batch scraping success rates in Step 5

## Future Architecture Considerations

### Potential Enhancements

1. **Caching Layer**
   - Cache mapped URLs for domains
   - Cache scraped content with TTL
   - Reduce redundant API calls

2. **Incremental Processing**
   - Resume failed workflows
   - Checkpoint after each step
   - Partial result recovery

3. **Parallel Batch Scraping**
   - Split Step 5 into parallel vendor/prospect scraping
   - Faster total execution time

4. **Result Storage**
   - Airtable integration for results
   - Historical analysis tracking
   - Trend analysis over time

5. **Visual Analysis**
   - Screenshot capture and analysis
   - Trust indicator detection
   - Visual quality metrics

## Directory Structure

```
octave-clone/
├── steps/                      # Workflow step implementations
│   ├── step1_domain_validation.py
│   ├── step2_homepage_scraping.py
│   ├── step3_initial_analysis.py
│   ├── step4_url_prioritization.py
│   └── step5_batch_scraping.py
├── agents/                     # AI agent definitions
│   ├── homepage_analyst.py
│   └── url_prioritizer.py
├── utils/                      # Utility functions
│   ├── firecrawl_helpers.py
│   └── workflow_helpers.py
├── models/                     # Data models
│   ├── common.py
│   └── vendor_elements.py
├── config.py                   # Central configuration
├── agno-example-workflow.py    # Main workflow execution
└── ARCHITECTURE.md            # This file
```

## Version History

- **Phase 1 Complete** (2adf6dc): Intelligence Gathering Pipeline
  - Steps 1-5 implemented
  - Parallel processing for vendor/prospect
  - Fail-fast validation throughout
  - AI-powered analysis and prioritization
