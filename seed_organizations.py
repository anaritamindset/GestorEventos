#!/usr/bin/env python3
"""
Script para gerir e configurar as organizações.
Edite este ficheiro para alterar os detalhes das organizações e execute-o para aplicar as alterações.

Executar: python seed_organizations.py

Funcionalidades:
- Cria novas organizações se não existirem
- Atualiza organizações existentes (sincronização)
- Valida dados essenciais (email, logos, cores)
- Mostra relatório detalhado das alterações
"""

import os
import sys
from dotenv import load_dotenv
from app import create_app, db
from app.models import Organization
from datetime import datetime

# Carregar variáveis de ambiente do .env
load_dotenv()

# ==========================================
# ⚙️ CONFIGURAÇÃO DAS ORGANIZAÇÕES
# ==========================================
ORGANIZATIONS_CONFIG = [
    {
        'slug': 'ana-rita-mindset-wellness',
        'data': {
            # Informação básica
            'nome': 'Ana Rita',
            'subtitulo': 'Mindset & Wellness',
            'descricao': 'Eventos de mindfulness, workshops de bem-estar e sessões de desenvolvimento pessoal',
            'icone': '🧘',
            'ativa': True,

            # Branding - Cores
            'cor_primaria': '#9DB5A5',  # Verde suave
            'cor_secundaria': '#C8B8D8',  # Lilás suave

            # Branding - Logos e imagens
            'logo_path': 'Logos/ana_rita_m&w_logo_trnsp.png',
            'seal_logo_path': 'Logos/Lacre - Ana Rita M&W.png',

            # Contactos
            'email': 'anarita@mindsetwellness.com',

            # Configuração SMTP para envio de emails
            'smtp_email': 'anaritamindset@gmail.com',
            'smtp_password': os.getenv('EMAIL_PASSWORD', 'mrll wqhc gzor xwfg'),
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,

            # Assinatura para certificados
            'assinatura_nome': 'Ana Rita Vieira',
            'assinatura_cargo': 'Mindset & Wellness'
        }
    },
    {
        'slug': 'ardaterra',
        'data': {
            # Informação básica
            'nome': 'ARdaTerra',
            'subtitulo': 'Óleos Essenciais',
            'descricao': 'Eventos de aromaterapia, workshops de óleos essenciais e experiências naturais',
            'icone': '🌿',
            'ativa': True,

            # Branding - Cores
            'cor_primaria': '#8B9D7C',  # Verde terra
            'cor_secundaria': '#D4A574',  # Castanho dourado

            # Branding - Logos e imagens
            'logo_path': 'Logos/ARdaTerra_logo.png',
            'seal_logo_path': 'Logos/Lacre - ARdaTerra.png',

            # Contactos
            'email': 'ardoterra@gmail.com',

            # Configuração SMTP para envio de emails
            'smtp_email': os.getenv('ARDATERRA_EMAIL', 'ardoterra@gmail.com'),
            'smtp_password': os.getenv('ARDATERRA_PASSWORD'),
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,

            # Assinatura para certificados
            'assinatura_nome': 'ARdaTerra',
            'assinatura_cargo': 'Óleos Essenciais'
        }
    }
]

def validate_file_exists(filepath, file_type="arquivo"):
    """Valida se um ficheiro existe no sistema"""
    if not filepath:
        return False, f"{file_type} não definido"

    if os.path.exists(filepath):
        return True, f"{file_type} encontrado"
    else:
        return False, f"{file_type} não encontrado: {filepath}"


