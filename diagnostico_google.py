#!/usr/bin/env python3
"""
Script de diagnóstico para Google Drive API
"""

import sys
sys.path.insert(0, '/Users/f.nuno/projetos/GestorEventos')

from app.services.google_auth_service import GoogleAuthService

def main():
    print("🔍 Diagnóstico Google Drive API\n")

    try:
        auth_service = GoogleAuthService()
        drive_service = auth_service.get_drive_service()

        if not drive_service:
            print("❌ Não conseguiu obter serviço do Drive")
            return

        # 1. Ver informações da conta autenticada
        print("=" * 60)
        print("📧 CONTA AUTENTICADA")
        print("=" * 60)
        try:
            about = drive_service.about().get(fields="user").execute()
            user = about.get('user', {})
            print(f"Nome: {user.get('displayName', 'N/A')}")
            print(f"Email: {user.get('emailAddress', 'N/A')}")
            print()
        except Exception as e:
            print(f"Erro ao obter informações do usuário: {e}\n")

        # 2. Buscar com corpora='user'
        print("=" * 60)
        print("📋 BUSCA COM corpora='user' (apenas My Drive)")
        print("=" * 60)
        query = "mimeType='application/vnd.google-apps.form' and trashed=false"
        results = drive_service.files().list(
            q=query,
            pageSize=100,
            orderBy='modifiedTime desc',
            fields='files(id, name, modifiedTime)',
            corpora='user'
        ).execute()
        forms = results.get('files', [])
        print(f"Encontrados: {len(forms)} formulários")
        for form in forms[:5]:
            print(f"  - {form['name']}")
        print()

        # 3. Buscar com corpora='allDrives'
        print("=" * 60)
        print("📋 BUSCA COM corpora='allDrives' (todos os drives)")
        print("=" * 60)
        try:
            results = drive_service.files().list(
                q=query,
                pageSize=100,
                orderBy='modifiedTime desc',
                fields='files(id, name, modifiedTime)',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                corpora='allDrives'
            ).execute()
            forms = results.get('files', [])
            print(f"Encontrados: {len(forms)} formulários")
            for form in forms[:5]:
                print(f"  - {form['name']}")
        except Exception as e:
            print(f"Erro: {e}")
        print()

        # 4. Buscar TODOS os arquivos Google Forms (sem limite)
        print("=" * 60)
        print("📋 BUSCA COMPLETA (todas as páginas)")
        print("=" * 60)
        all_forms = []
        page_token = None
        page = 1

        while True:
            results = drive_service.files().list(
                q=query,
                pageSize=100,
                orderBy='modifiedTime desc',
                fields='nextPageToken, files(id, name, modifiedTime, owners)',
                corpora='user',
                pageToken=page_token
            ).execute()

            forms = results.get('files', [])
            all_forms.extend(forms)

            print(f"Página {page}: {len(forms)} formulários")

            page_token = results.get('nextPageToken')
            if not page_token:
                break
            page += 1

        print(f"\n✅ TOTAL: {len(all_forms)} formulários encontrados")
        print("\nPrimeiros 10:")
        for i, form in enumerate(all_forms[:10], 1):
            owner = form.get('owners', [{}])[0].get('emailAddress', 'N/A')
            print(f"{i}. {form['name']} ({owner})")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
