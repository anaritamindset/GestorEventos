#!/usr/bin/env python3
"""
Script de teste para listar todos os Google Forms
"""

import sys
sys.path.insert(0, '/Users/f.nuno/projetos/GestorEventos')

from app.services.google_forms_service import GoogleFormsService

def main():
    print("🔍 Listando todos os Google Forms...\n")

    try:
        service = GoogleFormsService()
        forms = service.list_recent_forms(limit=200)

        print(f"✅ Encontrados {len(forms)} formulários:\n")

        for i, form in enumerate(forms, 1):
            print(f"{i}. {form['name']}")
            print(f"   ID: {form['id']}")
            print(f"   URL: {form['url']}")
            if form.get('event_date'):
                print(f"   📅 Data do Evento: {form['event_date']}")
            print(f"   👤 Proprietário: {form.get('owner', 'Desconhecido')}")
            print(f"   🕐 Modificado: {form.get('modified_time', 'N/A')}")
            print()

        print(f"\n📊 Total: {len(forms)} formulários")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
