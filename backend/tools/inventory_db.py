# backend/tools/inventory_db.py
from typing import List, Dict, Any

# In-memory "database" for hackathon speed
inventory_db: List[Dict[str, Any]] = []

def log_donation(donor_name: str, items: List[str], quantity: int, notes: str = "") -> str:
    """Logs a new donation into the pantry inventory system."""
    donation_id = f"DON-{len(inventory_db) + 1:04d}"
    record = {
        "id": donation_id,
        "donor": donor_name,
        "items": items,
        "quantity": quantity,
        "notes": notes,
        "status": "pending_approval"
    }
    inventory_db.append(record)
    return f"Successfully logged donation {donation_id}. Awaiting human approval."

def get_pending_donations() -> List[Dict[str, Any]]:
    """Retrieves all donations awaiting human approval."""
    return [item for item in inventory_db if item["status"] == "pending_approval"]

def approve_donation(donation_id: str) -> str:
    """Approves a pending donation, making it active inventory."""
    for item in inventory_db:
        if item["id"] == donation_id:
            item["status"] = "approved"
            return f"Donation {donation_id} approved and added to active inventory."
    return f"Donation {donation_id} not found."