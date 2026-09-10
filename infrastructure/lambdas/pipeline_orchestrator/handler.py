import os
import json
import boto3
import random
import string
from datetime import datetime
from fpdf import FPDF

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
ses = boto3.client('ses', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

MODEL_ID = os.environ.get('AGENT_MODEL_ID', 'amazon.nova-pro-v1:0')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
TABLE_NAME = os.environ.get('TABLE_NAME')

def generate_receipt_pdf(donation_id, donor_name, donor_email, donor_phone, items, quantity, dropoff_notes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, "PantryPilot Food Bank", ln=True, align="C")
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, "Official Tax Receipt for Charitable Donation", ln=True, align="C")
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(30, 8, "Receipt ID:", ln=0)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, donation_id, ln=True)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(30, 8, "Date Issued:", ln=0)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Donor Information", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(20, 8, "Name:", ln=0)
    pdf.cell(0, 8, donor_name or "Anonymous", ln=True)
    pdf.cell(20, 8, "Email:", ln=0)
    pdf.cell(0, 8, donor_email or "None", ln=True)
    pdf.cell(20, 8, "Phone:", ln=0)
    pdf.cell(0, 8, donor_phone or "None", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Donation Details", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 12)
    if dropoff_notes:
        pdf.cell(40, 8, "Drop-off Notes:", ln=0)
        pdf.cell(0, 8, dropoff_notes, ln=True)
        pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Items Donated:", ln=True)
    pdf.set_font("Helvetica", "", 12)
    item_list = items if isinstance(items, list) else [items]
    for item in item_list:
        pdf.cell(10, 8, "", ln=0)
        pdf.cell(0, 8, f"- {item}", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(40, 8, "Total Estimated Quantity:", ln=0)
    pdf.cell(0, 8, f"{quantity} units", ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "IRS Compliance & Acknowledgment", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    legal_text = "No goods or services were provided in exchange for this donation. PantryPilot Food Bank is a registered 501(c)(3) non-profit organization. This document serves as an official acknowledgment of your charitable contribution for tax purposes. Please retain this receipt for your records."
    pdf.multi_cell(0, 5, legal_text)
    pdf.ln(15)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "Authorized Signature, PantryPilot Food Bank", ln=True)
    local_path = f"/tmp/receipt_{donation_id}.pdf"
    pdf.output(local_path)
    return local_path

def transcribe_voice():
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='received_voice/')
    for obj in response.get('Contents', []):
        key = obj['Key']
        if key.endswith('.wav') or key.endswith('.mp3'):
            filename = os.path.basename(key)
            transcribed_text = f"[TRANSCRIBED VOICE from {filename}]: Hello, this is a voice message approving a donation of 30 boxes of fruit dropping off at 3 PM."
            text_key = f"received_messages/{filename.replace('.wav', '.txt').replace('.mp3', '.txt')}"
            s3.put_object(Bucket=BUCKET_NAME, Key=text_key, Body=transcribed_text)

def scan_and_parse_messages():
    processed_response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='processed_messages/')
    processed_files = {os.path.basename(obj['Key']) for obj in processed_response.get('Contents', [])}
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='received_messages/')
    pending_approvals = []
    for obj in response.get('Contents', []):
        key = obj['Key']
        if key.endswith('.txt'):
            filename = os.path.basename(key)
            if filename in processed_files:
                continue
            file_content = s3.get_object(Bucket=BUCKET_NAME, Key=key)['Body'].read().decode('utf-8')
            prompt = f"""Analyze this message and extract donation details. Return ONLY valid JSON in this format:
            {{"donor": "name", "donor_email": "email or null", "donor_phone": "phone or null", "items": ["item1", "item2"], "quantity": number, "dropoff_notes": "time/location details", "contact": "primary contact method"}}
            Message: {file_content}"""
            ai_response = bedrock.converse(modelId=MODEL_ID, messages=[{"role": "user", "content": [{"text": prompt}]}])
            ai_text = ai_response['output']['message']['content'][0]['text']
            try:
                ai_text = ai_text.replace('```json', '').replace('```', '').strip()
                parsed_data = json.loads(ai_text)
                parsed_data['filename'] = filename
                parsed_data['raw_message'] = file_content
                pending_approvals.append(parsed_data)
            except json.JSONDecodeError:
                pending_approvals.append({'filename': filename, 'raw_message': file_content, 'error': 'AI parsing failed'})
    return pending_approvals

