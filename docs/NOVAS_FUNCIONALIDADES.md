# Novas Funcionalidades - GestorEventos v2.0

Documento resumo das funcionalidades implementadas durante a sessão de desenvolvimento.

---

## 1. Integração com Google Sheets

### Descrição
Importação automática de participantes a partir de Google Sheets para eventos existentes.

### Endpoints API

#### GET `/api/gdrive/auth`
Inicia o fluxo de autenticação OAuth com Google APIs.

#### GET `/api/gdrive/files`
Lista todas as Google Sheets disponíveis no Google Drive do utilizador.

#### GET `/api/gdrive/preview/<spreadsheet_id>`
Pré-visualiza dados de uma Google Sheet antes da importação.

#### POST `/api/gdrive/import/participants/<event_id>`
Importa participantes de uma Google Sheet para um evento específico.

**Request Body:**
```json
{
    "spreadsheet_id": "1abc...xyz",
    "range": "A2:Z1000",
    "skip_duplicates": true,
    "column_mapping": {
        "0": "nome",
        "1": "email",
        "2": "telefone",
        "3": "empresa",
        "4": "observacoes"
    }
}
```

**Response:**
```json
{
    "message": "Importação concluída: 15 participantes importados",
    "stats": {
        "total_rows": 20,
        "imported": 15,
        "skipped": 3,
        "errors": 2,
        "error_details": [...]
    }
}
```

### Funcionalidades
- Autenticação OAuth2 com Google
- Detecção automática de duplicados
- Mapeamento flexível de colunas
- Estatísticas detalhadas de importação
- Gestão de erros linha a linha

---

## 2. Geração de Certificados com QR Codes

### Descrição
Sistema completo de geração de certificados PDF personalizados com QR codes para validação.

### Endpoints API

#### POST `/api/certificates/generate/<participant_id>`
Gera certificado PDF para um participante específico.

**Request Body (opcional):**
```json
{
    "template_id": 1,
    "base_url": "https://meusite.com"
}
```

**Response:**
```json
{
    "message": "Certificado gerado com sucesso",
    "participant": {...},
    "certificate_path": "certificados/certificado_123_20250113_143052.pdf"
}
```

#### POST `/api/certificates/generate/event/<event_id>`
Gera certificados para todos os participantes de um evento (geração em lote).

**Response:**
```json
{
    "message": "Geração em lote concluída: 25 certificados gerados",
    "stats": {
        "total": 30,
        "generated": 25,
        "errors": 5,
        "error_details": [...]
    }
}
```

#### GET `/api/certificates/download/<participant_id>`
Faz download do certificado PDF de um participante.

#### GET `/api/certificates/validate/<participant_id>`
Valida um certificado através do QR code (endpoint público para validação).

**Response:**
```json
{
    "valid": true,
    "participant": {
        "nome": "João Silva",
        "email": "joao@example.com"
    },
    "event": {
        "nome": "Workshop Python Avançado",
        "data_inicio": "2025-01-15",
        "duracao_horas": 8
    },
    "certificate_generated": true,
    "certificate_sent": true
}
```

### Funcionalidades do Certificado

#### Design Profissional
- Layout landscape A4
- Bordas duplas com cores personalizáveis
- Tipografia hierárquica (título, nome, evento)
- Cores configuráveis via template

#### Informações Incluídas
- Nome completo do participante (destaque)
- Nome do evento
- Data do evento (início e fim se aplicável)
- Duração em horas
- Local do evento
- Nome do formador
- Data de emissão
- ID único do certificado

#### QR Code
- Gerado automaticamente
- Aponta para URL de validação
- Posicionado no canto inferior direito
- Inclui texto "Valide este certificado"

#### Customização
- Cores primária, secundária e de texto
- Fontes personalizáveis
- Suporte para logos e assinaturas (preparado)
- Templates reutilizáveis via modelo CertificateTemplate

### Serviço CertificateService

**Localização:** `app/services/certificate_service.py`

**Métodos principais:**
- `generate_certificate()` - Gera certificado individual
- `batch_generate_certificates()` - Geração em lote
- `generate_qr_code()` - Criação de QR codes
- `_create_pdf()` - Criação do PDF com ReportLab

**Dependências:**
- ReportLab 4.3.1 - Geração de PDFs
- qrcode 8.0 - Geração de QR codes
- Pillow 11.1.0 - Processamento de imagens

---

## 3. Serviço de Importação de Participantes

### Descrição
Serviço dedicado para importação de participantes com suporte para Google Sheets e Google Forms.

**Localização:** `app/services/participant_import_service.py`

### Funcionalidades

#### Importação de Google Sheets
```python
from app.services.participant_import_service import ParticipantImportService

service = ParticipantImportService()
stats = service.import_from_sheet(
    spreadsheet_id='1abc...xyz',
    event_id=5,
    column_mapping={0: 'nome', 1: 'email'},
    skip_duplicates=True
)
```

#### Importação de Google Forms
```python
stats = service.import_from_form_responses(
    form_id='1def...uvw',
    event_id=5,
    skip_duplicates=True
)
```

