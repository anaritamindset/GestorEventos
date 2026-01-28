"""
Event model with enhanced features
"""

from app import db
from datetime import datetime

class Event(db.Model):
    """
    Event model with support for multi-day events and recurring events
    """
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)

    # Organization (multi-tenant support)
    organizacao_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True, index=True)
    organizacao = db.relationship('Organization', back_populates='eventos')

    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    # Dates
    data_inicio = db.Column(db.Date, nullable=False, index=True)
    data_fim = db.Column(db.Date, nullable=True)
    duracao_minutos = db.Column(db.Integer, nullable=False)

    # Event details
    local = db.Column(db.String(200), nullable=True)
    formadora = db.Column(db.String(100), nullable=True)
    tipo_evento = db.Column(db.String(50), default='formacao', nullable=False)
    # tipos: formacao, workshop, conferencia, reuniao, webinar

    # Status
    status = db.Column(db.String(20), default='planejado', nullable=False)
    # status: planejado, em_andamento, concluido, cancelado

    # Capacity
    capacidade_maxima = db.Column(db.Integer, nullable=True)

    # Certificate template
    template_id = db.Column(db.Integer, db.ForeignKey('certificate_templates.id'), nullable=True)
    template = db.relationship('CertificateTemplate', backref='events')

    # Google Integration
    google_form_id = db.Column(db.String(200), nullable=True)
    google_form_url = db.Column(db.String(500), nullable=True)
    google_sheet_id = db.Column(db.String(200), nullable=True)
    google_sheet_url = db.Column(db.String(500), nullable=True)

    # Relationships
    participantes = db.relationship('Participant', back_populates='evento', cascade='all, delete-orphan', lazy='dynamic')

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Created by
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    creator = db.relationship('User', backref='eventos_criados')

    def get_participant_count(self):
        """Get total number of participants"""
        return self.participantes.count()

    def get_confirmed_count(self):
        """Get number of confirmed participants"""
        return self.participantes.filter_by(status='confirmado').count()

    def get_certificate_count(self):
        """Get number of certificates generated"""
        return self.participantes.filter_by(certificado_gerado=True).count()

    def is_full(self):
        """Check if event is at capacity"""
        if self.capacidade_maxima:
            return self.get_participant_count() >= self.capacidade_maxima
        return False

    def to_dict(self, include_participants=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'duracao_minutos': self.duracao_minutos,
            'local': self.local,
            'formadora': self.formadora,
            'tipo_evento': self.tipo_evento,
            'status': self.status,
            'capacidade_maxima': self.capacidade_maxima,
            'total_participantes': self.get_participant_count(),
            'participantes_confirmados': self.get_confirmed_count(),
            'certificados_gerados': self.get_certificate_count(),
            'lotado': self.is_full(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_participants:
            data['participantes'] = [p.to_dict() for p in self.participantes.all()]

        return data

    def __repr__(self):
        return f'<Event {self.nome}>'
