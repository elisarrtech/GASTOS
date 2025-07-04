from io import BytesIO
from xhtml2pdf import pisa

def generar_pdf(html_content):
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(html_content.encode("utf-8")), dest=pdf)
    return pdf.getvalue()
