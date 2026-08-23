# backend/tools/email_mcp.py
import os
import logging
from typing import Dict, Any
from utils.logger import dispatch_logger, log_tool_execution

def send_donor_receipt(to_email: str, donor_name: str, items: list, quantity: int) -> Dict[str, Any]:
    """
    Sends a formal tax receipt email to the donor.
    """
    dispatch_logger.info(f"Attempting to send receipt email to {to_email}")
    
    # 🛡️ HACKATHON DEMO SAFETY NET
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    
    if not all([smtp_host, smtp_user, smtp_pass]):
        dispatch_logger.warning("Email credentials missing. Using mock email response for demo.")
        
        subject = f"Thank You for Your Donation to PantryPilot, {donor_name}!"
        body = (
            f"Dear {donor_name},\n\n"
            f"Thank you for your generous donation of {quantity} units, including: {', '.join(items)}.\n\n"
            f"Your contribution makes a direct impact on our community. "
            f"Please note: PantryPilot is a registered 501(c)(3) organization. "
            f"No goods or services were provided in exchange for this contribution.\n\n"
            f"Keep this email for your tax records.\n\n"
            f"With gratitude,\nThe PantryPilot Team"
        )
        
        mock_response = {
            "status": "success",
            "message_id": "MOCK-EMAIL-" + "".join([str(i) for i in range(8)]),
            "to": to_email,
            "subject": subject,
            "body_preview": body[:100] + "...",
            "note": "Mocked for demo reliability. Add SMTP_* env vars to send real emails."
        }
        
        log_tool_execution(dispatch_logger, "send_donor_receipt", {"to": to_email}, mock_response)
        return mock_response

    # 🚀 REAL SMTP EXECUTION (Production Ready)
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        subject = f"Thank You for Your Donation to PantryPilot, {donor_name}!"
        body = (
            f"Dear {donor_name},\n\n"
            f"Thank you for your generous donation of {quantity} units, including: {', '.join(items)}.\n\n"
            f"Your contribution makes a direct impact on our community. "
            f"Please note: PantryPilot is a registered 501(c)(3) organization. "
            f"No goods or services were provided in exchange for this contribution.\n\n"
            f"Keep this email for your tax records.\n\n"
            f"With gratitude,\nThe PantryPilot Team"
        )

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_host, 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            
        success_response = {
            "status": "success",
            "message_id": "SENT-VIA-SMTP",
            "to": to_email,
            "subject": subject,
            "body_preview": body[:100] + "..."
        }
        
        log_tool_execution(dispatch_logger, "send_donor_receipt", {"to": to_email}, success_response)
        return success_response
        
    except Exception as e:
        error_response = {
            "status": "error",
            "error_message": str(e),
            "to": to_email
        }
        dispatch_logger.error(f"Failed to send email: {e}")
        log_tool_execution(dispatch_logger, "send_donor_receipt", {"to": to_email}, error_response)
        return error_response