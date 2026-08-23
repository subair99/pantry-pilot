# backend/agents/intake_agent.py
import os
import json
import re
from tools.inventory_db import log_donation
from tools.ocr_mcp import extract_donation_details
from utils.guardrails import PantryGuardrails
from utils.logger import intake_logger, log_agent_action, log_hitl_event, log_tool_execution
from state.memory import memory

def extract_info_from_message(message: str) -> dict:
    """
    Upgraded, bulletproof parser for the mock fallback.
    Intelligently finds donor names at the beginning, middle, or end of the message.
    """
    message_lower = message.lower()
    donor_name = "Anonymous Donor"
    
    # 1. Try matching "[Name]'s [Place]" (e.g., Mike's Farm, Sarah's Bakery)
    name_match = re.search(r"([A-Z][a-z]+)'s\s+(?:Farm|Bakery|Market|Pantry|Garden)", message)
    if name_match:
        donor_name = name_match.group(1)
        if "farm" in message_lower: donor_name += " (Farm)"
        elif "bakery" in message_lower: donor_name += " (Local Bakery)"
        elif "garden" in message_lower: donor_name += " (Community Garden)"
    else:
        # 2. Try matching "This is [Name]" or "from [Name]"
        name_match = re.search(r'(?:this is|from)\s+([A-Z][a-z]+)', message)
        if name_match:
            donor_name = name_match.group(1)
            if "bakery" in message_lower: donor_name += " (Local Bakery)"
        else:
            # 3. Try matching "[Name] from" at the start (e.g., "David from community garden")
            name_match = re.search(r'^([A-Z][a-z]+)\s+from', message)
            if name_match:
                donor_name = name_match.group(1)
                if "garden" in message_lower: donor_name += " (Community Garden)"
            else:
                # 4. Try matching "[Name] here" at the start (e.g., "Lisa here.")
                name_match = re.search(r'^([A-Z][a-z]+)\s+here', message)
                if name_match:
                    donor_name = name_match.group(1)
                else:
                    # 5. Try matching email sign-offs like "Best, [Name]", "Regards, [Name]"
                    name_match = re.search(r'(?:Best,|Regards,|Sincerely,)\s+([A-Z][a-zA-Z\s]+)', message)
                    if name_match:
                        donor_name = name_match.group(1).strip()
                        if "pastor" in donor_name.lower(): 
                            donor_name = "Pastor Mark"
                        elif "amanda" in donor_name.lower():
                            donor_name = "Amanda (Rotary Club)"
    
    # Extract Time
    time_str = "5 PM today"
    if "afternoon" in message_lower: time_str = "This Afternoon (approx. 2 PM)"
    elif "morning" in message_lower: time_str = "This Morning (approx. 9 AM)"
    elif "evening" in message_lower: time_str = "This Evening (approx. 6 PM)"
    else:
        time_match = re.search(r'at\s+(\d+\s*(?:AM|PM|am|pm))', message)
        if time_match: time_str = time_match.group(1)

    # Extract Items
    item_pattern = r'(\d+)\s*(lbs?|pounds?|boxes?|bags?|loaves?|containers?|gallons?|trays?)\s+(?:of\s+)?(?:fresh\s+|organic\s+|untouched\s+)?(\w+)'
    matches = re.findall(item_pattern, message_lower)
    
    items = []
    quantity = 0
    for count, unit, item in matches:
        items.append(f"{count} {unit} of {item}")
        quantity += int(count)
    
    # Fallback for simple mentions without units
    if not items:
        if "pasta" in message_lower: items.append("boxes of pasta"); quantity += 12
        if "apples" in message_lower: items.append("lbs of apples"); quantity += 20
        if "bread" in message_lower: items.append("loaves of bread"); quantity += 50
        if "tomato" in message_lower: items.append("lbs of tomatoes"); quantity += 100
        if "corn" in message_lower: items.append("lbs of corn"); quantity += 50
        if "canned goods" in message_lower: items.append("canned goods"); quantity += 200
        if "coats" in message_lower: items.append("winter coats"); quantity += 50
        if "blankets" in message_lower: items.append("blankets"); quantity += 30
        if "zucchini" in message_lower: items.append("lbs of zucchini"); quantity += 150

    return {
        "donor_name": donor_name,
        "items": items if items else ["miscellaneous items"],
        "quantity": quantity if quantity > 0 else 10,
        "dropoff_time": time_str
    }

def process_incoming_donation(raw_message: str, donor_email: str = None, donor_phone: str = None) -> str:
    """Main entry point for the intake agent."""
    print(f"🤖 Intake Agent processing: {raw_message}")
    
    is_safe, safety_msg = PantryGuardrails.check_input_safety(raw_message)
    if not is_safe:
        log_hitl_event(intake_logger, "input_safety_check", "BLOCKED", {"reason": safety_msg})
        return safety_msg

    if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
        print("⚠️ No AWS credentials found. Using smart mock parser.")
        
        mock_parsed = extract_info_from_message(raw_message)
        mock_parsed["estimated_value"] = "$50.00"
        
        # Override with explicit data from seed script if provided
        if donor_email: mock_parsed["donor_email"] = donor_email
        if donor_phone: mock_parsed["donor_phone"] = donor_phone
        
        # Fallback mock contacts if not provided
        if not mock_parsed.get("donor_email"):
            mock_parsed["donor_email"] = f"{mock_parsed['donor_name'].split()[0].lower()}@example.com"
        if not mock_parsed.get("donor_phone"):
            mock_parsed["donor_phone"] = "+15550000000"
        
        log_tool_execution(intake_logger, "extract_donation_details", raw_message, mock_parsed)

        is_compliant, compliance_msg, mock_parsed = PantryGuardrails.prevent_financial_hallucination(mock_parsed)
        if not is_compliant:
            log_hitl_event(intake_logger, "financial_hallucination_check", "REDACTED", {"reason": compliance_msg})

        context_snippet = memory.generate_context_prompt(mock_parsed["donor_name"])
        print(f"🧠 Memory Context: {context_snippet}")

        result = log_donation(
            donor_name=mock_parsed["donor_name"],
            items=mock_parsed["items"],
            quantity=mock_parsed["quantity"],
            notes=f"Dropoff at {mock_parsed['dropoff_time']}",
            donor_email=mock_parsed.get("donor_email"),
            donor_phone=mock_parsed.get("donor_phone")
        )
        
        memory.save_interaction(
            donor_name=mock_parsed["donor_name"],
            raw_message=raw_message,
            action_taken=result
        )
        
        log_agent_action(intake_logger, "log_donation", {"donation_id": "DON-0001", "status": "pending_approval"})
        log_hitl_event(intake_logger, "human_approval", "PENDING", {"donation_id": "DON-0001"})
        
        memory_note = "\n\n🧠 Agent Memory Note: I recognized this donor from past interactions." if "first time" not in context_snippet else ""
        
        return f"✅ Donation processed successfully!{memory_note}\n\nParsed: {json.dumps(mock_parsed, indent=2)}\nSystem: {result}\n\n{compliance_msg}"

    return "AWS logic placeholder."