# infrastructure/lambdas/send_sms/handler.py
import json

def lambda_handler(event, context):
    arguments = event.get('arguments', {})
    volunteer_phone = arguments.get('volunteer_phone', 'Unknown')
    dropoff_details = arguments.get('dropoff_details', 'No details provided')

    # In a real app, you would use boto3 to call SNS or the Twilio API here.
    # For this demo, we return a successful mock response.
    
    return {
        "status": "success",
        "message_id": f"mock-sms-{volunteer_phone[-4:]}",
        "message": f"Mock SMS sent to {volunteer_phone}: {dropoff_details}"
    }