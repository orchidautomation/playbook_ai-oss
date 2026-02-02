"""
Playbook AI - API Server
Serves the complete sales intelligence workflow as a REST API endpoint.

Usage:
    python serve.py

API Endpoints:
    POST /workflows/playbook-ai-sales-intelligence-pipeline/runs
    GET  /docs (OpenAPI documentation)
    GET  /health (Health check)
    GET  /config (AgentOS configuration)

Example API Call:
    curl -X POST 'http://localhost:8080/workflows/playbook-ai-sales-intelligence-pipeline/runs' \
      -H 'Content-Type: application/json' \
      -d '{
        "message": {
          "vendor_domain": "gong.io",
          "prospect_domain": "sendoso.com"
        }
      }'

    Note: The workflow input must be wrapped in a "message" object (Agno AgentOS API format).

Control Plane UI:
    http://localhost:8080
"""

from agno.os import AgentOS
from main import workflow
import os

# Initialize AgentOS with the complete sales intelligence workflow
agent_os = AgentOS(
    id="playbook-ai-sales-intelligence",
    description="Complete sales intelligence pipeline API - End-to-end vendor analysis, prospect research, and sales playbook generation",
    workflows=[workflow],
)

# Get the FastAPI app
app = agent_os.get_app()

# Add custom health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "playbook-ai-api",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PLAYBOOK AI - SALES INTELLIGENCE API SERVER")
    print("=" * 80)
    print("\n🚀 Starting AgentOS API Server...")
    print(f"\n📡 API Endpoint:")
    print(f"   POST http://localhost:8080/workflows/playbook-ai-sales-intelligence-pipeline/runs")
    print(f"\n📚 Documentation:")
    print(f"   http://localhost:8080/docs")
    print(f"\n🎛️  Control Plane UI:")
    print(f"   http://localhost:8080")
    print(f"\n💊 Health Check:")
    print(f"   http://localhost:8080/health")
    print("\n" + "=" * 80 + "\n")

    agent_os.serve(app="serve:app", reload=True, port=8080)
