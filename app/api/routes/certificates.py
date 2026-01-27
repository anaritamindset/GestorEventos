"""
Certificates API endpoints
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from app import db
from app.models import Participant, Event
from app.services.certificate_service import CertificateService
import logging
import os

logger = logging.getLogger(__name__)
bp = Blueprint('certificates', __name__, url_prefix='/api/certificates')

# Initialize certificate service
cert_service = CertificateService()


@bp.route('/generate/<int:participant_id>', methods=['POST'])
def generate_certificate(participant_id):
    """Generate certificate for participant"""
    try:
        participant = Participant.query.get_or_404(participant_id)

        if participant.deleted_at:
            return jsonify({'error': 'Participante não encontrado'}), 404

        # Get optional parameters
        data = request.get_json() if request.is_json else {}
        template_id = data.get('template_id')

        # Generate certificate
        filepath = cert_service.generate_certificate(
            participant_id=participant_id,
            template_id=template_id
        )

        # Update participant record
        participant.certificado_gerado = True
        participant.certificado_path = filepath
        db.session.commit()

        logger.info(f"Certificate generated for participant {participant_id}: {filepath}")

        return jsonify({
            'message': 'Certificado gerado com sucesso',
            'participant': participant.to_dict(),
            'certificate_path': filepath
        }), 200

    except Exception as e:
        logger.error(f"Error generating certificate: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/generate/event/<int:event_id>', methods=['POST'])
def generate_event_certificates(event_id):
    """Generate certificates for all participants in an event"""
    try:
        event = Event.query.get_or_404(event_id)

        if event.deleted_at:
            return jsonify({'error': 'Evento não encontrado'}), 404

        # Get optional parameters
        data = request.get_json() if request.is_json else {}
        template_id = data.get('template_id')

        # Batch generate certificates
        stats = cert_service.batch_generate_certificates(
            event_id=event_id,
            template_id=template_id
        )

        logger.info(f"Batch certificate generation for event {event_id}: {stats}")

        return jsonify({
            'message': f'Geração em lote concluída: {stats["generated"]} certificados gerados',
            'stats': stats
        }), 200

    except Exception as e:
        logger.error(f"Error in batch generation: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/download/<int:participant_id>', methods=['GET'])
def download_certificate(participant_id):
    """Download certificate PDF"""
    try:
        participant = Participant.query.get_or_404(participant_id)

        if participant.deleted_at:
            return jsonify({'error': 'Participante não encontrado'}), 404

        if not participant.certificado_gerado or not participant.certificado_path:
            return jsonify({'error': 'Certificado ainda não foi gerado'}), 404

        # Check if file exists
        if not os.path.exists(participant.certificado_path):
            return jsonify({'error': 'Ficheiro de certificado não encontrado'}), 404

        # Send file
        return send_file(
            participant.certificado_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'certificado_{participant.nome.replace(" ", "_")}.pdf'
        )

    except Exception as e:
        logger.error(f"Error downloading certificate: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/validate/<int:participant_id>', methods=['GET'])
def validate_certificate(participant_id):
    """Validate certificate via QR code"""
    try:
        participant = Participant.query.get_or_404(participant_id)

        if participant.deleted_at:
            return jsonify({'error': 'Participante não encontrado', 'valid': False}), 404

        if not participant.certificado_gerado:
            return jsonify({'error': 'Certificado não foi gerado', 'valid': False}), 404

        event = Event.query.get(participant.evento_id)

        return jsonify({
            'valid': True,
            'participant': {
                'nome': participant.nome,
                'email': participant.email,
            },
            'event': {
                'nome': event.nome,
                'data_inicio': event.data_inicio.isoformat() if event.data_inicio else None,
                'duracao_horas': event.duracao_horas,
            },
            'certificate_generated': participant.certificado_gerado,
            'certificate_sent': participant.certificado_enviado
        }), 200

    except Exception as e:
        logger.error(f"Error validating certificate: {e}")
        return jsonify({'error': str(e), 'valid': False}), 500


@bp.route('/send/<int:participant_id>', methods=['POST'])
def send_certificate(participant_id):
    """Send certificate via email"""
    try:
        participant = Participant.query.get_or_404(participant_id)

        if participant.deleted_at:
            return jsonify({'error': 'Participante não encontrado'}), 404

        if not participant.certificado_gerado:
            return jsonify({'error': 'Certificado ainda não foi gerado'}), 400

        # TODO: Implement actual email sending logic
        # For now, just mark as sent
        participant.certificado_enviado = True
        from datetime import datetime
        participant.data_envio_certificado = datetime.utcnow()
        db.session.commit()

        logger.info(f"Certificate marked as sent for participant {participant_id}")

        return jsonify({
            'message': 'Certificado enviado com sucesso',
            'participant': participant.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error sending certificate: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
