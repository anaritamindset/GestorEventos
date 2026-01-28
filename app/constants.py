"""
Application constants and configuration values
Centralizes magic numbers and repeated values for better maintainability
"""

from reportlab.lib.units import cm

# Certificate Layout Constants
class CertificateLayout:
    """Constants for certificate PDF layout"""

    # Logo sizing
    LOGO_TARGET_WIDTH = 4.5 * cm
    LOGO_TOP_MARGIN = 6 * cm
    LOGO_VERTICAL_OFFSET = 1.6 * cm  # Additional offset from top
    LOGO_PADDING_BELOW = 0.2 * cm

    # Seal/Lacre sizing and positioning
    SEAL_HEIGHT = 3 * cm
    SEAL_MARGIN_LEFT = 3.5 * cm
    SEAL_MARGIN_BOTTOM = 3.5 * cm

    # Borders
    BORDER_OUTER_MARGIN = 1.5 * cm
    BORDER_OUTER_WIDTH = 3
    BORDER_INNER_MARGIN = 2 * cm
    BORDER_INNER_WIDTH = 1

    # Text spacing
    TITLE_SPACING_BELOW_LOGO = 0.3 * cm
    TITLE_EXTRA_SPACING = 0.8 * cm
    BODY_SPACING_BELOW_TITLE = 2 * cm
    LINE_HEIGHT = 0.8 * cm
    MAX_TEXT_WIDTH_MARGIN = 6 * cm

    # Signature
    SIGNATURE_Y_POSITION = 4.5 * cm
    SIGNATURE_LINE_WIDTH = 6 * cm  # Total width (3cm on each side)
    SIGNATURE_NAME_OFFSET = 0.3 * cm
    SIGNATURE_ORG_OFFSET = 0.5 * cm

    # Font sizes
    FONT_SIZE_TITLE = 32
    FONT_SIZE_BODY = 16
    FONT_SIZE_SIGNATURE = 22
    FONT_SIZE_ORG = 9


# Certificate Text Constants
class CertificateText:
    """Text templates and formatting"""

    TITLE = "CERTIFICADO DE PARTICIPAÇÃO"

    # Text templates
    CERTIFY_PREFIX = "Certificamos que "
    PARTICIPATED_TEXT = " participou no evento "
    HELD_ON_TEXT = " realizado a "
    DURATION_TEXT_TEMPLATE = " com a duração de {} minutos"
    TAUGHT_BY_TEXT = ", ministrado por "

    # Month names in Portuguese
    MONTHS = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    # Fonts
    FONT_TITLE = 'Helvetica-Bold'
    FONT_BODY = 'Helvetica'
    FONT_BODY_BOLD = 'Helvetica-Bold'
    FONT_SIGNATURE = 'Times-Italic'


# Default Colors
class DefaultColors:
    """Default color values"""

    PRIMARY = '#9DB5A5'  # Soft green
    SECONDARY = '#C8B8D8'  # Soft lavender
    TEXT = '#1f2937'  # Dark gray


# File Paths
class FilePaths:
    """Default file paths"""

    LOGOS_DIR = 'Logos'
    CERTIFICATES_DIR = 'certificados'
    DEFAULT_LOGO = 'Logos/ana_rita_m&w_logo_trnsp.png'


# Email Configuration
class EmailConfig:
    """Email service configuration"""

    SMTP_SERVER_DEFAULT = 'smtp.gmail.com'
    SMTP_PORT_DEFAULT = 587
    TIMEOUT_SECONDS = 30
