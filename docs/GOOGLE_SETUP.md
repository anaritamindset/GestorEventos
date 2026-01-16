# Configuração Google OAuth - Gestão Automática

Este guia explica como configurar a autenticação Google para usar as funcionalidades automáticas do Gestor de Eventos.

## Passo 1: Criar Projeto no Google Cloud Console

1. Aceda a [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Anote o nome do projeto

## Passo 2: Ativar APIs Necessárias

No Google Cloud Console, ative as seguintes APIs:

1. **Google Forms API**
   - Vá a "APIs & Services" > "Library"
   - Pesquise "Google Forms API"
   - Clique em "Enable"

2. **Google Sheets API**
   - Pesquise "Google Sheets API"
   - Clique em "Enable"

3. **Google Drive API**
   - Pesquise "Google Drive API"
   - Clique em "Enable"

## Passo 3: Configurar OAuth Consent Screen

1. Vá a "APIs & Services" > "OAuth consent screen"
2. Escolha "External" (para uso pessoal) ou "Internal" (para organização)
3. Preencha os campos obrigatórios:
   - **App name**: Gestor de Eventos Wellness
   - **User support email**: seu email
   - **Developer contact information**: seu email
4. Clique em "Save and Continue"
5. Em **Scopes**, adicione os seguintes escopos:
   - `https://www.googleapis.com/auth/forms.body`
   - `https://www.googleapis.com/auth/forms.responses.readonly`
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive.file`
6. Clique em "Save and Continue"
7. Em "Test users", adicione seu email (para modo de teste)
8. Clique em "Save and Continue"

## Passo 4: Criar Credenciais OAuth 2.0

1. Vá a "APIs & Services" > "Credentials"
2. Clique em "+ CREATE CREDENTIALS" > "OAuth client ID"
3. Escolha "Web application"
4. Preencha:
   - **Name**: Gestor Eventos Web Client
   - **Authorized redirect URIs**:
     - `http://localhost:5000/google/callback`
     - `http://127.0.0.1:5000/google/callback`
     - (Adicione também o URL de produção quando aplicável)
5. Clique em "CREATE"
6. **Baixe o ficheiro JSON** clicando no ícone de download
7. Renomeie o ficheiro para `credentials.json`
8. Coloque o ficheiro na raiz do projeto: `/Users/f.nuno/projetos/GestorEventos/credentials.json`

## Passo 5: Estrutura do Ficheiro credentials.json

O ficheiro deve ter a seguinte estrutura:

```json
{
  "web": {
    "client_id": "SEU_CLIENT_ID_AQUI.apps.googleusercontent.com",
    "project_id": "seu-projeto",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "SEU_CLIENT_SECRET_AQUI",
    "redirect_uris": [
      "http://localhost:5000/google/callback"
    ]
  }
}
```

## Passo 6: Testar a Autenticação

1. Inicie o servidor: `python run.py`
2. Aceda a: http://127.0.0.1:5000/gestao_automatica
3. Clique em "Conectar com Google"
4. Autorize a aplicação
5. Será redirecionado de volta com autenticação completa

## Segurança

⚠️ **IMPORTANTE:**
- **NÃO** faça commit do ficheiro `credentials.json` no Git
- **NÃO** faça commit do ficheiro `token.json` no Git
- Estes ficheiros já estão no `.gitignore`

## Resolução de Problemas

### Erro: "Credentials file not found"
- Verifique se o ficheiro `credentials.json` está na raiz do projeto
- Verifique se o nome do ficheiro está correto

### Erro: "Redirect URI mismatch"
- Verifique se o URI de redirecionamento no Google Cloud Console coincide exatamente com o usado na aplicação
- URIs devem incluir protocolo (http/https), domínio e porta

### Erro: "Access blocked: This app's request is invalid"
- Verifique se adicionou seu email como "Test user" no OAuth consent screen
- Verifique se ativou todas as APIs necessárias

### Erro: "Invalid grant"
- Delete o ficheiro `token.json` e refaça a autenticação

## Funcionalidades Disponíveis Após Autenticação

✅ Criar Google Forms automaticamente para cada evento
✅ Criar Google Sheets para armazenar respostas
✅ Sincronizar participantes das respostas do Form
✅ Enviar certificados automaticamente

## Mais Informações

- [Google Forms API Documentation](https://developers.google.com/forms/api)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
