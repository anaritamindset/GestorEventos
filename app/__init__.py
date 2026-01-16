"""
GestorEventos v2.0 - Event Management System
Modern Flask application with RESTful API
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    """Application factory pattern"""
    # Base directory
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Initialize Flask with custom template and static folders
    template_dir = os.path.join(basedir, 'templates')
    static_dir = os.path.join(basedir, 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "gestorev2.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
    app.config['JSON_AS_ASCII'] = False  # Support PT-PT characters

    # Upload configurations
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

    # Email configurations
    app.config['EMAIL_USER'] = os.environ.get('EMAIL_USER', '')
    app.config['EMAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD', '')
    app.config['SMTP_SERVER'] = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    app.config['SMTP_PORT'] = int(os.environ.get('SMTP_PORT', 587))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Create upload folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(basedir, 'certificados'), exist_ok=True)

    # Register API blueprints
    from app.api.routes import events, participants, users, certificates, gdrive
    app.register_blueprint(events.bp)
    app.register_blueprint(participants.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(certificates.bp)
    app.register_blueprint(gdrive.bp)

    # Register frontend blueprint (main - beautiful v1 frontend)
    from app.api.routes import main
    app.register_blueprint(main.bp)

    # Register web blueprint (API info routes)
    from app.api.routes import web
    app.register_blueprint(web.bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Recurso não encontrado'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Erro interno do servidor'}, 500

    # Context processor for templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    return app
