# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.intake_agent import process_incoming_donation
from tools.inventory_db import get_pending_donations, approve_donation
from agents.dispatch_agent import dispatch_volunteer # <-- Add this

app = FastAPI(title="PantryPilot Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DonationRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"message": "PantryPilot Agent Orchestrator is running"}

@app.post("/api/process-donation")
def process_donation(request: DonationRequest):
    result = process_incoming_donation(request.message)
    return {"status": "success", "agent_response": result}

@app.get("/api/pending-approvals")
def get_pending():
    return {"pending": get_pending_donations()}

@app.post("/api/approve/{donation_id}")
def approve(donation_id: str):
    # 1. Approve the donation in the DB
    approval_msg = approve_donation(donation_id)
    
    # 2. Find the donation details to pass to the Dispatch Agent
    donation = next((d for d in get_pending_donations() if d["id"] == donation_id), None)
    
    dispatch_info = None
    if donation:
        # 3. Trigger the Dispatch Agent
        dispatch_info = dispatch_volunteer(
            donation_id=donation["id"],
            dropoff_time=donation["notes"].replace("Dropoff at ", ""),
            items=donation["items"]
        )
        
    return {
        "status": "success", 
        "message": approval_msg,
        "dispatch": dispatch_info # <-- Send this to the frontend
    }