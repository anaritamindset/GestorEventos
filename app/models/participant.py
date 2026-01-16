"""
Participant model
"""

from app import db
from datetime import datetime

class Participant(db.Model):
    """Participant in an event"""
    __tablename__ = 'participants'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, index=True)

    # Event relationship
    evento_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    evento = db.relationship('Event', back_populates='participantes')

    # Status: pendente, confirmado, presente, ausente, cancelado
    status = db.Column(db.String(20), default='pendente', nullable=False)

    # Certificate
    certificado_gerado = db.Column(db.Boolean, default=False, nullable=False)
    certificado_enviado = db.Column(db.Boolean, default=False, nullable=False)
    certificado_path = db.Column(db.String(255), nullable=True)
    data_envio_certificado = db.Column(db.DateTime, nullable=True)

    # Additional info
    telefone = db.Column(db.String(20), nullable=True)
    empresa = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)

    # Check-in/out
    checkin_at = db.Column(db.DateTime, nullable=True)
    checkout_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('email', 'evento_id', name='_email_evento_uc'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'evento_id': self.evento_id,
            'status': self.status,
            'certificado_gerado': self.certificado_gerado,
            'certificado_enviado': self.certificado_enviado,
            'data_envio_certificado': self.data_envio_certificado.isoformat() if self.data_envio_certificado else None,
            'telefone': self.telefone,
            'empresa': self.empresa,
            'observacoes': self.observacoes,
            'checkin_at': self.checkin_at.isoformat() if self.checkin_at else None,
            'checkout_at': self.checkout_at.isoformat() if self.checkout_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Participant {self.nome} - Event {self.evento_id}>'
