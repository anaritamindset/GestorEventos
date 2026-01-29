"""
Main entry point for Google App Engine and Cloud Run deployment.
This file is required by App Engine/Cloud Run to run the Flask application.
"""

import os
from app import create_app, db
from app.models.organization import Organization

# Create the Flask application instance
app = create_app()

# Initialize database on first run (for Cloud Run with ephemeral filesystem)
# Use a file lock to prevent race conditions between workers
import threading
_init_lock = threading.Lock()

def init_database():
    """Initialize database with tables and seed data."""
    with _init_lock:
        # Check if already initialized
        try:
            Organization.query.first()
            return  # Already initialized
        except Exception:
            pass

        # Create tables
        print("Creating database tables...")
        db.create_all()

        # Import and run seed data
        print("Seeding organizations...")
        from seed_organizations import seed_organizations
        seed_organizations()
        print("Database initialized successfully!")

# Run initialization once
with app.app_context():
    init_database()

if __name__ == '__main__':
    # This is used when running locally
    app.run(host='0.0.0.0', port=8080)
