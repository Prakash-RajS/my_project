"""from fpdf import FPDF
import os
from datetime import datetime

def generate_invoice_pdf(billing_data: dict, output_dir: str = "invoices") -> str:
    os.makedirs(output_dir, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Invoice", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Invoice ID: {billing_data['invoice_id']}", ln=True)
    pdf.cell(200, 10, txt=f"Plan: {billing_data['plan_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Amount: ${billing_data['amount']}", ln=True)
    pdf.cell(200, 10, txt=f"Payment Method: {billing_data['payment_method']}", ln=True)
    pdf.cell(200, 10, txt=f"Status: {billing_data['status']}", ln=True)
    pdf.cell(200, 10, txt=f"Paid On: {billing_data['paid_on']}", ln=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(output_dir, f"invoice_{billing_data['invoice_id']}_{timestamp}.pdf")
    pdf.output(file_path)

    return file_path"""



"""from fpdf import FPDF
import os
from datetime import datetime
  
def generate_invoice_pdf(billing_data: dict, output_dir: str = "invoices") -> str:
    os.makedirs(output_dir, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    
    # Document metadata
    pdf.set_title("Invoice")
    pdf.set_author("Your Company Name")

    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "Your Company Name", ln=True)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(190, 10, "123 Business Rd, Tech City", ln=True)
    pdf.cell(190, 10, "Email: support@yourcompany.com", ln=True)
    pdf.ln(5)

    # Title
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, "INVOICE", ln=True, align="C")
    pdf.ln(5)

    # Invoice Details
    pdf.set_font("Arial", '', 12)
    pdf.cell(190, 10, f"Invoice ID: {billing_data['invoice_id']}", ln=True)
    pdf.cell(190, 10, f"Date: {billing_data['paid_on']}", ln=True)
    pdf.cell(190, 10, f"Status: {billing_data['status']}", ln=True)
    pdf.ln(5)

    # Table Header
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(90, 10, "Description", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Duration", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Amount", 1, 1, 'C', fill=True)

    # Table Row
    pdf.set_font("Arial", '', 12)
    pdf.cell(90, 10, billing_data["plan_name"], 1)
    pdf.cell(50, 10, billing_data.get("duration", "1 Month"), 1)
    pdf.cell(50, 10, f"${billing_data['amount']:.2f}", 1, ln=True)

    # Payment method
    pdf.ln(5)
    pdf.cell(190, 10, f"Payment Method: {billing_data['payment_method']}", ln=True)

    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 11)
    pdf.cell(190, 10, "Thank you for your purchase!", ln=True, align="C")

    # Save
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(output_dir, f"invoice_{billing_data['invoice_id']}_{timestamp}.pdf")
    pdf.output(file_path)

    return file_path"""


"""from fpdf import FPDF
import os
from datetime import datetime

def generate_invoice_pdf(billing_data: dict, output_dir: str = "invoices") -> str:
    os.makedirs(output_dir, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Colors
    primary_color = (30, 144, 255)  # Dodger Blue
    grey = (100, 100, 100)

    # Company Name - Header
    pdf.set_fill_color(*primary_color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(190, 15, "  YOUR COMPANY NAME", ln=True, fill=True)
    
    # Address & Email
    pdf.set_text_color(*grey)
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 8, "  123 Tech Lane, Innovation City", ln=True)
    pdf.cell(190, 8, "  Email: billing@yourcompany.com", ln=True)
    pdf.ln(10)

    # INVOICE Title with Blue Line
    pdf.set_text_color(*primary_color)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(190, 15, "INVOICE", ln=True, align="C")

    pdf.set_draw_color(*primary_color)
    pdf.set_line_width(1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    # Invoice Info
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(100, 10, f"Invoice ID: {billing_data['invoice_id']}", ln=False)
    pdf.cell(90, 10, f"Date: {billing_data['paid_on']}", ln=True)
    pdf.cell(100, 10, f"Status: {billing_data['status']}", ln=False)
    pdf.cell(90, 10, f"Payment Method: {billing_data['payment_method']}", ln=True)
    pdf.ln(8)

    # Table Header
    pdf.set_fill_color(*primary_color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(90, 10, "Plan Name", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Duration", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Amount", 1, 1, 'C', fill=True)

    # Table Row
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(90, 10, billing_data["plan_name"], 1)
    pdf.cell(50, 10, billing_data.get("duration", "1 Month"), 1)
    pdf.cell(50, 10, f"${billing_data['amount']:.2f}", 1, ln=True)

    # Thank You Message
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 12)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(190, 10, "Thank you for your purchase and trust in us!", ln=True, align="C")
    pdf.cell(190, 7, "If you have any questions, contact billing@yourcompany.com", ln=True, align="C")

    # Save File
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(output_dir, f"invoice_{billing_data['invoice_id']}_{timestamp}.pdf")
    pdf.output(file_path)

    return file_path"""

