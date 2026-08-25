# backend/agents/dispatch_agent.py
import os
from tools.twilio_mcp import send_volunteer_sms, send_donor_engagement_sms
from tools.email_mcp import send_donor_receipt
from utils.logger import dispatch_logger, log_tool_execution

# Mock Volunteer Database (Simulates a real DB query for the demo)
VOLUNTEER_DB = [
    {"name": "Elena Gilbert", "phone": "+15550103", "preferred_times": ["morning", "evening"]},
    {"name": "Sarah Jenkins", "phone": "+15550101", "preferred_times": ["afternoon", "evening"]},
    {"name": "Mike Ross", "phone": "+15550102", "preferred_times": ["morning", "afternoon"]},
]

def get_best_volunteer(dropoff_time: str) -> dict:
    """
    Simulates querying a volunteer database to find the best match 
    based on dropoff time. Ensures deterministic, realistic routing for the demo.
    """
    time_lower = dropoff_time.lower()
    
    # Simple matching logic for the demo
    if "morning" in time_lower or "8 am" in time_lower or "9 am" in time_lower:
        return VOLUNTEER_DB[0] # Elena (Morning)
    elif "afternoon" in time_lower or "2 pm" in time_lower or "5 pm" in time_lower:
        return VOLUNTEER_DB[2] # Mike (Afternoon)
    elif "evening" in time_lower or "6 pm" in time_lower:
        return VOLUNTEER_DB[1] # Sarah (Evening)
    
    # Fallback for unmatched times
    return VOLUNTEER_DB[0]

def dispatch_volunteer(donation_id: str, dropoff_time: str, items: list, quantity: int, donor_name: str, donor_email: str = None, donor_phone: str = None) -> dict:
    """
    Dispatch Agent: Routes volunteer SMS based on availability, sends 
    donor tax receipts if an email was provided, and proactively asks 
    SMS donors for their email if missing.
    """
    dispatch_logger.info(f"Dispatch Agent triggered for {donation_id}")
    
    # 1. Query the "database" for the best available volunteer
    volunteer = get_best_volunteer(dropoff_time)
    
    # 2. Draft the SMS message to the volunteer
    item_summary = ", ".join(items)
    drafted_sms = (
        f"Hi {volunteer['name']}! PantryPilot here. We have a donation of {item_summary} "
        f"dropping off at {dropoff_time}. Can you cover the intake shift? Reply YES to confirm."
    )
    
    # 3. Execute the SMS MCP Tool (Always send to volunteer to coordinate pickup)
    sms_result = send_volunteer_sms(to_phone=volunteer["phone"], message=drafted_sms)
    
    # 4. Execute the Email MCP Tool (ONLY if the donor provided a REAL email address)
    email_result = {"status": "skipped", "reason": "No donor email provided (SMS donation)"}
    if donor_email and donor_email != f"{donor_name.split()[0].lower()}@example.com":
        # Only send if email was explicitly provided, not auto-generated
        email_result = send_donor_receipt(
            to_email=donor_email,
            donor_name=donor_name,
            items=items,
            quantity=quantity
        )

    # 5. 🌟 NEW: Proactive Donor Engagement (ONLY if SMS donation with NO email)
    donor_engagement_sms = None
    if not donor_email and donor_phone:
        donor_engagement_sms = send_donor_engagement_sms(to_phone=donor_phone, donor_name=donor_name)
    
    return {
        "volunteer_name": volunteer["name"],
        "volunteer_phone": volunteer["phone"],
        "drafted_sms": drafted_sms,
        "sms_response": sms_result,
        "donor_email": donor_email,
        "email_subject": email_result.get("subject", "N/A"),
        "email_body_preview": email_result.get("body_preview", "Skipped"),
        "email_response": email_result,
        "donor_engagement_sms": donor_engagement_sms, 
        "status": "sent"
    }