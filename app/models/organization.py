"""
Organization model for multi-tenant support
"""

from app import db
from datetime import datetime

class Organization(db.Model):
    """
    Organization/Client model for multi-tenant architecture
    Each organization has its own events, participants, and certificate templates
    """
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)
    descricao = db.Column(db.Text, nullable=True)

    # Visual identity
    cor_primaria = db.Column(db.String(7), default='#9DB5A5')  # Hex color
    cor_secundaria = db.Column(db.String(7), default='#C8B8D8')  # Hex color
    logo_path = db.Column(db.String(500), nullable=True)
    icone = db.Column(db.String(10), default='🌿')  # Emoji icon

    # Contact information
    email = db.Column(db.String(120), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    website = db.Column(db.String(200), nullable=True)

    # Certificate settings
    assinatura_nome = db.Column(db.String(100), nullable=True)  # Nome para assinatura nos certificados
    assinatura_cargo = db.Column(db.String(100), nullable=True)  # Cargo para assinatura

    # Status
    ativa = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    eventos = db.relationship('Event', back_populates='organizacao', cascade='all, delete-orphan', lazy='dynamic')
    templates = db.relationship('CertificateTemplate', back_populates='organizacao', cascade='all, delete-orphan', lazy='dynamic')

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Organization {self.nome}>'

    @property
    def total_eventos(self):
        """Total number of active events"""
        return self.eventos.filter_by(deleted_at=None).count()

    @property
    def total_participantes(self):
        """Total number of participants across all events"""
        from app.models.participant import Participant
        total = 0
        for evento in self.eventos.filter_by(deleted_at=None):
            total += evento.participantes.filter_by(deleted_at=None).count()
        return total