from fpdf import FPDF
import os
from datetime import datetime

def generate_invoice_pdf(billing_data: dict, output_dir: str = "invoices") -> str:
    os.makedirs(output_dir, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Define colors
    header_color = (52, 152, 219)
    primary_color = (41, 128, 185)
    grey_color = (120, 120, 120)
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Add Logo
    logo_path = os.path.join("fastapi_app", "static", "logo.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=10, w=40)

    # Company info
    pdf.set_xy(55, 10)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(*primary_color)
    pdf.cell(140, 10, "YOUR COMPANY NAME", ln=True, align="R")

    pdf.set_xy(55, 18)
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(*grey_color)
    pdf.cell(140, 6, "123 Tech Lane, Innovation City", ln=True, align="R")
    pdf.cell(190, 6, "Email: billing@yourcompany.com", ln=True, align="R")
    pdf.ln(12)

    # Invoice header
    pdf.set_fill_color(*header_color)
    pdf.set_text_color(*white)
    pdf.set_font("Arial", 'B', 26)
    pdf.cell(190, 15, "INVOICE", ln=True, align="C")
    pdf.set_draw_color(*header_color)
    pdf.set_line_width(1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Invoice details
    pdf.set_text_color(*black)
    pdf.set_font("Arial", '', 12)

    label_font = ("Arial", '', 12)
    value_font = ("Arial", 'B', 12)

    details = [
        ("Invoice ID:", billing_data['invoice_id']),
        ("Status:", billing_data['status']),
        ("Date:", billing_data['paid_on']),
        ("Payment Method:", billing_data['payment_method']),
    ]

    for label, value in details:
        pdf.set_font(*label_font)
        pdf.cell(50, 10, label, ln=False)
        pdf.set_font(*value_font)
        pdf.cell(140, 10, str(value), ln=True)

    pdf.ln(5)

    # Table headers
    pdf.set_fill_color(*primary_color)
    pdf.set_text_color(*white)
    pdf.set_font("Arial", 'B', 12)
    col_widths = [90, 50, 50]
    headers = ["Plan Name", "Duration", "Amount"]

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1, 0, 'C', fill=True)
    pdf.ln()

    # Table data
    pdf.set_text_color(*black)
    pdf.set_font("Arial", '', 12)
    pdf.cell(col_widths[0], 10, billing_data["plan_name"], 1)
    pdf.cell(col_widths[1], 10, billing_data.get("duration", "1 Month"), 1)
    pdf.cell(col_widths[2], 10, f"${billing_data['amount']:.2f}", 1)
    pdf.ln()

    # Total row - same width as table
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(col_widths[0] + col_widths[1], 10, "Total:", 1, 0, 'R', fill=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(col_widths[2], 10, f"${billing_data['amount']:.2f}", 1, ln=True, fill=True)

    pdf.ln(20)

    # Thank you note and contact info
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(*primary_color)
    pdf.cell(190, 10, "Thank you for your business!", ln=True, align="C")

    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(*grey_color)
    pdf.cell(190, 8, "If you have any questions, contact us at billing@yourcompany.com", ln=True, align="C")

    # Save the PDF
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(output_dir, f"invoice_{billing_data['invoice_id']}_{timestamp}.pdf")
    pdf.output(file_path)

    return file_path





