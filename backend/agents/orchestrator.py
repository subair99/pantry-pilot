# backend/agents/orchestrator.py
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Import specialist agents
from agents.intake_agent import process_incoming_donation
from agents.dispatch_agent import dispatch_volunteer
from agents.logistics_agent import analyze_inventory_health

# Import tools and utilities
from tools.inventory_db import get_donation, get_pending_donations, approve_donation
from tools.receipt_generator import generate_tax_receipt
from utils.logger import orchestrator_logger, log_agent_action, log_hitl_event

def save_approved_donation(donation_data: dict):
    """Saves the approved donation data to a JSON file for the history dashboard."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    db_file = data_dir / "approved_donations.json"
    
    # Load existing data
    approved_list = []
    if db_file.exists():
        try:
            with open(db_file, "r") as f:
                approved_list = json.load(f)
        except json.JSONDecodeError:
            approved_list = []
            
    # Append new donation
    approved_list.append(donation_data)
    
    # Save back to file
    with open(db_file, "w") as f:
        json.dump(approved_list, f, indent=2)

class PantryOrchestrator:
    def __init__(self):
        self.name = "PantryPilot Orchestrator"
        orchestrator_logger.info("Orchestrator initialized and ready.")

    def process_incoming_message(self, raw_message: str, donor_email: str = None, donor_phone: str = None, source: str = None) -> Dict[str, Any]:
        orchestrator_logger.info(f"Received new task: {raw_message[:50]}...")
        
        # Pass the source to the intake agent
        result = process_incoming_donation(raw_message, donor_email, donor_phone, source)
        
        log_agent_action(orchestrator_logger, "intake_complete", {"status": "pending_human_approval"})
        return {"status": "success", "agent_response": result}

    def execute_post_approval_workflow(self, donation_id: str) -> Dict[str, Any]:
        orchestrator_logger.info(f"Human approved donation {donation_id}. Starting downstream agents.")
        
        # 1. Fetch the donation FIRST (before changing its status)
        donation = get_donation(donation_id)
        if not donation:
            orchestrator_logger.warning(f"Donation {donation_id} not found in database.")
            return {"status": "error", "message": "Donation not found."}
            
        # 2. Approve it
        approval_msg = approve_donation(donation_id)
        
        # 3. Generate Tax Receipt
        try:
            receipt_path = generate_tax_receipt(donation, donation_id)
            orchestrator_logger.info(f"Tax receipt generated successfully: {receipt_path}")
        except Exception as e:
            orchestrator_logger.error(f"Failed to generate tax receipt: {e}")
            receipt_path = None
        
        dispatch_info = None
        logistics_info = None
        
        # 4. Trigger Dispatch Agent
        try:
            dispatch_info = dispatch_volunteer(
                donation_id=donation["id"],
                dropoff_time=donation["notes"].replace("Dropoff at ", ""),
                items=donation["items"],
                quantity=donation["quantity"],
                donor_name=donation["donor"],
                donor_email=donation.get("donor_email"),
                donor_phone=donation.get("donor_phone")
            )
            log_agent_action(orchestrator_logger, "dispatch_executed", {"volunteer": dispatch_info.get("volunteer_name")})
        except Exception as e:
            orchestrator_logger.error(f"Dispatch Agent failed: {e}")
            dispatch_info = {"error": "Dispatch agent failed, but donation was logged."}
            
        # 5. Trigger Logistics Agent
        try:
            logistics_info = analyze_inventory_health(
                new_items=donation["items"],
                new_quantity=donation["quantity"]
            )
            log_agent_action(orchestrator_logger, "logistics_executed", {"shortages": len(logistics_info.get("shortages_flagged", []))})
        except Exception as e:
            orchestrator_logger.error(f"Logistics Agent failed: {e}")
            logistics_info = {"error": "Logistics agent failed, but donation was logged."}
            
        # ✅ SAVE APPROVED DONATION FOR HISTORY DASHBOARD ✅
        save_approved_donation({
            "id": donation_id,
            "donor_name": donation.get("donor", "Unknown"),
            "donor_email": donation.get("donor_email", "N/A"),
            "donor_phone": donation.get("donor_phone", "N/A"),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
            
        return {
            "status": "success", 
            "message": approval_msg,
            "receipt_path": receipt_path,
            "dispatch": dispatch_info,
            "logistics": logistics_info
        }

orchestrator = PantryOrchestrator()