#### Pré-visualização
```python
preview = service.preview_sheet_data(
    spreadsheet_id='1abc...xyz',
    sheet_range='A1:Z100'
)
# Retorna primeiras 10 linhas para validação
```

#### Listar Sheets Disponíveis
```python
sheets = service.get_available_sheets(limit=50)
# Retorna lista de Google Sheets do utilizador
```

---

## 4. Melhorias na API de Google Drive

### Endpoint Melhorado: POST `/api/gdrive/import/participants/<event_id>`

**Antes:** Endpoint genérico `/api/gdrive/import` que apenas parseava dados

**Depois:** Endpoint específico para eventos com:
- Validação de evento existente
- Importação direta para base de dados
- Detecção de duplicados
- Mapeamento flexível de colunas
- Estatísticas detalhadas
- Gestão de erros robusta

---

## 5. Estrutura de Ficheiros Criados

```
app/
├── services/
│   ├── __init__.py                      (atualizado)
│   ├── google_service.py                (existente)
│   ├── certificate_service.py           (NOVO)
│   └── participant_import_service.py    (NOVO)
└── api/
    └── routes/
        ├── certificates.py              (melhorado)
        └── gdrive.py                    (melhorado)

certificados/                            (pasta criada automaticamente)
NOVAS_FUNCIONALIDADES.md                 (NOVO)
```

---

## 6. Fluxo de Trabalho Típico

### Cenário: Organizar um Evento com Google Forms

1. **Criar evento no sistema**
   ```
   POST /api/events
   ```

2. **Criar Google Form** (opcional, via GoogleService)
   ```python
   from app.services import GoogleService
   gs = GoogleService()
   form_id = gs.create_event_form(
       evento_nome="Workshop Python",
       evento_data="15/01/2025",
       evento_duracao="8 horas"
   )
   ```

3. **Importar respostas do Form**
   ```
   POST /api/gdrive/import/participants/{event_id}
   ```

4. **Fazer check-in dos participantes** (durante evento)
   ```
   POST /api/participants/{id}/checkin
   ```

5. **Gerar certificados** (após evento)
   ```
   POST /api/certificates/generate/event/{event_id}
   ```

6. **Participantes fazem download**
   ```
   GET /api/certificates/download/{participant_id}
   ```

7. **Validação via QR code** (qualquer pessoa)
   ```
   GET /api/certificates/validate/{participant_id}
   ```

---

## 7. Configuração Necessária

### Google APIs
1. Criar projeto no Google Cloud Console
2. Ativar APIs:
   - Google Sheets API
   - Google Drive API
   - Google Forms API
3. Criar credenciais OAuth 2.0
4. Descarregar `credentials.json` para pasta raiz
5. Primeiro uso: autenticar via `/api/gdrive/auth`

### Variáveis de Ambiente (opcional)
```bash
# .env
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.pickle
CERTIFICATE_OUTPUT_DIR=certificados
BASE_URL=https://gestorev2.example.com
```

---

## 8. Próximos Passos Sugeridos

### Funcionalidades Pendentes
- [ ] Serviço de envio de emails (EmailService)
- [ ] Área de download pública para participantes
- [ ] Templates de certificados customizáveis via UI
- [ ] Suporte para logos e assinaturas nos certificados
- [ ] Testes automatizados (pytest)
- [ ] Documentação Swagger/OpenAPI
- [ ] Autenticação JWT nos endpoints
- [ ] Rate limiting
- [ ] Cache para validação de certificados

### Melhorias Técnicas
- [ ] Celery para processamento em background
- [ ] Redis para cache
- [ ] Webhook para Google Forms (em vez de polling)
- [ ] Compressão de PDFs
- [ ] Watermark nos certificados
- [ ] Versioning de templates

---

## 9. Dependências Adicionadas

Já incluídas em `requirements_v2.txt`:
```txt
# PDF & QR Codes
reportlab==4.3.1
Pillow==11.1.0
qrcode==8.0

# Google APIs
google-api-python-client==2.111.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.0
```

---

## 10. Notas de Segurança

### Google Credentials
- `credentials.json` e `token.pickle` **NÃO devem** estar no git
- Adicionar ao `.gitignore`:
  ```
  credentials.json
  token.pickle
  *.pickle
  ```

### Certificados
- PDFs armazenados localmente em `certificados/`
- Considerar storage cloud (S3, GCS) para produção
- Implementar controlo de acesso aos downloads
- QR codes apontam para validação pública (OK)

### APIs
- Implementar autenticação JWT
- Rate limiting nos endpoints de geração
- Validação rigorosa de inputs
- Sanitização de nomes de ficheiros

---

## Resumo

Implementámos com sucesso:

✅ **Integração completa com Google Sheets** - Importação automática de participantes
✅ **Geração de certificados PDF** - Com ReportLab, design profissional
✅ **QR Codes de validação** - Para autenticidade dos certificados
✅ **API robusta** - 4 novos endpoints, melhorias em 2 existentes
✅ **Serviços modulares** - CertificateService, ParticipantImportService
✅ **Documentação** - Este ficheiro!

O sistema está pronto para gerar certificados profissionais e importar participantes de forma automatizada!