def validate_organization_data(slug, data):
    """Valida os dados de uma organização e retorna lista de avisos/erros"""
    warnings = []
    errors = []

    # Validações obrigatórias
    required_fields = ['nome', 'email', 'smtp_email', 'smtp_password']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Campo obrigatório ausente: {field}")

    # Validar password SMTP
    if not data.get('smtp_password'):
        errors.append("Password SMTP não configurada (variável de ambiente?)")

    # Validar cores (formato hex)
    for color_field in ['cor_primaria', 'cor_secundaria']:
        color = data.get(color_field)
        if color and not (color.startswith('#') and len(color) == 7):
            warnings.append(f"{color_field} com formato inválido: {color}")

    # Validar ficheiros
    if data.get('logo_path'):
        exists, msg = validate_file_exists(data['logo_path'], "Logo principal")
        if not exists:
            warnings.append(msg)
    else:
        warnings.append("Logo principal não definido")

    if data.get('seal_logo_path'):
        exists, msg = validate_file_exists(data['seal_logo_path'], "Logo lacre")
        if not exists:
            warnings.append(msg)
    else:
        warnings.append("Logo lacre não definido")

    return errors, warnings


def seed_organizations():
    """Sincroniza as organizações definidas acima com a base de dados"""

    app = create_app()

    with app.app_context():
        print("\n" + "=" * 70)
        print(" " * 20 + "🌿 GESTOR DE ORGANIZAÇÕES")
        print("=" * 70)
        print(f"Total de organizações a processar: {len(ORGANIZATIONS_CONFIG)}")
        print("=" * 70)

        updated_count = 0
        created_count = 0
        warnings_count = 0
        errors_count = 0

        for org_config in ORGANIZATIONS_CONFIG:
            slug = org_config['slug']
            data = org_config['data']

            print(f"\n📍 {data['nome']} (slug: {slug})")
            print("-" * 70)

            # Validate data
            errors, warnings = validate_organization_data(slug, data)

            if errors:
                print("   ❌ ERROS CRÍTICOS:")
                for error in errors:
                    print(f"      • {error}")
                errors_count += len(errors)
                print("   ⚠️  Organização NÃO será processada devido a erros críticos!")
                continue

            if warnings:
                print("   ⚠️  AVISOS:")
                for warning in warnings:
                    print(f"      • {warning}")
                warnings_count += len(warnings)

            # Process organization
            org = Organization.query.filter_by(slug=slug).first()

            if not org:
                # Create new
                org = Organization(slug=slug)
                for key, value in data.items():
                    setattr(org, key, value)

                org.created_at = datetime.utcnow()
                org.updated_at = datetime.utcnow()

                db.session.add(org)
                created_count += 1
                print("   ✅ Nova organização criada com sucesso")
            else:
                # Update existing
                changes = []
                change_details = []

                for key, value in data.items():
                    old_value = getattr(org, key, None)
                    if old_value != value:
                        # Mask sensitive data in output
                        if 'password' in key.lower():
                            old_display = "***" if old_value else "(vazio)"
                            new_display = "***" if value else "(vazio)"
                        else:
                            old_display = str(old_value)[:50] if old_value else "(vazio)"
                            new_display = str(value)[:50] if value else "(vazio)"

                        setattr(org, key, value)
                        changes.append(key)
                        change_details.append(f"{key}: {old_display} → {new_display}")

                if changes:
                    org.updated_at = datetime.utcnow()
                    updated_count += 1
                    print(f"   🔄 Organização atualizada ({len(changes)} campos)")
                    print("   Alterações:")
                    for detail in change_details:
                        print(f"      • {detail}")
                else:
                    print("   ✨ Sem alterações (dados já sincronizados)")

        # Commit
        print("\n" + "=" * 70)
        try:
            db.session.commit()
            print("✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
            print("-" * 70)
            print(f"   📊 Estatísticas:")
            print(f"      • Organizações criadas: {created_count}")
            print(f"      • Organizações atualizadas: {updated_count}")
            print(f"      • Avisos: {warnings_count}")
            print(f"      • Erros: {errors_count}")
            print("=" * 70 + "\n")

            if warnings_count > 0:
                print("💡 Dica: Reveja os avisos acima para garantir configuração completa.")

            return 0

        except Exception as e:
            db.session.rollback()
            print("❌ ERRO AO GUARDAR ALTERAÇÕES NA BASE DE DADOS")
            print("-" * 70)
            print(f"   Erro: {e}")
            print("=" * 70 + "\n")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    exit_code = seed_organizations()
    sys.exit(exit_code)
