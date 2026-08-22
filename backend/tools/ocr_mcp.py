# backend/tools/ocr_mcp.py
import json

def extract_donation_details(image_url_or_text: str) -> str:
    """
    Extracts structured donation details (donor name, items, quantity) from 
    an image URL or raw text message. 
    (Simulated for demo reliability; replace with boto3 textract in production).
    """
    # Simulating a successful OCR parse of a text like: 
    # "Hi, this is John. Dropping off 12 boxes of pasta and 20lbs of apples at 5 PM."
    
    # In a real scenario, you would call AWS Textract here:
    # client = boto3.client('textract', region_name='us-east-1')
    # response = client.detect_document_text(Document={'Bytes': image_data})
    
    simulated_result = {
        "donor_name": "John Doe",
        "items": ["boxes of pasta", "lbs of apples"],
        "quantity": 32, # combined estimate
        "dropoff_time": "5 PM",
        "confidence": 0.98
    }
    
    return json.dumps(simulated_result, indent=2)