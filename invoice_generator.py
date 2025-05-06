
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





