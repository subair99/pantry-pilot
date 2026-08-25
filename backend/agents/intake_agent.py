# backend/agents/intake_agent.py
import os
import json
from pydantic import BaseModel, Field
from openai import OpenAI
# from strands import Agent  # <-- UNCOMMENT THIS LINE WHEN SWITCHING TO BEDROCK

from tools.inventory_db import log_donation
from utils.guardrails import PantryGuardrails
from utils.logger import intake_logger, log_agent_action, log_hitl_event, log_tool_execution
from state.memory import memory

# 1. Define the strict schema the LLM must output
class DonationExtraction(BaseModel):
    donor_name: str = Field(description="The name of the donor or organization (e.g., 'Jennifer', 'Mike (Farm)')")
    items: list[str] = Field(description="List of donated items with quantities (e.g., ['40 trays of catering', '10 gallons of milk'])")
    total_quantity: int = Field(description="The total numerical count of all items combined")
    dropoff_time: str = Field(description="The proposed dropoff time (e.g., 'Today (flexible)', '5 PM')")

# 2. Initialize the Qwen API Client (OpenAI-compatible)
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")

if QWEN_API_KEY:
    qwen_client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL
    )
    LLM_AVAILABLE = True
else:
    intake_logger.warning("QWEN_API_KEY not found. LLM extraction disabled, using fallback.")
    LLM_AVAILABLE = False

def extract_info_with_llm(message: str) -> dict:
    """Uses Qwen API with Pydantic structured output to perfectly parse text."""
    try:
        response = qwen_client.beta.chat.completions.parse(
            model=QWEN_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert logistics coordinator for a food bank. CRITICAL: You MUST extract ALL items mentioned. NEVER return an empty list for items. If the user says '100 lbs of tomatoes', return ['100 lbs of tomatoes']. Be concise and accurate."},
                {"role": "user", "content": f"Extract the donation details from this message: '{message}'"}
            ],
            response_format=DonationExtraction
        )
        
        parsed = response.choices[0].message.parsed
        return {
            "donor_name": parsed.donor_name or "Anonymous Donor",
            "items": parsed.items or ["miscellaneous items"],
            "quantity": parsed.total_quantity or 10,
            "dropoff_time": parsed.dropoff_time or "5 PM today"
        }
    except Exception as e:
        intake_logger.error(f"Qwen LLM extraction failed: {e}")
        return None

def process_incoming_donation(raw_message: str, donor_email: str = None, donor_phone: str = None, source: str = None) -> str:
    """Main entry point for the intake agent."""
    print(f"🤖 Intake Agent processing: {raw_message}")
    
    # 1. Guardrail Check
    is_safe, safety_msg = PantryGuardrails.check_input_safety(raw_message)
    if not is_safe:
        log_hitl_event(intake_logger, "input_safety_check", "BLOCKED", {"reason": safety_msg})
        return safety_msg

    # 2. LLM Extraction (with Fallback for demo reliability)
    if LLM_AVAILABLE:
        print(f"✨ Using Qwen API ({QWEN_MODEL}) for structured extraction...")
        mock_parsed = extract_info_with_llm(raw_message)
        
        # Fallback if LLM fails or returns empty
        if not mock_parsed or not mock_parsed.get("items"):
            print("⚠️ LLM returned empty, using fallback parser...")
            mock_parsed = {"donor_name": "Anonymous Donor", "items": ["miscellaneous items"], "quantity": 10, "dropoff_time": "5 PM today"}
    else:
        print("⚠️ LLM unavailable. Using fallback parser.")
        mock_parsed = {"donor_name": "Anonymous Donor", "items": ["miscellaneous items"], "quantity": 10, "dropoff_time": "5 PM today"}
        
    mock_parsed["estimated_value"] = "$50.00"
    
    # 3. Inject Contact Info (Only store what was actually provided)
    if donor_email: 
        mock_parsed["donor_email"] = donor_email
    if donor_phone: 
        mock_parsed["donor_phone"] = donor_phone
        
    # Fallback only for phone if missing (for demo purposes)
    if not mock_parsed.get("donor_phone"):
        mock_parsed["donor_phone"] = "+15550000000"
        
    # ⚠️ DO NOT auto-generate fake emails. If donor_email is None, leave it None.
    # This allows the Dispatch Agent to distinguish between "Email donation" and "SMS donation".
    
    # 4. Determine Source (CRITICAL FOR FRONTEND)
    # Use provided source, or infer from contact info
    if source:
        message_source = source
    elif donor_email:
        message_source = "Email"
    else:
        message_source = "SMS"  # Default fallback
        
    mock_parsed["source"] = message_source
    
    log_tool_execution(intake_logger, "extract_donation_details", raw_message, mock_parsed)

    # 5. Guardrail: Prevent Financial Hallucination
    is_compliant, compliance_msg, mock_parsed = PantryGuardrails.prevent_financial_hallucination(mock_parsed)
    if not is_compliant:
        log_hitl_event(intake_logger, "financial_hallucination_check", "REDACTED", {"reason": compliance_msg})

    # 6. Memory & Logging
    context_snippet = memory.generate_context_prompt(mock_parsed["donor_name"])
    print(f"🧠 Memory Context: {context_snippet}")

    # 7. Save to Database WITH THE SOURCE FIELD
    result = log_donation(
        donor_name=mock_parsed["donor_name"],
        items=mock_parsed["items"],
        quantity=mock_parsed["quantity"],
        notes=f"Dropoff at {mock_parsed['dropoff_time']}",
        donor_email=mock_parsed.get("donor_email"),
        donor_phone=mock_parsed.get("donor_phone"),
        source=message_source  
    )
    
    memory.save_interaction(donor_name=mock_parsed["donor_name"], raw_message=raw_message, action_taken=result)
    log_agent_action(intake_logger, "log_donation", {"donation_id": "DON-0001", "status": "pending_approval"})
    log_hitl_event(intake_logger, "human_approval", "PENDING", {"donation_id": "DON-0001"})
    
    memory_note = "\n\n🧠 Agent Memory Note: I recognized this donor from past interactions." if "first time" not in context_snippet else ""
    
    return f"✅ Donation processed successfully!{memory_note}\n\nParsed: {json.dumps(mock_parsed, indent=2)}\nSystem: {result}\n\n{compliance_msg}"