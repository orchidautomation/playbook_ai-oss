# API Serving Guide - AgentOS Integration

## Overview

The Octave Clone sales intelligence workflow can now be served as a REST API endpoint using AgentOS. This allows you to:

- Run the workflow via HTTP API calls
- Stream real-time progress updates
- Monitor runs through a web-based control plane
- Integrate with other systems and services

## Quick Start

### 1. Install Dependencies

Ensure you have AgentOS installed:

```bash
pip install agno
```

### 2. Start the API Server

```bash
python serve.py
```

The server will start on `http://localhost:7777`

### 3. Access the Control Plane UI

Open your browser to: `http://localhost:7777`

You'll see the AgentOS control plane where you can:
- Test the workflow interactively
- Monitor running workflows
- View workflow history
- Inspect results

## API Endpoints

### Execute Workflow

**Endpoint**: `POST /workflows/octave-clone-complete-sales-intelligence-pipeline/runs`

**Request Body**:
```json
{
  "vendor_domain": "octavehq.com",
  "prospect_domain": "sendoso.com"
}
```

**Example with curl**:
```bash
curl -X POST 'http://localhost:7777/workflows/octave-clone-complete-sales-intelligence-pipeline/runs' \
  -H 'Content-Type: application/json' \
  -d '{
    "vendor_domain": "octavehq.com",
    "prospect_domain": "sendoso.com"
  }'
```

**Example with Python**:
```python
import requests

response = requests.post(
    'http://localhost:7777/workflows/octave-clone-complete-sales-intelligence-pipeline/runs',
    json={
        "vendor_domain": "octavehq.com",
        "prospect_domain": "sendoso.com"
    },
    stream=True
)

# Stream real-time updates
for line in response.iter_lines():
    if line:
        print(line.decode())
```

**Example with JavaScript/TypeScript**:
```typescript
const response = await fetch(
  'http://localhost:7777/workflows/octave-clone-complete-sales-intelligence-pipeline/runs',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      vendor_domain: 'octavehq.com',
      prospect_domain: 'sendoso.com'
    })
  }
);

const result = await response.json();
console.log(result);
```

### Health Check

**Endpoint**: `GET /health`

```bash
curl http://localhost:7777/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "octave-sales-intelligence-api",
  "version": "1.0.0"
}
```

### OpenAPI Documentation

**Endpoint**: `GET /docs`

Interactive API documentation with request/response schemas and a built-in test interface.

Visit: `http://localhost:7777/docs`

### Configuration

**Endpoint**: `GET /config`

View the complete AgentOS configuration including registered workflows.

```bash
curl http://localhost:7777/config
```

## Response Format

The workflow returns a comprehensive JSON object with all phases:

```json
{
  "vendor_domain": "https://octavehq.com",
  "prospect_domain": "https://sendoso.com",
  "vendor_content": {
    "https://octavehq.com": "...",
    "https://octavehq.com/about": "..."
  },
  "prospect_content": {
    "https://sendoso.com": "...",
    "https://sendoso.com/about": "..."
  },
  "vendor_elements": {
    "offerings": [...],
    "case_studies": [...],
    "value_propositions": [...],
    "customers": [...],
    "use_cases": [...],
    "personas": [...],
    "differentiators": [...]
  },
  "company_profile": {...},
  "pain_points": [...],
  "buyer_personas": [...],
  "sales_playbook": {
    "summary": "...",
    "battle_cards": [...],
    "email_sequences": [...],
    "talk_tracks": [...]
  },
  "stats": {
    "vendor_chars": 50000,
    "prospect_chars": 45000,
    "total_urls_scraped": 20
  }
}
```

## Streaming Support

The API supports Server-Sent Events (SSE) for real-time progress updates:

```bash
curl -N -X POST 'http://localhost:7777/workflows/octave-clone-complete-sales-intelligence-pipeline/runs' \
  -H 'Content-Type: application/json' \
  -d '{
    "vendor_domain": "octavehq.com",
    "prospect_domain": "sendoso.com",
    "stream": true
  }'
```

You'll receive events as the workflow progresses through each phase:
- Domain validation
- Homepage scraping
- Content analysis
- Vendor extraction
- Prospect analysis
- Playbook generation

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn uvicorn[standard]

gunicorn serve:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

### Using Docker

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7777

CMD ["python", "serve.py"]
```

**Build and Run**:
```bash
docker build -t octave-api .
docker run -p 7777:7777 -e ANTHROPIC_API_KEY=your-key octave-api
```

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional
export AGENTOS_PORT=7777
export AGENTOS_HOST=0.0.0.0
export AGNO_TELEMETRY=false  # Disable telemetry in production
```

## Security Considerations

### Add JWT Authentication

```python
from agno.os.middleware import JWTMiddleware
import os

# Add to serve.py after getting the app
if os.getenv("JWT_SECRET"):
    app.add_middleware(
        JWTMiddleware,
        secret_key=os.getenv("JWT_SECRET"),
        algorithm="HS256",
        exclude_paths=["/health", "/docs", "/openapi.json"]
    )
```

### Add Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/workflows/{workflow_id}/runs")
@limiter.limit("10/minute")
async def rate_limited_endpoint(request: Request):
    # Your endpoint logic
    pass
```

### Add CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)
```

## Monitoring

### Connect to AgentOS Control Plane

1. Visit the AgentOS platform at https://app.agno.com
2. Add new OS instance
3. Select "Local" for development or "Live" for production
4. Enter your endpoint URL
5. Monitor all workflow runs in real-time

### Custom Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Comparison: CLI vs API

| Feature | CLI (`main.py`) | API (`serve.py`) |
|---------|-----------------|------------------|
| Execution | Command line | HTTP REST API |
| Integration | Scripts, cron jobs | Any HTTP client |
| Monitoring | Terminal output | Web UI + SSE |
| Concurrency | Single run | Multiple concurrent runs |
| Remote Access | SSH required | HTTP endpoint |
| Authentication | OS-level | JWT/API keys |
| Scalability | Single machine | Horizontal scaling |

Both methods use the **exact same workflow** - no code duplication!

## Troubleshooting

### Port Already in Use

```bash
# Change the port
agent_os.serve(app="serve:app", reload=True, port=8000)
```

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
pip install agno
```

### API Keys

Verify your `.env` file has:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### Workflow Timeout

For long-running workflows, increase the timeout:
```bash
gunicorn serve:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 600  # 10 minutes
```

## Next Steps

1. **Test Locally**: Run `python serve.py` and test via the UI
2. **Add Authentication**: Implement JWT middleware for security
3. **Deploy**: Use Docker or cloud platform (AWS, GCP, Azure)
4. **Monitor**: Connect to AgentOS control plane for visibility
5. **Scale**: Add load balancer and multiple instances

## Resources

- [AgentOS Documentation](https://docs.agno.com)
- [AgentOS Implementation Guide](/docs/AGENTOS_IMPLEMENTATION_GUIDE.md)
- [Workflow Documentation](/docs/README.md)

---

**Questions or Issues?** Check the main [AGENTOS_IMPLEMENTATION_GUIDE.md](./AGENTOS_IMPLEMENTATION_GUIDE.md) for comprehensive details.
