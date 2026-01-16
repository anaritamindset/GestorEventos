"""
Participants API endpoints
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models import Participant, Event
from datetime import datetime

bp = Blueprint('participants', __name__, url_prefix='/api/participants')

@bp.route('/<int:participant_id>', methods=['GET'])
def get_participant(participant_id):
    """Get single participant"""
    try:
        participant = Participant.query.get_or_404(participant_id)
        if participant.deleted_at:
            return jsonify({'error': 'Participante não encontrado'}), 404
        return jsonify(participant.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/event/<int:event_id>', methods=['POST'])
def add_participant(event_id):
    """Add participant to event"""
    try:
        event = Event.query.get_or_404(event_id)
        if event.deleted_at:
            return jsonify({'error': 'Evento não encontrado'}), 404

        data = request.get_json()

        # Check if already exists
        existing = Participant.query.filter_by(
            email=data['email'],
            evento_id=event_id,
            deleted_at=None
        ).first()

        if existing:
            return jsonify({'error': 'Participante já está inscrito neste evento'}), 400

        participant = Participant(
            nome=data['nome'],
            email=data['email'],
            evento_id=event_id,
            telefone=data.get('telefone'),
            empresa=data.get('empresa'),
            observacoes=data.get('observacoes'),
            status=data.get('status', 'pendente')
        )

        db.session.add(participant)
        db.session.commit()

        return jsonify(participant.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:participant_id>/checkin', methods=['POST'])
def checkin(participant_id):
    """Check-in participant"""
    try:
        participant = Participant.query.get_or_404(participant_id)
        if participant.deleted_at:
            return jsonify({'error': 'Participante não encontrado'}), 404

        participant.checkin_at = datetime.utcnow()
        participant.status = 'presente'
        db.session.commit()

        return jsonify(participant.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:participant_id>', methods=['DELETE'])
def delete_participant(participant_id):
    """Soft delete participant"""
    try:
        participant = Participant.query.get_or_404(participant_id)
        if participant.deleted_at:
            return jsonify({'error': 'Participante já foi removido'}), 404

        participant.deleted_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': 'Participante removido com sucesso'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
