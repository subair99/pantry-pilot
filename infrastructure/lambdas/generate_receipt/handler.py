# infrastructure/lambdas/generate_receipt/handler.py
import os
import boto3
import json
from datetime import datetime
from fpdf import FPDF

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('RECEIPTS_BUCKET_NAME')

def lambda_handler(event, context):
    # AgentCore passes tool arguments inside the 'arguments' key
    arguments = event.get('arguments', {})
    donation_id = arguments.get('donation_id', 'UNKNOWN')
    donor_name = arguments.get('donor_name', 'Anonymous')
    items = arguments.get('items', [])
    quantity = arguments.get('quantity', 0)

    # 1. Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "PantryPilot Tax Receipt", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Donation ID: {donation_id}", ln=True)
    pdf.cell(0, 8, f"Donor: {donor_name}", ln=True)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, f"Items: {', '.join(items)}", ln=True)
    pdf.cell(0, 8, f"Quantity: {quantity}", ln=True)
    
    # Save locally
    local_pdf_path = f"/tmp/receipt_{donation_id}.pdf"
    pdf.output(local_pdf_path)

    # 2. Upload to S3
    s3_key = f"receipts/{donation_id}.pdf"
    s3.upload_file(local_pdf_path, BUCKET_NAME, s3_key)

    # 3. Return result to AgentCore
    s3_url = f"s3://{BUCKET_NAME}/{s3_key}"
    
    return {
        "status": "success",
        "receipt_url": s3_url,
        "message": f"Receipt generated and saved to {s3_url}"
    }