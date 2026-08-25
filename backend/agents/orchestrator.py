# backend/agents/orchestrator.py
from typing import Dict, Any

# Import specialist agents
from agents.intake_agent import process_incoming_donation
from agents.dispatch_agent import dispatch_volunteer
from agents.logistics_agent import analyze_inventory_health

# Import tools and utilities
from tools.inventory_db import get_donation, get_pending_donations, approve_donation
from utils.logger import orchestrator_logger, log_agent_action, log_hitl_event

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
        
        dispatch_info = None
        logistics_info = None
        
        # 3. Trigger Dispatch Agent
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
            
        # 4. Trigger Logistics Agent
        try:
            logistics_info = analyze_inventory_health(
                new_items=donation["items"],
                new_quantity=donation["quantity"]
            )
            log_agent_action(orchestrator_logger, "logistics_executed", {"shortages": len(logistics_info.get("shortages_flagged", []))})
        except Exception as e:
            orchestrator_logger.error(f"Logistics Agent failed: {e}")
            logistics_info = {"error": "Logistics agent failed, but donation was logged."}
            
        return {
            "status": "success", 
            "message": approval_msg,
            "dispatch": dispatch_info,
            "logistics": logistics_info
        }

orchestrator = PantryOrchestrator()