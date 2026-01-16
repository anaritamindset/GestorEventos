"""
Audit Log model for tracking all system actions
"""

from app import db
from datetime import datetime

class AuditLog(db.Model):
    """Audit trail for all system actions"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)

    # Who performed the action
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    user = db.relationship('User', backref='audit_logs')
    user_email = db.Column(db.String(100), nullable=True)  # Backup if user deleted

    # What action
    action = db.Column(db.String(50), nullable=False, index=True)
    # actions: create, update, delete, login, logout, generate_certificate, send_email, etc.

    # Which entity
    entity_type = db.Column(db.String(50), nullable=False, index=True)
    # entity_types: event, participant, user, certificate, etc.
    entity_id = db.Column(db.Integer, nullable=True, index=True)

    # Details
    details = db.Column(db.JSON, nullable=True)
    # JSON with before/after states, additional info

    # Request info
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.entity_type}>'
