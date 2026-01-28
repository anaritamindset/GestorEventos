"""
Certificate Template model for customizable certificates
"""

from app import db
from datetime import datetime

class CertificateTemplate(db.Model):
    """Customizable certificate templates"""
    __tablename__ = 'certificate_templates'

    id = db.Column(db.Integer, primary_key=True)

    # Organization (multi-tenant support)
    organizacao_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True, index=True)
    organizacao = db.relationship('Organization', back_populates='templates')

    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    # Template configuration (JSON)
    config = db.Column(db.JSON, nullable=False)
    # config includes: fonts, colors, positions, logo_path, signature_path, etc.

    # Active status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    creator = db.relationship('User', backref='templates_criados')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'config': self.config,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<CertificateTemplate {self.nome}>'
