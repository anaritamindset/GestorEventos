"""
Events API endpoints
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models import Event, Participant
from datetime import datetime

bp = Blueprint('events', __name__, url_prefix='/api/events')

@bp.route('/', methods=['GET'])
def list_events():
    """List all events with optional filtering"""
    try:
        # Query parameters
        status = request.args.get('status')
        tipo = request.args.get('tipo')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        # Build query
        query = Event.query.filter(Event.deleted_at.is_(None))

        if status:
            query = query.filter_by(status=status)
        if tipo:
            query = query.filter_by(tipo_evento=tipo)

        # Paginate
        events = query.order_by(Event.data_inicio.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'events': [e.to_dict() for e in events.items],
            'total': events.total,
            'pages': events.pages,
            'current_page': page
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get single event by ID"""
    try:
        event = Event.query.get_or_404(event_id)

        if event.deleted_at:
            return jsonify({'error': 'Evento não encontrado'}), 404

        include_participants = request.args.get('include_participants', 'false').lower() == 'true'
        return jsonify(event.to_dict(include_participants=include_participants)), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
def create_event():
    """Create new event"""
    try:
        data = request.get_json()

        # Validate required fields
        required = ['nome', 'data_inicio', 'duracao_horas']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400

        # Parse dates
        data_inicio = datetime.fromisoformat(data['data_inicio'].replace('Z', '+00:00')).date()
        data_fim = None
        if 'data_fim' in data and data['data_fim']:
            data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00')).date()

        # Create event
        event = Event(
            nome=data['nome'],
            descricao=data.get('descricao'),
            data_inicio=data_inicio,
            data_fim=data_fim,
            duracao_horas=data['duracao_horas'],
            local=data.get('local'),
            formadora=data.get('formadora'),
            tipo_evento=data.get('tipo_evento', 'formacao'),
            status=data.get('status', 'planejado'),
            capacidade_maxima=data.get('capacidade_maxima'),
            template_id=data.get('template_id'),
        )

        db.session.add(event)
        db.session.commit()

        return jsonify(event.to_dict()), 201

    except ValueError as e:
        return jsonify({'error': f'Data inválida: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update event"""
    try:
        event = Event.query.get_or_404(event_id)

        if event.deleted_at:
            return jsonify({'error': 'Evento não encontrado'}), 404

        data = request.get_json()

        # Update fields
        if 'nome' in data:
            event.nome = data['nome']
        if 'descricao' in data:
            event.descricao = data['descricao']
        if 'data_inicio' in data:
            event.data_inicio = datetime.fromisoformat(data['data_inicio'].replace('Z', '+00:00')).date()
        if 'data_fim' in data:
            event.data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00')).date() if data['data_fim'] else None
        if 'duracao_horas' in data:
            event.duracao_horas = data['duracao_horas']
        if 'local' in data:
            event.local = data['local']
        if 'formadora' in data:
            event.formadora = data['formadora']
        if 'tipo_evento' in data:
            event.tipo_evento = data['tipo_evento']
        if 'status' in data:
            event.status = data['status']
        if 'capacidade_maxima' in data:
            event.capacidade_maxima = data['capacidade_maxima']
        if 'template_id' in data:
            event.template_id = data['template_id']

        db.session.commit()
        return jsonify(event.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Soft delete event"""
    try:
        event = Event.query.get_or_404(event_id)

        if event.deleted_at:
            return jsonify({'error': 'Evento já foi apagado'}), 404

        # Soft delete
        event.deleted_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': 'Evento apagado com sucesso'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:event_id>/stats', methods=['GET'])
def event_stats(event_id):
    """Get event statistics"""
    try:
        event = Event.query.get_or_404(event_id)

        if event.deleted_at:
            return jsonify({'error': 'Evento não encontrado'}), 404

        stats = {
            'event_id': event.id,
            'event_name': event.nome,
            'total_participantes': event.get_participant_count(),
            'confirmados': event.get_confirmed_count(),
            'certificados_gerados': event.get_certificate_count(),
            'capacidade_maxima': event.capacidade_maxima,
            'lotado': event.is_full(),
            'taxa_confirmacao': round(event.get_confirmed_count() / max(event.get_participant_count(), 1) * 100, 2),
        }

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
