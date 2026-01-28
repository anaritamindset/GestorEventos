"""
Certificate Service - Handles PDF certificate generation
"""

import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from app.models import Participant, Event, CertificateTemplate

logger = logging.getLogger(__name__)


class CertificateService:
    """Service to generate PDF certificates"""

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

    def generate_certificate(self, participant_id, template_id=None):
        """
        Generate certificate PDF for a participant

        Args:
            participant_id: Participant ID
            template_id: Optional template ID (uses default if None)

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

        # Create PDF
        self._create_pdf(
            filepath=filepath,
            participant=participant,
            event=event,
            config=config
        )

        logger.info(f"Certificate generated: {filepath}")
        return filepath

    def _center_text(self, c, text, y, font, size):
        """Helper to center text horizontally"""
        text_width = c.stringWidth(text, font, size)
        page_width, _ = landscape(A4)
        return (page_width - text_width) / 2, text_width

    def _draw_centered_text(self, c, text, y, font, size, color):
        """Draw centered text at specified y position"""
        c.setFont(font, size)
        c.setFillColor(color)
        x, _ = self._center_text(c, text, y, font, size)
        c.drawString(x, y, text)

    def _get_absolute_path(self, relative_path):
        """Convert relative path to absolute path based on project root"""
        if os.path.isabs(relative_path):
            return relative_path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        return os.path.join(project_root, relative_path)

    def _create_pdf(self, filepath, participant, event, config):
        """Create the actual PDF certificate"""
        page_width, page_height = landscape(A4)
        c = canvas.Canvas(filepath, pagesize=landscape(A4))

        # Get organization for colors and logo
        organizacao = event.organizacao if event.organizacao else None

        # Extract colors from organization or config
        if organizacao:
            primary_color = HexColor(organizacao.cor_primaria or config.get('primary_color', '#9DB5A5'))
            secondary_color = HexColor(organizacao.cor_secundaria or config.get('secondary_color', '#C8B8D8'))
        else:
            primary_color = HexColor(config.get('primary_color', '#9DB5A5'))
            secondary_color = HexColor(config.get('secondary_color', '#C8B8D8'))

        text_color = HexColor(config.get('text_color', '#1f2937'))

        # Logo first (will be behind borders)
        # Move logo down by 2 lines (~1.6cm)
        current_y = page_height - 6 * cm - 1.6 * cm

        # Use organization logo if available, otherwise use template logo
        logo_path_to_use = None
        if organizacao and organizacao.logo_path:
            logo_path_to_use = organizacao.logo_path
        elif config.get('logo_path'):
            logo_path_to_use = config.get('logo_path')

        if config.get('include_logo', True) and logo_path_to_use:
            logo_path = self._get_absolute_path(logo_path_to_use)

            if os.path.exists(logo_path):
                try:
                    from PIL import Image

                    # Load image to get dimensions
                    img = Image.open(logo_path)
                    img_width, img_height = img.size
                    aspect_ratio = img_width / img_height

                    # Fixed width for consistent sizing
                    # All logos will have same width, height varies by aspect ratio
                    target_width = 4.5 * cm
                    logo_width = target_width
                    logo_height = target_width / aspect_ratio

                    # Center logo horizontally
                    logo_x = (page_width - logo_width) / 2

                    # Use mask='auto' to preserve transparency in PNG files
                    c.drawImage(ImageReader(logo_path), logo_x, current_y,
                               width=logo_width, height=logo_height,
                               mask='auto')
                    current_y -= 0.2 * cm  # Small padding below logo
                    logger.info(f"Logo added from {logo_path} ({logo_width/cm:.1f}x{logo_height/cm:.1f}cm)")
                except Exception as e:
                    logger.error(f"Could not add logo: {e}")
            else:
                logger.warning(f"Logo not found: {logo_path}")

        # Draw borders (on top of logo)
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
        # Move title down by 1 additional line (0.8cm)
        current_y -= 0.3 * cm + 0.8 * cm
        self._draw_centered_text(c, "CERTIFICADO DE PARTICIPAÇÃO", current_y,
                                "Helvetica-Bold", 32, primary_color)

        # Main certificate text with bold formatting
        # Reduce spacing: 2cm base + 4cm - 4cm (5 lines up) = 2cm total
        current_y -= 2 * cm

        # Build event details inline - data por extenso
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        dia = event.data_inicio.day
        mes = meses[event.data_inicio.month]
        ano = event.data_inicio.year
        data_str = f"{dia} de {mes} de {ano}"

        if event.data_fim and event.data_fim != event.data_inicio:
            dia_fim = event.data_fim.day
            mes_fim = meses[event.data_fim.month]
            ano_fim = event.data_fim.year
            data_str += f" a {dia_fim} de {mes_fim} de {ano_fim}"

        # Create full text with parts
        # Note: Punctuation is attached to preceding words to prevent orphaned commas
        text_parts = [
            ("Certificamos que ", "Helvetica", 16, text_color),
            (f"{participant.nome},", "Helvetica-Bold", 16, primary_color),
            (" participou no evento ", "Helvetica", 16, text_color),
            (f"{event.nome},", "Helvetica-Bold", 16, primary_color),
            (f" realizado a {data_str},", "Helvetica", 16, text_color),
            (f" com a duração de {event.duracao_minutos} minutos", "Helvetica", 16, text_color),
        ]

        # Add optional formadora
        if event.formadora:
            text_parts.append((", ministrado por ", "Helvetica", 16, text_color))
            text_parts.append((f"{event.formadora}.", "Helvetica-Bold", 16, primary_color))
        else:
            # Add period at the end if no formadora
            text_parts[-1] = (text_parts[-1][0] + ".", text_parts[-1][1], text_parts[-1][2], text_parts[-1][3])

        # Calculate total width and wrap if needed
        max_width = page_width - 6 * cm
        current_line = []
        current_line_width = 0
        lines = []

        for text, font, size, color in text_parts:
            text_width = c.stringWidth(text, font, size)

            if current_line_width + text_width > max_width and current_line:
                lines.append(current_line)
                current_line = []
                current_line_width = 0

            current_line.append((text, font, size, color))
            current_line_width += text_width

        if current_line:
            lines.append(current_line)

        # Draw the lines
        line_height = 0.8 * cm
        for line in lines:
            # Calculate total width of this line
            line_width = sum(c.stringWidth(t, f, s) for t, f, s, col in line)
            x = (page_width - line_width) / 2

            for text, font, size, color in line:
                c.setFont(font, size)
                c.setFillColor(color)
                c.drawString(x, current_y, text)
                x += c.stringWidth(text, font, size)

            current_y -= line_height

        # Signature (center bottom)
        sig_y = 4.5 * cm
        sig_x = page_width / 2

        # Handwritten signature above line
        self._draw_centered_text(c, "Ana Rita Vieira", sig_y + 0.3 * cm,
                                "Times-Italic", 22, text_color)

        # Signature line
        c.setStrokeColor(text_color)
        c.setLineWidth(1)
        c.line(sig_x - 3 * cm, sig_y, sig_x + 3 * cm, sig_y)

        # Organization name below line
        self._draw_centered_text(c, "Mindset & Wellness", sig_y - 0.5 * cm,
                                "Helvetica", 9, text_color)

        # Add seal/lacre logo in bottom left corner
        if organizacao and organizacao.seal_logo_path:
            seal_path = self._get_absolute_path(organizacao.seal_logo_path)
            if os.path.exists(seal_path):
                try:
                    from PIL import Image

                    # Load seal image
                    seal_img = Image.open(seal_path)
                    seal_aspect = seal_img.width / seal_img.height

                    # Seal size - 3cm height
                    seal_height = 3 * cm
                    seal_width = seal_height * seal_aspect

                    # Position in bottom left corner with margin
                    seal_x = 2.5 * cm
                    seal_y = 2.5 * cm

                    c.drawImage(ImageReader(seal_path), seal_x, seal_y,
                               width=seal_width, height=seal_height,
                               mask='auto')
                    logger.info(f"Seal logo added from {seal_path}")
                except Exception as e:
                    logger.error(f"Could not add seal logo: {e}")

        # Save PDF
        c.save()

    def _get_default_template_config(self):
        """Get default template configuration"""
        return {
            'primary_color': '#9DB5A5',  # Verde suave Mindset
            'secondary_color': '#C8B8D8',  # Lilás suave
            'text_color': '#1f2937',
            'font_title': 'Helvetica-Bold',
            'font_body': 'Helvetica',
            'border_style': 'double',
            'include_qr': False,
            'include_logo': True,
            'logo_path': 'Logos/ana_rita_m&w_logo_trnsp.png'  # Logo PNG transparente
        }

    def batch_generate_certificates(self, event_id, template_id=None):
        """
        Generate certificates for all participants in an event

        Args:
            event_id: Event ID
            template_id: Optional template ID

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
                    template_id=template_id
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
