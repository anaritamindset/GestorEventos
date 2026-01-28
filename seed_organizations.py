#!/usr/bin/env python3
"""
Script para criar as organizações iniciais: Ana Rita e ARdaTerra
Executar: python seed_organizations.py
"""

from app import create_app, db
from app.models import Organization
from datetime import datetime

def seed_organizations():
    """Cria as organizações iniciais"""

    app = create_app()

    with app.app_context():
        print("=" * 60)
        print("🌿 Criando Organizações Iniciais")
        print("=" * 60)

        # Verificar se já existem organizações
        existing = Organization.query.count()
        if existing > 0:
            print(f"\n⚠️  Já existem {existing} organizações na base de dados.")
            resposta = input("Deseja continuar mesmo assim? (s/N): ")
            if resposta.lower() != 's':
                print("❌ Operação cancelada.")
                return

        # Organização 1: Ana Rita - Mindset & Wellness
        print("\n1️⃣  Criando: Ana Rita - Mindset & Wellness")

        ana_rita = Organization.query.filter_by(slug='ana-rita-mindset-wellness').first()
        if not ana_rita:
            ana_rita = Organization(
                nome='Ana Rita - Mindset & Wellness',
                slug='ana-rita-mindset-wellness',
                descricao='Eventos de mindfulness, workshops de bem-estar e sessões de desenvolvimento pessoal',
                cor_primaria='#9DB5A5',  # Verde suave
                cor_secundaria='#C8B8D8',  # Lilás suave
                logo_path='Logos/ana_rita_m&w_logo_trnsp.png',
                icone='🧘',
                email='anarita@mindsetwellness.com',
                smtp_email='anaritamindset@gmail.com',
                smtp_password='mrll wqhc gzor xwfg',
                smtp_server='smtp.gmail.com',
                smtp_port=587,
                assinatura_nome='Ana Rita Vieira',
                assinatura_cargo='Mindset & Wellness',
                ativa=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(ana_rita)
            print("   ✅ Organização criada")
        else:
            # Update existing organization with SMTP credentials
            ana_rita.smtp_email = 'anaritamindset@gmail.com'
            ana_rita.smtp_password = 'mrll wqhc gzor xwfg'
            ana_rita.smtp_server = 'smtp.gmail.com'
            ana_rita.smtp_port = 587
            ana_rita.updated_at = datetime.utcnow()
            print("   ℹ️  Organização já existe - credenciais SMTP atualizadas")

        # Organização 2: ARdaTerra
        print("\n2️⃣  Criando: ARdaTerra")

        ardaterra = Organization.query.filter_by(slug='ardaterra').first()
        if not ardaterra:
            ardaterra = Organization(
                nome='ARdaTerra',
                slug='ardaterra',
                descricao='Eventos de aromaterapia, workshops de óleos essenciais e experiências naturais',
                cor_primaria='#8B9D7C',  # Verde terra
                cor_secundaria='#D4A574',  # Castanho dourado
                logo_path='Logos/ardaterra_logo.png',
                icone='🌿',
                email='contacto@ardaterra.pt',
                smtp_email='contacto@ardaterra.pt',
                smtp_password='xxxx xxxx xxxx xxxx',  # NOTA: Substituir pela app password real
                smtp_server='smtp.gmail.com',
                smtp_port=587,
                assinatura_nome='ARdaTerra',
                assinatura_cargo='Aromaterapia & Natureza',
                ativa=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(ardaterra)
            print("   ✅ Organização criada")
            print("   ⚠️  ATENÇÃO: Adicionar app password real da ARdaTerra após configurar na Google")
        else:
            # Update existing organization with SMTP credentials
            ardaterra.smtp_email = 'contacto@ardaterra.pt'
            ardaterra.smtp_password = 'xxxx xxxx xxxx xxxx'  # NOTA: Substituir pela app password real
            ardaterra.smtp_server = 'smtp.gmail.com'
            ardaterra.smtp_port = 587
            ardaterra.updated_at = datetime.utcnow()
            print("   ℹ️  Organização já existe - credenciais SMTP atualizadas")
            print("   ⚠️  ATENÇÃO: Adicionar app password real da ARdaTerra após configurar na Google")

        # Commit
        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print("✅ DADOS INICIAIS CRIADOS COM SUCESSO!")
            print("=" * 60)

            # Mostrar resumo
            print("\n📊 Resumo:")
            print(f"   • Ana Rita - Mindset & Wellness (ID: {ana_rita.id if ana_rita else 'N/A'})")
            print(f"   • ARdaTerra (ID: {ardaterra.id if ardaterra else 'N/A'})")

            print("\n🔄 Próximos passos:")
            print("   1. Associar eventos existentes às organizações")
            print("   2. Criar rotas específicas para cada organização")
            print("   3. Testar acesso através do menu principal")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro ao criar organizações: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    seed_organizations()
