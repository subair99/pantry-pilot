# backend/tools/receipt_generator.py
from fpdf import FPDF
from pathlib import Path
from datetime import datetime

class TaxReceiptPDF(FPDF):
    def header(self):
        # w=0 means "use full width between margins"
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "PantryPilot Food Bank", ln=True, align="C")
        
        self.set_font("Helvetica", "", 12)
        self.cell(0, 5, "Official Tax Receipt for Charitable Donation", ln=True, align="C")
        
        self.ln(5)
        # Draw a line across the page
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def generate_tax_receipt(donation_data: dict, donation_id: str) -> str:
    """
    Generates an IRS-compliant PDF tax receipt.
    """
    output_dir = Path(__file__).parent.parent / "generated_receipts"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"receipt_{donation_id}.pdf"

    pdf = TaxReceiptPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Set safe margins
    pdf.set_margins(left=15, top=15, right=15)
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- HELPER FUNCTION ---
    # This function guarantees text never cuts off by resetting X to the left margin
    # and using w=0 (full available width).
    def print_line(text, bold=False, size=10, h=6):
        pdf.set_x(pdf.l_margin)  # Force cursor to left edge
        pdf.set_font("Helvetica", "B" if bold else "", size)
        pdf.multi_cell(w=0, h=h, text=text) # w=0 uses all space to the right margin
        pdf.ln(1) # Small gap between lines

    # 1. Receipt Details (Full width lines to prevent cutoff)
    print_line(f"Receipt ID: {donation_id}", bold=True, size=11)
    print_line(f"Date Issued: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", size=10)
    pdf.ln(5)

    # 2. Donor Information
    print_line("Donor Information", bold=True, size=12, h=8)
    print_line(f"Name: {donation_data.get('donor', 'Anonymous Donor')}")
    print_line(f"Email: {donation_data.get('donor_email', 'N/A')}")
    print_line(f"Phone: {donation_data.get('donor_phone', 'N/A')}")
    pdf.ln(5)

    # 3. Donation Details
    print_line("Donation Details", bold=True, size=12, h=8)
    print_line(f"Drop-off Notes: {donation_data.get('notes', 'N/A')}")
    pdf.ln(2)
    
    print_line("Items Donated:", bold=True, size=10)
    items = donation_data.get("items", [])
    if items:
        for item in items:
            print_line(f"  - {item}")
    else:
        print_line("  - Miscellaneous items")
        
    print_line(f"Total Estimated Quantity: {donation_data.get('quantity', 0)} units")
    pdf.ln(5)

    # 4. IRS Compliance Statement
    print_line("IRS Compliance & Acknowledgment", bold=True, size=11, h=8)
    irs_text = (
        "No goods or services were provided in exchange for this donation. "
        "PantryPilot Food Bank is a registered 501(c)(3) non-profit organization. "
        "This document serves as an official acknowledgment of your charitable contribution "
        "for tax purposes. Please retain this receipt for your records."
    )
    print_line(irs_text, size=9, h=5)

    # 5. Signature Line
    pdf.ln(10)
    pdf.set_x(pdf.l_margin)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 75, pdf.get_y())
    pdf.ln(5)
    print_line("Authorized Signature, PantryPilot Food Bank", size=9)

    # Save the PDF
    pdf.output(str(file_path))
    return str(file_path)