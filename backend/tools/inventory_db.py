# backend/tools/inventory_db.py
import uuid
from datetime import datetime

# In-memory "database" for the hackathon demo
DONATIONS_DB = []

def log_donation(donor_name: str, items: list, quantity: int, notes: str, donor_email: str = None, donor_phone: str = None, source: str = "SMS") -> str:
    """Logs a new donation to the in-memory database."""
    donation_id = f"DON-{str(uuid.uuid4())[:4].upper()}"
    
    DONATIONS_DB.append({
        "id": donation_id,
        "donor": donor_name,
        "items": items,
        "quantity": quantity,
        "notes": notes,
        "donor_email": donor_email,
        "donor_phone": donor_phone,
        "source": source,
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M") # Added timestamp
    })
    return f"Successfully logged donation {donation_id}"

def get_donation(donation_id: str):
    """Fetches a specific donation by ID, regardless of status."""
    for d in DONATIONS_DB:
        if d["id"] == donation_id:
            return d
    return None

def get_pending_donations():
    """Fetches all donations that are still pending approval."""
    return [d for d in DONATIONS_DB if d["status"] == "pending"]

def approve_donation(donation_id: str):
    """Marks a donation as approved."""
    for d in DONATIONS_DB:
        if d["id"] == donation_id:
            d["status"] = "approved"
            return f"Donation {donation_id} approved and logged."
    return "Donation not found."

def get_approved_donations():
    """
    Fetches approved donations directly from the in-memory database.
    Maps internal keys to the keys expected by the frontend.
    """
    approved = []
    for d in DONATIONS_DB:
        if d["status"] == "approved":
            approved.append({
                "id": d["id"],
                "donor_name": d["donor"],  # Map 'donor' to 'donor_name' for the UI
                "donor_email": d.get("donor_email") or "N/A",
                "donor_phone": d.get("donor_phone") or "N/A",
                "date": d.get("created_at", "Unknown")
            })
            
    # Return newest first
    return list(reversed(approved))