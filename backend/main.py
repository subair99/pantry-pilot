# backend/main.py
import json
import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import the central orchestrator and the DB tool
from agents.orchestrator import orchestrator
from tools.inventory_db import get_pending_donations

# Import observability tools
from utils.metrics import metrics
from utils.tracing import tracer

# 1. CREATE THE APP FIRST
app = FastAPI(title="PantryPilot Agent API")

# 2. ADD MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. DEFINE MODELS
class DonationRequest(BaseModel):
    message: str
    donor_email: str | None = None
    donor_phone: str | None = None

# 4. DEFINE ROUTES
@app.get("/")
def read_root():
    return {"message": "PantryPilot Agent Orchestrator is running"}

@app.post("/api/process-donation")
def process_donation(request: DonationRequest):
    """Receives a raw SMS/text and routes it to the Intake Agent via the Orchestrator."""
    start = time.time()
    span = tracer.start_span("process_donation", "Orchestrator")
    
    try:
        # Pass the optional contact info to the orchestrator
        result = orchestrator.process_incoming_message(
            request.message, 
            donor_email=request.donor_email, 
            donor_phone=request.donor_phone
        )
        span.finish("success")
        metrics.record_request("IntakeAgent", True, (time.time() - start) * 1000)
        return result
    except Exception as e:
        span.finish("error", {"error": str(e)})
        metrics.record_request("IntakeAgent", False, (time.time() - start) * 1000)
        return {"status": "error", "message": str(e)}

@app.get("/api/pending-approvals")
def get_pending():
    """Fetches items awaiting Human-in-the-Loop approval."""
    return {"pending": get_pending_donations()}

@app.post("/api/approve/{donation_id}")
def approve(donation_id: str):
    """Human approves the action. Orchestrator triggers Dispatch & Logistics agents."""
    return orchestrator.execute_post_approval_workflow(donation_id)

@app.get("/api/logs")
def get_agent_logs():
    """Fetches the structured JSON logs from the backend for the AgentLog UI."""
    log_file = os.path.join(os.path.dirname(__file__), "logs", "agent_activity.jsonl")
    
    if not os.path.exists(log_file):
        return {"logs": []}
        
    logs = []
    try:
        with open(log_file, "r") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
        # Return the most recent 50 logs, reversed so the newest appears first in the UI
        return {"logs": logs[-50:][::-1]}
    except Exception as e:
        return {"logs": [], "error": str(e)}

@app.get("/api/traces")
def get_traces():
    """Fetches recent agent traces for the Observability Dashboard."""
    return {"traces": tracer.get_recent_traces()}

@app.get("/api/metrics")
def get_metrics():
    """Fetches system metrics for the Observability Dashboard."""
    return {"metrics": metrics.get_summary()}