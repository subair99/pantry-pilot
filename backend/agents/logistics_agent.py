# backend/agents/logistics_agent.py
import os
import json
import random
from utils.logger import logistics_logger, log_agent_action, log_hitl_event
from utils.guardrails import PantryGuardrails

# Mock historical demand data for the hackathon demo
MOCK_HISTORICAL_DEMAND = {
    "pasta": {"weekly_avg": 50, "current_stock": 12},
    "apples": {"weekly_avg": 30, "current_stock": 20},
    "protein": {"weekly_avg": 40, "current_stock": 5}, # Critically low!
    "canned_vegetables": {"weekly_avg": 25, "current_stock": 40}
}

def analyze_inventory_health(new_items: list, new_quantity: int) -> dict:
    """
    Logistics Agent Core: Analyzes current stock against historical demand 
    to flag shortages or overstock situations.
    """
    print(f"📦 Logistics Agent analyzing inventory health...")
    
    # ️ GUARDRAIL: Prevent the agent from making false promises about distribution
    is_safe, safety_msg = PantryGuardrails.check_input_safety(f"Logistics analysis for {new_items}")
    if not is_safe:
        log_hitl_event(logistics_logger, "input_safety", "BLOCKED", {"reason": safety_msg})
        return {"status": "error", "message": safety_msg}

    # Simulate analysis
    shortages = []
    surpluses = []
    
    # In a real app, this would query a vector DB or time-series DB. 
    # For the demo, we use our mock data.
    for item_key, data in MOCK_HISTORICAL_DEMAND.items():
        deficit = data["weekly_avg"] - data["current_stock"]
        if deficit > 15:
            shortages.append(f"{item_key} (Need {deficit} more units)")
        elif deficit < -10:
            surpluses.append(f"{item_key} (Overstocked by {-deficit} units)")

    # Check if the NEW donation helps any shortages
    helped_items = []
    for item in new_items:
        for shortage in shortages:
            if item.split()[0].lower() in shortage.split()[0].lower(): # Simple string match for demo
                helped_items.append(item)

    analysis_result = {
        "shortages_flagged": shortages if shortages else ["None. Inventory is healthy."],
        "surpluses_flagged": surpluses if surpluses else ["None."],
        "donation_impact": f"This donation helps alleviate shortages in: {helped_items}" if helped_items else "This donation adds to general surplus.",
        "capacity_check": "✅ Volunteer capacity is sufficient for current intake volume."
    }

    log_agent_action(logistics_logger, "inventory_analysis", analysis_result)
    
    return analysis_result

def evaluate_surplus_pickup(donation_details: dict) -> dict:
    """
    Evaluates if a large, time-sensitive surplus donation (e.g., from a grocery store)
    can be picked up before it spoils.
    """
    print(f"🚚 Logistics Agent evaluating surplus pickup feasibility...")
    
    # Mock logic: 80% chance we have capacity, 20% chance we are overwhelmed
    has_capacity = random.random() > 0.2 
    
    if has_capacity:
        result = {
            "pickup_feasible": True,
            "recommended_volunteers": 2,
            "estimated_time": "45 minutes",
            "spoilage_risk": "Low"
        }
    else:
        result = {
            "pickup_feasible": False,
            "reason": "All volunteers are currently deployed. Escalating to human coordinator.",
            "spoilage_risk": "High"
        }
        
    log_agent_action(logistics_logger, "pickup_evaluation", result)
    return result