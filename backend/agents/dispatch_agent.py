# backend/agents/dispatch_agent.py
import os
import random

# Mock volunteer database for the demo
VOLUNTEERS = [
    {"name": "Sarah Jenkins", "phone": "+1-555-0101", "availability": "Evenings"},
    {"name": "Mike Ross", "phone": "+1-555-0102", "availability": "Weekends"},
    {"name": "Elena Gilbert", "phone": "+1-555-0103", "availability": "Mornings"},
]

def dispatch_volunteer(donation_id: str, dropoff_time: str, items: list) -> dict:
    """
    Dispatch Agent: Selects the best available volunteer and drafts an SMS.
    (Mocked for demo reliability; swap with Twilio API in production).
    """
    print(f" Dispatch Agent triggered for {donation_id}")
    
    # Simulate agent logic: pick a random available volunteer
    volunteer = random.choice(VOLUNTEERS)
    
    # Draft the SMS message
    item_summary = ", ".join(items)
    drafted_sms = (
        f"Hi {volunteer['name']}! PantryPilot here. We have a donation of {item_summary} "
        f"dropping off at {dropoff_time}. Can you cover the intake shift? Reply YES to confirm."
    )
    
    return {
        "volunteer_name": volunteer["name"],
        "volunteer_phone": volunteer["phone"],
        "drafted_sms": drafted_sms,
        "status": "sent_to_approval_queue" # In a real app, this would go to another HITL gate
    }