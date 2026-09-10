# FORCE DEPLOY UPDATE
import os
import json
import boto3
from datetime import datetime
from fpdf import FPDF

# Initialize AWS Clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
s3 = boto3.client('s3')

MODEL_ID = os.environ.get('AGENT_MODEL_ID', 'amazon.nova-pro-v1:0')
BUCKET_NAME = os.environ.get('RECEIPTS_BUCKET_NAME')

def generate_receipt_pdf(donation_id: str, donor_name: str, items: list, quantity: int) -> str:
    """Tool: Generates an IRS-compliant PDF and uploads to S3."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "PantryPilot Official Tax Receipt", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Donation ID: {donation_id}", ln=True)
    pdf.cell(0, 8, f"Donor: {donor_name}", ln=True)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, f"Items: {', '.join(items)}", ln=True)
    pdf.cell(0, 8, f"Total Quantity: {quantity}", ln=True)
    
    local_path = f"/tmp/receipt_{donation_id}.pdf"
    pdf.output(local_path)
    
    s3_key = f"receipts/{donation_id}.pdf"
    s3.upload_file(local_path, BUCKET_NAME, s3_key)
    return f"Receipt successfully generated and saved to s3://{BUCKET_NAME}/{s3_key}"

def send_volunteer_sms(volunteer_phone: str, message: str) -> str:
    """Tool: Sends an SMS to a volunteer (Mocked for demo)."""
    return f"SMS successfully dispatched to {volunteer_phone}: '{message}'"

# Define the tools for Nova Pro's Converse API
TOOLS = [
    {
        "toolSpec": {
            "name": "generate_receipt",
            "description": "Generates a PDF tax receipt for an approved donation and saves it to S3.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "donation_id": {"type": "string"},
                        "donor_name": {"type": "string"},
                        "items": {"type": "array", "items": {"type": "string"}},
                        "quantity": {"type": "integer"}
                    },
                    "required": ["donation_id", "donor_name", "items", "quantity"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "send_volunteer_sms",
            "description": "Sends an SMS notification to a volunteer about a drop-off.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "volunteer_phone": {"type": "string"},
                        "message": {"type": "string"}
                    },
                    "required": ["volunteer_phone", "message"]
                }
            }
        }
    }
]

SYSTEM_PROMPT = """You are PantryPilot, an autonomous co-pilot for food banks. 
Embrace a 'quiet until it matters' UX. Silently process data in the background. 
ONLY use tools when explicitly instructed by the user or when a critical approval is needed.
If a user asks to approve a donation, use the generate_receipt tool immediately."""

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', 'Hello')
        
        # 1. Call Nova Pro via Converse API
        response = bedrock.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": user_message}]}],
            system=[{"text": SYSTEM_PROMPT}],
            toolConfig={"tools": TOOLS}
        )
        
        stop_reason = response.get('stopReason')
        output_message = response.get('output', {}).get('message', {})
        
        if stop_reason == 'tool_use':
            tool_requests = output_message.get('content', [])
            tool_results = []
            
            for tool_req in tool_requests:
                if 'toolUse' in tool_req:
                    tool_name = tool_req['toolUse']['name']
                    tool_input = tool_req['toolUse']['input']
                    
                    if tool_name == 'generate_receipt':
                        result = generate_receipt_pdf(**tool_input)
                    elif tool_name == 'send_volunteer_sms':
                        result = send_volunteer_sms(**tool_input)
                    else:
                        result = "Unknown tool"
                        
                    tool_results.append({
                        "toolResult": {
                            "toolUseId": tool_req['toolUse']['toolUseId'],
                            "content": [{"text": result}]
                        }
                    })
            
            # 3. Send tool results back to Nova Pro for final response
            final_response = bedrock.converse(
                modelId=MODEL_ID,
                messages=[
                    {"role": "user", "content": [{"text": user_message}]},
                    output_message,
                    {"role": "user", "content": tool_results}
                ],
                system=[{"text": SYSTEM_PROMPT}],
                toolConfig={"tools": TOOLS}
            )
            final_text = final_response['output']['message']['content'][0]['text']
        else:
            final_text = output_message['content'][0]['text']

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"reply": final_text})
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }