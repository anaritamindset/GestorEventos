"""
Certificate Service - Handles PDF certificate generation with QR codes
"""

import os
import logging
import qrcode
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image
from app.models import Participant, Event, CertificateTemplate

logger = logging.getLogger(__name__)


class CertificateService:
    """Service to generate PDF certificates with QR codes"""

    def __init__(self, output_dir='certificados'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Register fonts (you might need to adjust font paths)
        self._register_fonts()

    def _register_fonts(self):
        """Register custom fonts for Portuguese characters"""
        try:
            # Try to register common system fonts
            # macOS paths
            font_paths = [
                ('/System/Library/Fonts/Helvetica.ttc', 'Helvetica'),
                ('/System/Library/Fonts/Supplemental/Arial.ttf', 'Arial'),
                ('/System/Library/Fonts/Supplemental/Times New Roman.ttf', 'Times'),
            ]

            for font_path, font_name in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        logger.info(f"Registered font: {font_name}")
                    except Exception as e:
                        logger.warning(f"Could not register {font_name}: {e}")

        except Exception as e:
            logger.warning(f"Font registration failed: {e}")
            logger.info("Will use default ReportLab fonts")

    def generate_qr_code(self, data, size=200):
        """
        Generate QR code image

        Args:
            data: Data to encode in QR code (usually validation URL)
            size: Size of QR code in pixels

        Returns:
            PIL Image object
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        return img

    def generate_certificate(self, participant_id, template_id=None, base_url='http://localhost:5000'):
        """
        Generate certificate PDF for a participant

        Args:
            participant_id: Participant ID
            template_id: Optional template ID (uses default if None)
            base_url: Base URL for validation links

        Returns:
            Path to generated PDF file
        """
        # Get participant and event
        participant = Participant.query.get(participant_id)
        if not participant or participant.deleted_at:
            raise ValueError(f"Participante {participant_id} não encontrado")

        event = Event.query.get(participant.evento_id)
        if not event or event.deleted_at:
            raise ValueError(f"Evento {participant.evento_id} não encontrado")

        # Get template
        if template_id:
            template = CertificateTemplate.query.get(template_id)
        else:
            template = CertificateTemplate.query.filter_by(is_default=True, is_active=True).first()

        if not template:
            logger.warning("No template found, using default design")
            config = self._get_default_template_config()
        else:
            config = template.config

        # Generate filename
        filename = f"certificado_{participant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        # Generate QR code with validation URL
        validation_url = f"{base_url}/validate/certificate/{participant_id}"
        qr_img = self.generate_qr_code(validation_url)

        # Save QR code temporarily
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)

        # Create PDF
        self._create_pdf(
            filepath=filepath,
            participant=participant,
            event=event,
            qr_buffer=qr_buffer,
            config=config
        )

        logger.info(f"Certificate generated: {filepath}")
        return filepath

    def _create_pdf(self, filepath, participant, event, qr_buffer, config):
        """Create the actual PDF certificate"""
        # Use landscape A4
        page_width, page_height = landscape(A4)

        # Create canvas
        c = canvas.Canvas(filepath, pagesize=landscape(A4))

        # Colors
        primary_color = HexColor(config.get('primary_color', '#1e3a8a'))
        secondary_color = HexColor(config.get('secondary_color', '#3b82f6'))
        text_color = HexColor(config.get('text_color', '#1f2937'))

        # Draw border
        border_margin = 1.5 * cm
        c.setStrokeColor(primary_color)
        c.setLineWidth(3)
        c.rect(border_margin, border_margin,
               page_width - 2 * border_margin,
               page_height - 2 * border_margin)

        # Inner border
        inner_margin = 2 * cm
        c.setStrokeColor(secondary_color)
        c.setLineWidth(1)
        c.rect(inner_margin, inner_margin,
               page_width - 2 * inner_margin,
               page_height - 2 * inner_margin)

        # Title
        c.setFont("Helvetica-Bold", 32)
        c.setFillColor(primary_color)
        title_text = "CERTIFICADO DE PARTICIPAÇÃO"
        title_width = c.stringWidth(title_text, "Helvetica-Bold", 32)
        c.drawString((page_width - title_width) / 2, page_height - 4 * cm, title_text)

        # Line under title
        c.setStrokeColor(secondary_color)
        c.setLineWidth(2)
        c.line(page_width * 0.3, page_height - 4.5 * cm,
               page_width * 0.7, page_height - 4.5 * cm)

        # Intro text
        c.setFont("Helvetica", 14)
        c.setFillColor(text_color)
        intro_text = "Certificamos que"
        intro_width = c.stringWidth(intro_text, "Helvetica", 14)
        c.drawString((page_width - intro_width) / 2, page_height - 6 * cm, intro_text)

        # Participant name (highlighted)
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(primary_color)
        name_text = participant.nome
        name_width = c.stringWidth(name_text, "Helvetica-Bold", 24)
        c.drawString((page_width - name_width) / 2, page_height - 7.5 * cm, name_text)

        # Line under name
        name_line_width = name_width + 2 * cm
        c.setStrokeColor(secondary_color)
        c.setLineWidth(1)
        c.line((page_width - name_line_width) / 2, page_height - 8 * cm,
               (page_width + name_line_width) / 2, page_height - 8 * cm)

        # Event description
        c.setFont("Helvetica", 14)
        c.setFillColor(text_color)

        event_text_1 = "participou do evento"
        event_text_1_width = c.stringWidth(event_text_1, "Helvetica", 14)
        c.drawString((page_width - event_text_1_width) / 2, page_height - 9.5 * cm, event_text_1)

        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(primary_color)
        event_name_text = event.nome
        event_name_width = c.stringWidth(event_name_text, "Helvetica-Bold", 18)
        c.drawString((page_width - event_name_width) / 2, page_height - 11 * cm, event_name_text)

        # Event details
        c.setFont("Helvetica", 12)
        c.setFillColor(text_color)

        # Date
        data_str = event.data_inicio.strftime('%d/%m/%Y')
        if event.data_fim and event.data_fim != event.data_inicio:
            data_str += f" a {event.data_fim.strftime('%d/%m/%Y')}"

        details_y = page_height - 12.5 * cm
        details = [
            f"Data: {data_str}",
            f"Duração: {event.duracao_horas} horas",
        ]

        if event.local:
            details.append(f"Local: {event.local}")

        if event.formadora:
            details.append(f"Formador(a): {event.formadora}")

        for detail in details:
            detail_width = c.stringWidth(detail, "Helvetica", 12)
            c.drawString((page_width - detail_width) / 2, details_y, detail)
            details_y -= 0.7 * cm

        # QR Code
        qr_size = 3 * cm
        qr_x = page_width - 4 * cm
        qr_y = 2.5 * cm

        # Draw QR code image
        img = Image(qr_buffer, width=qr_size, height=qr_size)
        img.drawOn(c, qr_x, qr_y)

        # QR code label
        c.setFont("Helvetica", 8)
        c.setFillColor(text_color)
        qr_label = "Valide este certificado"
        qr_label_width = c.stringWidth(qr_label, "Helvetica", 8)
        c.drawString(qr_x + (qr_size - qr_label_width) / 2, qr_y - 0.5 * cm, qr_label)

        # Emission date
        c.setFont("Helvetica", 10)
        emission_date = datetime.now().strftime('%d de %B de %Y')
        emission_text = f"Emitido em {emission_date}"
        emission_width = c.stringWidth(emission_text, "Helvetica", 10)
        c.drawString((page_width - emission_width) / 2, 3 * cm, emission_text)

        # Certificate ID (small, at bottom)
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#9ca3af'))
        cert_id = f"Certificado ID: {participant.id} | Evento ID: {event.id}"
        cert_id_width = c.stringWidth(cert_id, "Helvetica", 8)
        c.drawString((page_width - cert_id_width) / 2, 1.5 * cm, cert_id)

        # Save PDF
        c.save()

    def _get_default_template_config(self):
        """Get default template configuration"""
        return {
            'primary_color': '#1e3a8a',
            'secondary_color': '#3b82f6',
            'text_color': '#1f2937',
            'font_title': 'Helvetica-Bold',
            'font_body': 'Helvetica',
            'border_style': 'double',
            'include_qr': True,
            'include_logo': False
        }

    def batch_generate_certificates(self, event_id, template_id=None, base_url='http://localhost:5000'):
        """
        Generate certificates for all participants in an event

        Args:
            event_id: Event ID
            template_id: Optional template ID
            base_url: Base URL for validation

        Returns:
            dict with generation statistics
        """
        event = Event.query.get(event_id)
        if not event or event.deleted_at:
            raise ValueError(f"Evento {event_id} não encontrado")

        participants = Participant.query.filter_by(
            evento_id=event_id,
            deleted_at=None
        ).all()

        stats = {
            'total': len(participants),
            'generated': 0,
            'errors': 0,
            'error_details': []
        }

        for participant in participants:
            try:
                filepath = self.generate_certificate(
                    participant_id=participant.id,
                    template_id=template_id,
                    base_url=base_url
                )

                # Update participant record
                participant.certificado_gerado = True
                participant.certificado_path = filepath

                from app import db
                db.session.commit()

                stats['generated'] += 1
                logger.info(f"Generated certificate for {participant.nome}")

            except Exception as e:
                stats['errors'] += 1
                stats['error_details'].append({
                    'participant_id': participant.id,
                    'participant_name': participant.nome,
                    'error': str(e)
                })
                logger.error(f"Error generating certificate for {participant.nome}: {e}")

                from app import db
                db.session.rollback()

        return stats
