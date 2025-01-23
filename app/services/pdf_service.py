from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import qrcode
from PIL import Image as PILImage  # Changed import
from datetime import datetime

class PDFService:
    @staticmethod
    async def generate_appointment_receipt(appointment_data: dict) -> BytesIO:
        """
        Generate a PDF receipt for an appointment
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Fetch styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        ))
        styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#3b5998')
        ))

        # Build the document content
        story = []

        # Header
        story.append(Paragraph("Appointment Receipt", styles['CustomTitle']))
        story.append(Paragraph(f"Receipt #{appointment_data['appointment_number']}", styles['CustomSubtitle']))
        story.append(Spacer(1, 12))

        # Create appointment details table
        appointment_details = [
            ['Doctor:', appointment_data['doctor_name']],
            ['Specialization:', appointment_data['doctor_specialization']],
            ['Hospital:', appointment_data['hospital_name']],
            ['Date:', appointment_data['appointment_date'].strftime('%B %d, %Y')],
            ['Time:', appointment_data['appointment_time'].strftime('%I:%M %p')],
            ['Status:', appointment_data['status']],
        ]

        detail_table = Table(appointment_details, colWidths=[2*inch, 4*inch])
        detail_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ]))
        story.append(detail_table)
        story.append(Spacer(1, 20))

        # Payment details
        story.append(Paragraph("Payment Details", styles['CustomSubtitle']))
        story.append(Spacer(1, 12))

        payment_details = [
            ['Item', 'Amount'],
            ['Consultation Fee', f"Rs. {appointment_data['consultation_fee']:.2f}"],
            ['Service Charge', f"Rs. {appointment_data['service_charge']:.2f}"],
            ['Total', f"Rs. {appointment_data['total_amount']:.2f}"],
        ]

        payment_table = Table(payment_details, colWidths=[4*inch, 2*inch])
        payment_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ]))
        story.append(payment_table)
        story.append(Spacer(1, 30))

        # Generate QR code
        qr_data = {
            'appointment_id': appointment_data['appointment_id'],
            'doctor': appointment_data['doctor_name'],
            'date': appointment_data['appointment_date'].strftime('%Y-%m-%d'),
            'time': appointment_data['appointment_time'].strftime('%H:%M')
        }
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to bytes
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Create a ReportLab Image object
        qr_image = Image(qr_buffer, width=2*inch, height=2*inch)
        
        # Add QR code to the document
        story.append(Paragraph("Scan QR code for digital verification:", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(qr_image)
        
        # Footer text
        story.append(Spacer(1, 30))
        footer_text = """
        This is a computer-generated document. No signature is required.
        For any queries, please contact our support team.
        """
        story.append(Paragraph(footer_text, styles['Normal']))

        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return buffer