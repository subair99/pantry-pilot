# backend/tools/twilio_mcp.py
import os
import logging
from typing import Dict, Any

# Lazy import twilio to prevent crashes if the package is missing during initial setup
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

from utils.logger import dispatch_logger, log_tool_execution

def send_volunteer_sms(to_phone: str, message: str) -> Dict[str, Any]:
    """
    Sends an SMS message to a volunteer via Twilio.
    """
    dispatch_logger.info(f"Attempting to send SMS to {to_phone}")
    
    # 🛡️ HACKATHON DEMO SAFETY NET
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")
    
    if not TWILIO_AVAILABLE or not all([account_sid, auth_token, from_phone]):
        dispatch_logger.warning("Twilio credentials missing. Using mock SMS response for demo.")
        
        mock_response = {
            "status": "success",
            "sid": "MOCK-SM" + "".join([str(i) for i in range(10)]),
            "to": to_phone,
            "from": from_phone or "+15550000000",
            "message_preview": message,
            "note": "Mocked for demo reliability. Add TWILIO_* env vars to send real SMS."
        }
        
        log_tool_execution(dispatch_logger, "send_volunteer_sms", {"to": to_phone}, mock_response)
        return mock_response

    # 🚀 REAL TWILIO EXECUTION
    try:
        client = Client(account_sid, auth_token)
        message_obj = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        
        success_response = {
            "status": "success",
            "sid": message_obj.sid,
            "to": to_phone,
            "from": from_phone,
            "message_preview": message
        }
        
        log_tool_execution(dispatch_logger, "send_volunteer_sms", {"to": to_phone}, success_response)
        return success_response
        
    except Exception as e:
        error_response = {
            "status": "error",
            "error_message": str(e),
            "to": to_phone
        }
        dispatch_logger.error(f"Failed to send SMS: {e}")
        log_tool_execution(dispatch_logger, "send_volunteer_sms", {"to": to_phone}, error_response)
        return error_response


def send_donor_engagement_sms(to_phone: str, donor_name: str) -> Dict[str, Any]:
    """
    Proactively asks an SMS donor if they want an IRS tax receipt.
    """
    dispatch_logger.info(f"Attempting to send engagement SMS to donor {to_phone}")
    
    # 🛡️ HACKATHON DEMO SAFETY NET
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")
    
    message = (
        f"Hi {donor_name}! Thanks for your generous donation to PantryPilot. "
        f"Would you like an IRS-compliant tax receipt for your records? "
        f"Simply reply to this message with your email address, and we'll send it right over! "
        f"- PantryPilot Team"
    )
    
    if not TWILIO_AVAILABLE or not all([account_sid, auth_token, from_phone]):
        dispatch_logger.warning("Twilio credentials missing. Using mock engagement SMS.")
        mock_response = {
            "status": "success",
            "sid": "MOCK-SMS-ENGAGE-123",
            "to": to_phone,
            "message": message,
            "note": "Mocked for demo reliability."
        }
        log_tool_execution(dispatch_logger, "send_donor_engagement_sms", {"to": to_phone}, mock_response)
        return mock_response

    # 🚀 REAL TWILIO EXECUTION (Production Ready)
    try:
        client = Client(account_sid, auth_token)
        message_obj = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        success_response = {
            "status": "success",
            "sid": message_obj.sid,
            "to": to_phone,
            "message": message
        }
        log_tool_execution(dispatch_logger, "send_donor_engagement_sms", {"to": to_phone}, success_response)
        return success_response
        
    except Exception as e:
        error_response = {
            "status": "error",
            "error_message": str(e),
            "to": to_phone
        }
        dispatch_logger.error(f"Failed to send engagement SMS: {e}")
        log_tool_execution(dispatch_logger, "send_donor_engagement_sms", {"to": to_phone}, error_response)
        return error_response