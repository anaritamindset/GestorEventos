"""
Users API endpoints
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models import User

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/', methods=['GET'])
def list_users():
    """List all users (admin only)"""
    try:
        users = User.query.filter(User.deleted_at.is_(None)).all()
        return jsonify({
            'users': [u.to_dict() for u in users]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get single user"""
    try:
        user = User.query.get_or_404(user_id)
        if user.deleted_at:
            return jsonify({'error': 'Utilizador não encontrado'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
def create_user():
    """Create new user (admin only)"""
    try:
        data = request.get_json()

        # Check if email already exists
        existing = User.query.filter_by(email=data['email']).first()
        if existing and not existing.deleted_at:
            return jsonify({'error': 'Email já está em uso'}), 400

        user = User(
            nome_completo=data['nome_completo'],
            email=data['email'],
            role=data.get('role', 'viewer'),
            is_active=data.get('is_active', True)
        )

        if 'password' in data:
            user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify(user.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
