# backend/tools/receipt_generator.py
import os
from datetime import datetime
from pathlib import Path
from fpdf import FPDF

class TaxReceiptPDF(FPDF):
    def header(self):
        # Logo or header line
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'PANTRYPILOT FOOD BANK', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, 'Tax Donation Receipt', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_tax_receipt(donation_data: dict, receipt_id: str) -> str:
    """
    Generates an IRS-compliant tax receipt PDF for a donation.
    Returns the file path of the generated PDF.
    """
    # Ensure receipts directory exists
    receipts_dir = Path(__file__).parent.parent / "generated_receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    
    # Create PDF
    pdf = TaxReceiptPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Receipt Header
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f'Receipt ID: {receipt_id}', 0, 1)
    pdf.cell(0, 10, f'Date Issued: {datetime.now().strftime("%B %d, %Y")}', 0, 1)
    pdf.ln(5)
    
    # Donor Information
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'DONOR INFORMATION', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f'Donor Name: {donation_data.get("donor_name", "Unknown")}', 0, 1)
    pdf.cell(0, 6, f'Date of Donation: {donation_data.get("donation_date", datetime.now().strftime("%B %d, %Y"))}', 0, 1)
    if donation_data.get("donor_email"):
        pdf.cell(0, 6, f'Email: {donation_data["donor_email"]}', 0, 1)
    if donation_data.get("donor_phone"):
        pdf.cell(0, 6, f'Phone: {donation_data["donor_phone"]}', 0, 1)
    pdf.ln(5)
    
    # Donation Details
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'DONATION DETAILS', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    # Items table header
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(120, 7, 'Item Description', 1, 0, 'L', True)
    pdf.cell(40, 7, 'Quantity', 1, 0, 'C', True)
    pdf.cell(30, 7, 'Est. Value', 1, 1, 'R', True)
    
    # Items
    pdf.set_font('Arial', '', 10)
    items = donation_data.get("items", [])
    quantity = donation_data.get("quantity", 0)
    estimated_value = donation_data.get("estimated_value", "$0.00")
    
    # Simple item listing
    for i, item in enumerate(items[:3]):  # Show first 3 items
        pdf.cell(120, 7, item[:40], 1, 0, 'L')
        if i == 0:
            pdf.cell(40, 7, str(quantity), 1, 0, 'C')
            pdf.cell(30, 7, estimated_value, 1, 1, 'R')
        else:
            pdf.cell(70, 7, '', 1, 1, 'L')
    
    # If more than 3 items, add "and X more"
    if len(items) > 3:
        pdf.cell(120, 7, f"... and {len(items) - 3} more items", 1, 0, 'L')
        pdf.cell(70, 7, '', 1, 1, 'L')
    
    pdf.ln(5)
    
    # Total Value
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(160, 8, 'Total Estimated Fair Market Value:', 0, 0, 'R')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(30, 8, estimated_value, 0, 1, 'R')
    pdf.ln(10)
    
    # IRS Compliance Statement
    pdf.set_font('Arial', 'I', 9)
    pdf.multi_cell(0, 5, 'IMPORTANT TAX INFORMATION:')
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 5, 
        'No goods or services were provided by PantryPilot Food Bank in exchange for this donation. '
        'This receipt is provided in compliance with IRS regulations for charitable contributions. '
        'The donor is responsible for determining the fair market value of donated goods. '
        'Please consult with a tax professional for specific deduction questions.'
    )
    pdf.ln(5)
    
    # Organization Info
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 7, 'PantryPilot Food Bank', 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 5, '501(c)(3) Non-Profit Organization', 0, 1)
    pdf.cell(0, 5, 'EIN: XX-XXXXXXX', 0, 1)
    pdf.cell(0, 5, 'www.pantrypilot.org', 0, 1)
    pdf.ln(5)
    
    # Signature line
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 10, '_________________________', 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 5, 'Authorized Signature', 0, 1)
    pdf.cell(0, 5, f'Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', 0, 1)
    
    # Save PDF
    pdf_path = receipts_dir / f"receipt_{receipt_id}.pdf"
    pdf.output(str(pdf_path))
    
    return str(pdf_path)