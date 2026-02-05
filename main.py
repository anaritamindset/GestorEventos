"""
Main entry point for Google App Engine and Cloud Run deployment.
This file is required by App Engine/Cloud Run to run the Flask application.
"""

import os
import fcntl
from app import create_app, db
from app.models.organization import Organization

# Create the Flask application instance
app = create_app()

def init_database():
    """Initialize database with tables and seed data."""
    # Use file-based lock for multi-process synchronization
    lock_file = '/tmp/.db_init.lock'

    try:
        with open(lock_file, 'w') as f:
            # Acquire exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)

            try:
                # Check if already initialized
                org = Organization.query.first()
                if org:
                    return  # Already initialized
            except Exception:
                pass

            # Create tables (safe - won't fail if tables exist)
            print("Creating database tables...")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            if not existing_tables:
                db.create_all()

            # Check if organizations need to be seeded
            try:
                org_count = Organization.query.count()
                if org_count == 0:
                    print("Seeding organizations...")
                    from seed_organizations import seed_organizations
                    seed_organizations()
            except Exception:
                # Table might not exist yet, create all and seed
                db.create_all()
                print("Seeding organizations...")
                from seed_organizations import seed_organizations
                seed_organizations()

            print("Database initialized successfully!")

    except Exception as e:
        print(f"Database init warning: {e}")

# Run initialization once
with app.app_context():
    init_database()

if __name__ == '__main__':
    # This is used when running locally
    app.run(host='0.0.0.0', port=8080)
