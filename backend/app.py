from flask import Flask, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile

app = Flask(__name__)

@app.route("/")
def index():
    return open("frontend/index.html").read()

@app.route("/generate", methods=["POST"])
def generate():
    data = request.form.to_dict(flat=False)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
        c = canvas.Canvas(pdf_file.name, pagesize=A4)
        width, height = A4

        y = height - 40
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, "Invoice")
        y -= 30

        def draw_section(title, keys):
            nonlocal y
            c.setFont("Helvetica-Bold", 12)
            c.drawString(30, y, title)
            y -= 20
            c.setFont("Helvetica", 10)
            for key in keys:
                val = data.get(key, [""])[0]
                c.drawString(40, y, f"{key.replace('_', ' ').title()}: {val}")
                y -= 15
            y -= 10

        draw_section("Issuer Details", ["issuer_name", "issuer_address", "issuer_mobile", "issuer_pan"])
        draw_section("Client Details", ["client_name", "client_address", "client_pan", "client_gst"])

        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y, "Items")
        y -= 20
        c.setFont("Helvetica", 10)
        c.drawString(30, y, "Sr No | Description | Date/Qty | Price")
        y -= 15
        items = zip(data.get("item_0", []), data.get("item_1", []), data.get("item_2", []), data.get("item_3", []))
        for item in items:
            c.drawString(30, y, " | ".join(item))
            y -= 15
        y -= 10

        draw_section("Banking Details", ["bank_name", "bank_number", "bank_ifsc", "bank_branch"])

        c.showPage()
        c.save()
        return send_file(pdf_file.name, as_attachment=True, download_name="invoice.pdf")

if __name__ == "__main__":
    app.run(debug=True)