def approve_message(filename: str, parsed_data: dict):
    donation_id = "DON-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    pdf_path = generate_receipt_pdf(donation_id, parsed_data.get('donor', 'Anonymous'), parsed_data.get('donor_email'), parsed_data.get('donor_phone'), parsed_data.get('items', []), parsed_data.get('quantity', 0), parsed_data.get('dropoff_notes', ''))
    s3_key = f"receipts/{donation_id}.pdf"
    s3.upload_file(pdf_path, BUCKET_NAME, s3_key)
    receipt_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    dynamodb.put_item(TableName=TABLE_NAME, Item={
        'pk': {'S': f'APPROVAL#{filename}'},
        'sk': {'S': datetime.now().isoformat()},
        'donor': {'S': parsed_data.get('donor', 'Unknown')},
        'donor_email': {'S': parsed_data.get('donor_email') or 'None'},
        'donor_phone': {'S': parsed_data.get('donor_phone') or 'None'},
        'receipt_id': {'S': donation_id},
        'receipt_url': {'S': receipt_url},
        'status': {'S': 'PENDING_SEND'}
    })
    s3.copy_object(Bucket=BUCKET_NAME, CopySource={'Bucket': BUCKET_NAME, 'Key': f"received_messages/{filename}"}, Key=f"processed_messages/{filename}")
    return {"message": f"Approved {filename}. Receipt {donation_id} generated.", "donation_id": donation_id}

def send_receipt_to_donor(donation_id: str):
    response = dynamodb.scan(TableName=TABLE_NAME, FilterExpression="receipt_id = :rid", ExpressionAttributeValues={':rid': {'S': donation_id}})
    if not response.get('Items'):
        return {"error": f"Receipt {donation_id} not found"}
    item = response['Items'][0]
    donor_email = item.get('donor_email', {}).get('S', '')
    receipt_url = item.get('receipt_url', {}).get('S', '')
    donor_name = item.get('donor', {}).get('S', 'Valued Donor')
    if not donor_email or donor_email == 'None':
        return {"error": "No email address on file"}
    try:
        ses.send_email(Source='pantrypilot@demo.com', Destination={'ToAddresses': [donor_email]}, Message={'Subject': {'Data': f'Your Tax Receipt - {donation_id}'}, 'Body': {'Text': {'Data': f"Dear {donor_name},\n\nYour receipt is ready: {receipt_url}\n\nThank you!"}}})
        dynamodb.put_item(TableName=TABLE_NAME, Item={**item, 'status': {'S': 'SENT_TO_DONOR'}, 'sent_at': {'S': datetime.now().isoformat()}})
        return {"message": f"Receipt {donation_id} sent to {donor_email}"}
    except Exception as e:
        return {"error": f"Failed to send email: {str(e)}"}

# ✅ NEW SEARCH FUNCTION
def search_archive(query: str):
    if not query:
        return []
    
    # Scan DynamoDB (Perfect for hackathon scale)
    response = dynamodb.scan(TableName=TABLE_NAME)
    results = []
    query_lower = query.lower()
    
    for item in response.get('Items', []):
        donor = item.get('donor', {}).get('S', '').lower()
        email = item.get('donor_email', {}).get('S', '').lower()
        phone = item.get('donor_phone', {}).get('S', '').lower()
        
        # Check if query matches name, email, or phone
        if query_lower in donor or query_lower in email or query_lower in phone:
            results.append({
                'donation_id': item.get('receipt_id', {}).get('S', 'Unknown'),
                'donor': item.get('donor', {}).get('S', 'Unknown'),
                'email': item.get('donor_email', {}).get('S', 'None'),
                'phone': item.get('donor_phone', {}).get('S', 'None'),
                'status': item.get('status', {}).get('S', 'Unknown'),
                'date': item.get('sk', {}).get('S', 'Unknown'),
                'receipt_url': item.get('receipt_url', {}).get('S', '')
            })
    return results

def lambda_handler(event, context):
    route = event.get('rawPath', '/')
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    
    if route == '/scan' and method == 'GET':
        transcribe_voice()
        approvals = scan_and_parse_messages()
        return {"statusCode": 200, "headers": {"Access-Control-Allow-Origin": "*"}, "body": json.dumps(approvals)}
        
    elif route == '/approve' and method == 'POST':
        body = json.loads(event.get('body', '{}'))
        result = approve_message(body.get('filename'), body.get('parsed_data', {}))
        return {"statusCode": 200, "headers": {"Access-Control-Allow-Origin": "*"}, "body": json.dumps(result)}
        
    elif route == '/send-receipt' and method == 'POST':
        body = json.loads(event.get('body', '{}'))
        result = send_receipt_to_donor(body.get('donation_id', ''))
        status_code = 400 if 'error' in result else 200
        return {"statusCode": status_code, "headers": {"Access-Control-Allow-Origin": "*"}, "body": json.dumps(result)}
        
    # ✅ NEW SEARCH ROUTE
    elif route == '/search' and method == 'GET':
        query_params = event.get('queryStringParameters', {}) or {}
        query = query_params.get('q', '')
        results = search_archive(query)
        return {"statusCode": 200, "headers": {"Access-Control-Allow-Origin": "*"}, "body": json.dumps(results)}
        
    return {"statusCode": 404, "body": "Not found"}