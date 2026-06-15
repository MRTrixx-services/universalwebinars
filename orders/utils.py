from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
import qrcode
import base64


def generate_invoice_pdf(order):
    """
    Ultra-fast single-page invoice generator with QR
    """
    verification_url = f"https://dailyrespond.com/orders/{order.order_number}"
    
    # Super minimal QR for speed
    qr = qrcode.QRCode(version=1, box_size=3, border=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    qr_img.save(buf, format="PNG", optimize=True)
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    
    context = {
        "order": order,
        "qr_code": qr_b64,
        "company": {
            "name": "dailyrespond",
            "address": "Professional Learning Hub",
            "website": "https://dailyrespond.com",
            "email": "support@dailyrespond.com"
        }
    }
    
    html_string = render_to_string("invoice/invoice.html", context)
    pdf_file = BytesIO()
    HTML(string=html_string, base_url="").write_pdf(pdf_file, presentational_hints=False)
    pdf_file.seek(0)
    
    return pdf_file
