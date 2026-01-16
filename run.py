"""
GestorEventos v2.0 - Entry Point
Modern Event Management System
"""

import os
from app import create_app, db
from app.models import User, Event, Participant, CertificateTemplate, AuditLog

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make shell context for flask shell command"""
    return {
        'db': db,
        'User': User,
        'Event': Event,
        'Participant': Participant,
        'CertificateTemplate': CertificateTemplate,
        'AuditLog': AuditLog,
    }

@app.cli.command()
def init_db():
    """Initialize the database with default data"""
    with app.app_context():
        # Create tables
        db.create_all()
        print("Database tables created!")

        # Create default admin user
        admin = User.query.filter_by(email='admin@gestorev2.local').first()
        if not admin:
            admin = User(
                nome_completo='Administrador',
                email='admin@gestorev2.local',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created: {admin.email} / admin123")
        else:
            print("Admin user already exists")

        # Create default certificate template
        default_template = CertificateTemplate.query.filter_by(nome='Padrão').first()
        if not default_template:
            default_template = CertificateTemplate(
                nome='Padrão',
                descricao='Template padrão de certificado',
                config={
                    'font_title': 'Helvetica-Bold',
                    'font_body': 'Helvetica',
                    'color_title': '#1a1a1a',
                    'color_body': '#333333',
                    'logo_position': {'x': 50, 'y': 750},
                    'signature_position': {'x': 300, 'y': 150},
                },
                is_active=True,
                is_default=True,
                created_by=admin.id
            )
            db.session.add(default_template)
            db.session.commit()
            print("Default certificate template created!")
        else:
            print("Default template already exists")

        print("\nDatabase initialized successfully!")
        print("You can now run: python run.py")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True') == 'True'

    print("="*60)
    print("GestorEventos v2.0 - Event Management System")
    print("="*60)
    print(f"Server running on: http://127.0.0.1:{port}")
    print(f"Debug mode: {debug}")
    print("="*60)

    app.run(host='127.0.0.1', port=port, debug=debug)
