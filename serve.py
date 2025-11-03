"""
AgentOS API Server for Octave Clone MVP
Serves the complete sales intelligence workflow as a REST API endpoint.

Usage:
    python serve.py

API Endpoints:
    POST /workflows/octave-clone-complete-sales-intelligence-pipeline/runs
    GET  /docs (OpenAPI documentation)
    GET  /health (Health check)
    GET  /config (AgentOS configuration)

Example API Call:
    curl -X POST 'http://localhost:7777/workflows/octave-clone-complete-sales-intelligence-pipeline/runs' \
      -H 'Content-Type: application/json' \
      -d '{
        "vendor_domain": "octavehq.com",
        "prospect_domain": "sendoso.com"
      }'

Control Plane UI:
    http://localhost:7777
"""

from agno.os import AgentOS
from main import workflow
import os

# Initialize AgentOS with the complete sales intelligence workflow
agent_os = AgentOS(
    id="octave-sales-intelligence",
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
        "service": "octave-sales-intelligence-api",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("OCTAVE SALES INTELLIGENCE API SERVER")
    print("=" * 80)
    print("\n🚀 Starting AgentOS API Server...")
    print(f"\n📡 API Endpoint:")
    print(f"   POST http://localhost:7777/workflows/octave-clone-complete-sales-intelligence-pipeline/runs")
    print(f"\n📚 Documentation:")
    print(f"   http://localhost:7777/docs")
    print(f"\n🎛️  Control Plane UI:")
    print(f"   http://localhost:7777")
    print(f"\n💊 Health Check:")
    print(f"   http://localhost:7777/health")
    print("\n" + "=" * 80 + "\n")

    agent_os.serve(app="serve:app", reload=True, port=7777)
