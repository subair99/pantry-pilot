# backend/main.py
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Import the central orchestrator and the DB tool
from agents.orchestrator import orchestrator
from tools.inventory_db import get_pending_donations

# Import observability tools
from utils.metrics import metrics
from utils.tracing import tracer

# Import queue processor and voice tool
from tools.file_queue import process_queue
from tools.voice_mcp import transcribe_voice_to_text

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
    """Legacy endpoint for direct API calls (optional)."""
    start = time.time()
    span = tracer.start_span("process_donation", "Orchestrator")
    try:
        result = orchestrator.process_incoming_message(
            request.message, 
            donor_email=request.donor_email, 
            donor_phone=request.donor_phone,
            source="SMS"
        )
        span.finish("success")
        metrics.record_request("IntakeAgent", True, (time.time() - start) * 1000)
        return result
    except Exception as e:
        span.finish("error", {"error": str(e)})
        return {"status": "error", "message": str(e)}

@app.post("/api/scan-queue")
def scan_queue():
    """
    Scans the received_messages folders (SMS -> Email -> Voice), 
    processes new files, and moves them to processed folders.
    """
    start = time.time()
    span = tracer.start_span("scan_queue", "Orchestrator")
    try:
        count = process_queue(orchestrator, transcribe_voice_to_text)
        span.finish("success")
        
        # ✅ RECORD METRICS HERE
        latency = (time.time() - start) * 1000
        metrics.record_request("QueueProcessor", True, latency)
        
        return {"status": "success", "processed_count": count}
    except Exception as e:
        span.finish("error", {"error": str(e)})
        metrics.record_request("QueueProcessor", False, (time.time() - start) * 1000)
        return {"status": "error", "message": str(e)}

@app.get("/api/pending-approvals")
def get_pending():
    """Fetches items awaiting Human-in-the-Loop approval."""
    return {"pending": get_pending_donations()}

@app.post("/api/approve/{donation_id}")
def approve(donation_id: str):
    """Human approves the action. Orchestrator triggers Dispatch & Logistics agents."""
    start = time.time()
    span = tracer.start_span("approve_donation", "Orchestrator")
    try:
        result = orchestrator.execute_post_approval_workflow(donation_id)
        span.finish("success")
        
        # ✅ RECORD METRICS HERE
        latency = (time.time() - start) * 1000
        metrics.record_request("ApprovalWorkflow", True, latency)
        
        return result
    except Exception as e:
        span.finish("error", {"error": str(e)})
        metrics.record_request("ApprovalWorkflow", False, (time.time() - start) * 1000)
        return {"status": "error", "message": str(e)}

@app.get("/api/download-receipt/{donation_id}")
def download_receipt(donation_id: str):
    """Downloads the tax receipt PDF for an approved donation."""
    receipt_path = Path(__file__).parent / "generated_receipts" / f"receipt_{donation_id}.pdf"
    
    if not receipt_path.exists():
        return {"status": "error", "message": "Receipt not found"}
    
    return FileResponse(
        path=str(receipt_path),
        media_type="application/pdf",
        filename=f"tax_receipt_{donation_id}.pdf"
    )

@app.get("/api/logs")
def get_agent_logs():
    log_file = os.path.join(os.path.dirname(__file__), "logs", "agent_activity.jsonl")
    if not os.path.exists(log_file):
        return {"logs": []}
    logs = []
    try:
        with open(log_file, "r") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
        return {"logs": logs[-50:][::-1]}
    except Exception as e:
        return {"logs": [], "error": str(e)}

@app.get("/api/traces")
def get_traces():
    return {"traces": tracer.get_recent_traces()}

@app.get("/api/metrics")
def get_metrics():
    return {"metrics": metrics.get_summary()}