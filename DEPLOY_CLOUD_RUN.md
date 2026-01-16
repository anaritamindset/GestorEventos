# 🚀 Deploy no Google Cloud Run

Guia passo a passo para fazer deploy da aplicação GestorEventos no Google Cloud Run.

## 📋 Pré-requisitos

1. **Conta Google Cloud**
   - Acesse: https://console.cloud.google.com/
   - Se for novo, tem $300 de crédito grátis por 90 dias
   - Tier gratuito: 2 milhões de requisições/mês

2. **Google Cloud CLI (gcloud)**
   - macOS: `brew install google-cloud-sdk`
   - Ou baixe de: https://cloud.google.com/sdk/docs/install

## 🔧 Passo 1: Configurar Google Cloud

### 1.1. Instalar gcloud CLI (se ainda não tem)

```bash
brew install google-cloud-sdk
```

### 1.2. Fazer login e configurar projeto

```bash
# Login na conta Google
gcloud auth login

# Criar novo projeto (ou usar existente)
gcloud projects create gestor-eventos-app --name="Gestor Eventos"

# Definir projeto ativo
gcloud config set project gestor-eventos-app

# Ativar APIs necessárias
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## 🐳 Passo 2: Build e Deploy

### Opção A - Deploy Direto (Recomendado para primeira vez)

```bash
# No diretório do projeto
cd /Users/f.nuno/projetos/GestorEventos

# Deploy com build automático
gcloud run deploy gestor-eventos \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

### Opção B - Build Manual + Deploy

```bash
# 1. Build da imagem Docker
gcloud builds submit --tag gcr.io/gestor-eventos-app/gestor-eventos

# 2. Deploy da imagem
gcloud run deploy gestor-eventos \
  --image gcr.io/gestor-eventos-app/gestor-eventos \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 512Mi
```

## 🔐 Passo 3: Configurar Credenciais Google (OAuth)

⚠️ **IMPORTANTE:** A aplicação precisa das credenciais do Google para funcionar com Google Forms/Drive.

### 3.1. Atualizar Redirect URIs

1. Acesse: https://console.cloud.google.com/apis/credentials
2. Selecione seu OAuth 2.0 Client ID
3. Em **"Authorized redirect URIs"**, adicione:
   ```
   https://gestor-eventos-XXXXXXX.europe-west1.run.app/google/callback
   ```
   (Substitua XXXXXXX pela URL que o Cloud Run gerou)

### 3.2. Adicionar credentials.json como Secret

```bash
# Criar secret com credentials.json
gcloud secrets create google-credentials \
  --data-file=credentials.json

# Dar permissão ao Cloud Run para acessar
gcloud secrets add-iam-policy-binding google-credentials \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# Atualizar serviço para usar o secret
gcloud run services update gestor-eventos \
  --update-secrets=/app/credentials.json=google-credentials:latest
```

## 📊 Passo 4: Configurar Base de Dados (Opcional)

### Opção A - SQLite (Ephemeral Storage)
⚠️ **Atenção:** Dados são perdidos quando container reinicia!

- Cloud Run já suporta SQLite
- Recomendado apenas para testes

### Opção B - Cloud SQL (Recomendado para produção)

```bash
# Criar instância PostgreSQL
gcloud sql instances create gestor-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=europe-west1

# Criar base de dados
gcloud sql databases create gestor \
  --instance=gestor-db

# Conectar Cloud Run ao Cloud SQL
gcloud run services update gestor-eventos \
  --add-cloudsql-instances gestor-db
```

## ✅ Passo 5: Verificar Deploy

Após o deploy, Cloud Run retorna a URL:

```
Service [gestor-eventos] deployed to https://gestor-eventos-XXXXXXX.europe-west1.run.app
```

Teste acessando:
```
https://gestor-eventos-XXXXXXX.europe-west1.run.app
```

## 🔄 Atualizar Aplicação

Sempre que fizer mudanças no código:

```bash
# Commit e push para GitHub
git add .
git commit -m "Descrição das mudanças"
git push

# Re-deploy no Cloud Run
gcloud run deploy gestor-eventos --source .
```

## 💰 Custos Estimados

### Tier Gratuito (Always Free):
- 2 milhões de requisições/mês
- 360.000 GB-segundos
- 180.000 vCPU-segundos

**Para este projeto = GRÁTIS na prática!**

### Se ultrapassar:
- $0.40 por milhão de requisições
- $0.00002400 por GB-segundo
- $0.00001000 por vCPU-segundo

## 🐛 Troubleshooting

### Ver logs:
```bash
gcloud run services logs read gestor-eventos --limit 100
```

### Ver status do serviço:
```bash
gcloud run services describe gestor-eventos
```

### Testar localmente com Docker:
```bash
docker build -t gestor-eventos .
docker run -p 8080:8080 gestor-eventos
```

## 📚 Recursos Úteis

- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Pricing**: https://cloud.google.com/run/pricing
- **Quotas**: https://cloud.google.com/run/quotas

---

**Desenvolvido por Ana Rita - Mindset Wellness**
