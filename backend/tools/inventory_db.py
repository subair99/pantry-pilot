# backend/tools/inventory_db.py
import uuid

# In-memory "database" for the hackathon demo
DONATIONS_DB = []

def log_donation(donor_name: str, items: list, quantity: int, notes: str, donor_email: str = None, donor_phone: str = None) -> str:
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
        "status": "pending"
    })
    return f"Successfully logged donation {donation_id}"

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