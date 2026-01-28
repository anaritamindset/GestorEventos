from app import create_app, db
from app.models import Organization

app = create_app()

with app.app_context():
    orgs = Organization.query.all()
    print(f"Total organizations: {len(orgs)}")
    for org in orgs:
        print(f"ID: {org.id}, Nome: {org.nome}, Ativa: {org.ativa}")
