"""
Email Service - Send certificates and notifications
GestorEventos v2.0
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Optional, List


class EmailService:
    """Service to send emails with certificates"""

    def __init__(self):
        """Initialize email service with credentials from environment"""
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')

        if not self.email_user or not self.email_password:
            raise ValueError(
                "Email credentials not found in environment variables. "
                "Please set EMAIL_USER and EMAIL_PASSWORD in .env file."
            )

    def send_certificate(
        self,
        recipient_email: str,
        recipient_name: str,
        event_name: str,
        certificate_path: str
    ) -> bool:
        """
        Send certificate via email

        Args:
            recipient_email: Email address of the recipient
            recipient_name: Name of the recipient
            event_name: Name of the event
            certificate_path: Path to the certificate PDF file

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = recipient_email
            msg['Subject'] = f"Certificado de Participação - {event_name}"

            # Email body
            body = f"""
Olá {recipient_name},

Segue em anexo o seu certificado de participação no evento "{event_name}".

Agradecemos a sua presença e participação!

Atenciosamente,
Mindset Wellness
Ana Rita

---
Este é um email automático. Por favor não responda.
            """.strip()

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Attach certificate PDF
            if os.path.exists(certificate_path):
                with open(certificate_path, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    pdf_attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=f'Certificado_{recipient_name}.pdf'
                    )
                    msg.attach(pdf_attachment)
            else:
                print(f"WARNING: Certificate file not found: {certificate_path}")
                return False

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)

            print(f"✓ Certificate sent successfully to {recipient_email}")
            return True

        except Exception as e:
            print(f"ERROR sending email to {recipient_email}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def send_bulk_certificates(
        self,
        recipients: List[dict]
    ) -> dict:
        """
        Send certificates to multiple recipients

        Args:
            recipients: List of dicts with keys: email, name, event_name, certificate_path

        Returns:
            dict: {'sent': int, 'failed': int, 'errors': list}
        """
        sent = 0
        failed = 0
        errors = []

        for recipient in recipients:
            try:
                success = self.send_certificate(
                    recipient_email=recipient['email'],
                    recipient_name=recipient['name'],
                    event_name=recipient['event_name'],
                    certificate_path=recipient['certificate_path']
                )

                if success:
                    sent += 1
                else:
                    failed += 1
                    errors.append(f"Failed to send to {recipient['email']}")

            except Exception as e:
                failed += 1
                errors.append(f"{recipient['email']}: {str(e)}")

        return {
            'sent': sent,
            'failed': failed,
            'errors': errors
        }
