"""
Web routes (HTML pages)
"""

from flask import Blueprint, render_template, jsonify
from app.models import Event, Participant, User

bp = Blueprint('web', __name__)

@bp.route('/api')
def api_info():
    """API info"""
    return jsonify({
        'app': 'GestorEventos v2.0',
        'version': '2.0.0',
        'status': 'running',
        'endpoints': {
            'events': '/api/events',
            'participants': '/api/participants',
            'users': '/api/users',
            'certificates': '/api/certificates'
        }
    })


@bp.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy'}), 200


@bp.route('/stats')
def stats():
    """System statistics"""
    try:
        total_events = Event.query.filter(Event.deleted_at.is_(None)).count()
        total_participants = Participant.query.filter(Participant.deleted_at.is_(None)).count()
        total_users = User.query.filter(User.deleted_at.is_(None)).count()

        return jsonify({
            'total_events': total_events,
            'total_participants': total_participants,
            'total_users': total_users,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
