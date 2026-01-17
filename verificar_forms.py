#!/usr/bin/env python3
"""
Verificar formulários específicos por ID
"""

import sys
sys.path.insert(0, '/Users/f.nuno/projetos/GestorEventos')

from app.services.google_auth_service import GoogleAuthService

# IDs dos formulários fornecidos
FORM_IDS = [
    "1TGgoD09NMwMHdewErbNvVUCz2m7rq5kQ",
    "1e-6zkjoTffN0BBWMv3nYyKe7z5J6y0bo",
    "1tKEwm9Dh594BIdeTRU1ivhqcgEtVDMgr",
    "1DpPryX1KVXLXBMJmVa-DC4OFFuXGA7nq",
    "16KWSlgLpyWE7S0zyF9TMTWCLk9Xsv3ih",
    "1-oFVTrdZrJkuCXlR4TvUJMoZoYpvQZiIV4MyXdRnfls",
    "1CJ2ugbAql_-GQuPGQa8-eQzouZJt_c-17QdEi42KM7E",
    "1zYY-JObN9M9Iw2K7lyhR3DeoL4SkQtD2hskYopv9XUE",
    "1DoZ7T6zjAn3XTMybrXdX3KxLuDwml-STO_V1UW01OX8",
    "1Ob0bTDehRIE6jBsgzoTZqm-dribVk65pW0HAk8JteME",
    "1AzvY-8jC2HXiDD49YS3vf0NYyZZTaCLX",
    "178aJPzkAyX5Qlxa2xIsQOnwTAaJzAdoc6a2QmHmJfV8",
    "1wKgwqPEJzTMVbgl6W4CxLWVa2lUp7xlggd9_6SV00aE",
    "1X-utjKtO-QJPme9RTQAzsCW7TvPCpdg-",
    "1EGiR4nzoWAjBr82jINOB6kWIye0jc_8M",
    "1RvX2dr84g80n0Z4glhZptXugYGOUMpjz",
    "1l67fwYZmk0U5bUaw9ulz5K2-TzlpMUcQ",
    "1HpFOJ1dq4tifCKTvoxqA47ueOpDFrQjEPWCehbYPGco",
    "1rxLyajsN5q7K9Fs7UFhbfIzxvl8woOV2XmxHiySWRD0",
    "1AVFer0wtfkM2wke38HygMO_5N8iOCesw",
    "1zLZRctUem1AFIX8PrYjO2gjuvYEFnsVW",
    "1Jp-EaITwEb2m6VLpidR3D8x3uLMIMf24cW7uC-aPq5M",
    "1lAuUAwm6VtpRCGM3iOLRQXZSkc8YtPUs",
    "1Bid4sRrX0t3XSakjks3xwtQWpzho9IO6",
    "1gHI6UUhL3E4YYsPoh-VzP1GxxmqilVI-",
    "16M7I2upUHb3hnx2uRcugDXcmM5PU8a_a",
    "1uVXsRvM4qC7IgCPkppwsDhak5AXiKm0w",
    "1Sg8gFfHYzPluOM_HKb-nhgSAZFVP8B7i",
    "1UyMSLsPmWjJ5fX6QMfUpm7CbfYja2ATBUtZwdvpG2Xc",
    "1N9cf_U8OInnVlcotMBk_iZlGYUtPSJRf",
    "1nb7xgGMyySwuYkCfL7V-Eh6VOHmQO8qR",
    "1X83dvpxnWqRciNuhLXUqHEsGOQxmIGgS",
    "1XwwJYlfV0mcHVvpmmWVkGebN4S6JpvnPaWjuPSmPGfo",
    "16VKSLMVGL6rdDaeuI6-kCnvVhEr69rGm",
    "1OTl9ohzUSETpbYt72eyafPEOVO7Qm2Zl",
]

def main():
    print(f"🔍 Verificando {len(FORM_IDS)} arquivos...\n")

    auth_service = GoogleAuthService()
    drive_service = auth_service.get_drive_service()

    if not drive_service:
        print("❌ Erro ao obter serviço do Drive")
        return

    forms_count = 0
    other_count = 0
    error_count = 0

    forms_list = []

    for i, file_id in enumerate(FORM_IDS, 1):
        try:
            # Obter metadados do arquivo
            file_metadata = drive_service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, createdTime, modifiedTime, owners, trashed',
                supportsAllDrives=True
            ).execute()

            mime_type = file_metadata.get('mimeType', '')
            name = file_metadata.get('name', 'Sem nome')
            trashed = file_metadata.get('trashed', False)
            owner = file_metadata.get('owners', [{}])[0].get('emailAddress', 'N/A')

            if mime_type == 'application/vnd.google-apps.form':
                forms_count += 1
                status = "🗑️ DELETADO" if trashed else "✅ ATIVO"
                print(f"{forms_count}. {status} {name}")
                print(f"   ID: {file_id}")
                print(f"   Owner: {owner}")
                print(f"   Trashed: {trashed}")
                print()

                if not trashed:
                    forms_list.append({
                        'id': file_id,
                        'name': name,
                        'owner': owner,
                        'modified': file_metadata.get('modifiedTime')
                    })
            else:
                other_count += 1
                type_name = mime_type.split('.')[-1] if '.' in mime_type else mime_type
                print(f"   [{i}] ⚠️  {name} ({type_name})")

        except Exception as e:
            error_count += 1
            print(f"   [{i}] ❌ Erro ao acessar {file_id}: {e}")

    print("\n" + "=" * 60)
    print(f"📊 RESUMO:")
    print(f"   ✅ Formulários ATIVOS: {len(forms_list)}")
    print(f"   📝 Total de formulários: {forms_count}")
    print(f"   📄 Outros tipos de arquivo: {other_count}")
    print(f"   ❌ Erros de acesso: {error_count}")
    print("=" * 60)

    # Agora vamos buscar via API e comparar
    print("\n🔍 Buscando via API do Drive...\n")

    query = "mimeType='application/vnd.google-apps.form' and trashed=false"
    results = drive_service.files().list(
        q=query,
        pageSize=100,
        fields='files(id, name)',
        corpora='user'
    ).execute()

    api_forms = results.get('files', [])
    api_ids = {f['id'] for f in api_forms}
    manual_ids = {f['id'] for f in forms_list}

    print(f"API encontrou: {len(api_forms)} formulários")
    print(f"Manualmente encontramos: {len(forms_list)} formulários ATIVOS\n")

    # Formulários que estão na lista manual mas NÃO aparecem na busca da API
    missing_in_api = manual_ids - api_ids

    if missing_in_api:
        print("⚠️  FORMULÁRIOS QUE A API NÃO ENCONTROU:")
        for form in forms_list:
            if form['id'] in missing_in_api:
                print(f"   - {form['name']} ({form['owner']})")
        print(f"\nTotal: {len(missing_in_api)} formulários não encontrados pela API")
    else:
        print("✅ Todos os formulários ativos foram encontrados pela API!")

if __name__ == '__main__':
    main()
