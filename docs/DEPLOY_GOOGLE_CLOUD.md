# 🚀 Deploy no Google Cloud Platform

Guia completo para fazer deploy da aplicação Gestor de Eventos no Google Cloud Platform.

## 📋 Opções de Deploy

### 1. Google App Engine (Recomendado - Mais Simples)
- ✅ Deploy automático
- ✅ Escalabilidade automática
- ✅ HTTPS automático
- ✅ Domínio gratuito
- 💰 **Preço**: Tier gratuito disponível (28 horas/dia)

### 2. Google Cloud Run
- ✅ Containers Docker
- ✅ Escalabilidade automática (até zero)
- ✅ HTTPS automático
- 💰 **Preço**: Pay-per-use (muito económico)

---

## 🔧 Opção 1: Google App Engine (RECOMENDADO)

### Passo 1: Preparar o Projeto

#### 1.1. Criar ficheiro `app.yaml`

Crie o ficheiro `app.yaml` na raiz do projeto:

```yaml
runtime: python39

env_variables:
  FLASK_ENV: "production"

handlers:
  # Static files
  - url: /static
    static_dir: app/static
    secure: always

  # All other URLs
  - url: /.*
    script: auto
    secure: always

# Automatic scaling
automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 0
  max_instances: 10

# Instance class
instance_class: F1
```

#### 1.2. Criar ficheiro `.gcloudignore`

```bash
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Flask
instance/
.env

# Database
*.db
*.sqlite
*.sqlite3

# Google credentials
credentials.json
token.json

# Git
.git
.gitignore

# IDE
.vscode/
.idea/

# Logs
*.log

# Certificates
certificados/
```

#### 1.3. Atualizar `requirements.txt`

Certifique-se que tem todas as dependências:

```bash
pip freeze > requirements.txt
```

### Passo 2: Configurar Google Cloud

#### 2.1. Criar Projeto no Google Cloud

1. Aceda a: https://console.cloud.google.com/
2. Clique em **"Criar Projeto"**
3. Nome: `gestor-eventos` (ou outro nome)
4. Clique em **"Criar"**

#### 2.2. Ativar App Engine

```bash
# No terminal do seu computador
gcloud app create --region=europe-west1
```

Regiões disponíveis em Portugal/Europa:
- `europe-west1` (Bélgica) - **Recomendado**
- `europe-west2` (Londres)
- `europe-west3` (Frankfurt)

#### 2.3. Ativar APIs Necessárias

```bash
# Cloud Build (para deploy)
gcloud services enable cloudbuild.googleapis.com

# App Engine Admin
gcloud services enable appengine.googleapis.com
```

### Passo 3: Configurar Base de Dados

#### Opção A: Cloud SQL (Produção)

Para produção, recomenda-se usar Cloud SQL (PostgreSQL):

1. Criar instância Cloud SQL:
```bash
gcloud sql instances create gestor-eventos-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=europe-west1
```

2. Criar base de dados:
```bash
gcloud sql databases create gestorevents --instance=gestor-eventos-db
```

3. Atualizar `app.yaml`:
```yaml
env_variables:
  DATABASE_URL: "postgresql://user:password@/dbname?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME"
```

#### Opção B: SQLite (Desenvolvimento/Teste)

Para testes, pode usar SQLite (já configurado).

### Passo 4: Configurar Variáveis de Ambiente

Crie ficheiro `.env.yaml` (NÃO COMMITAR):

```yaml
env_variables:
  EMAIL_PASSWORD: "sua_password_smtp"
  ARDATERRA_EMAIL: "ardoterra@gmail.com"
  ARDATERRA_PASSWORD: "password_ardaterra"
  SECRET_KEY: "chave-secreta-super-aleatoria-aqui"
  FLASK_ENV: "production"
```

Atualizar `app.yaml` para incluir:
```yaml
includes:
  - .env.yaml
```

### Passo 5: Deploy

#### 5.1. Fazer Deploy

```bash
# Deploy da aplicação
gcloud app deploy

# Deploy com versão específica
gcloud app deploy --version=v1
```

#### 5.2. Visualizar Aplicação

```bash
# Abrir no browser
gcloud app browse
```

Sua aplicação estará disponível em:
`https://PROJECT_ID.appspot.com`

#### 5.3. Ver Logs

```bash
# Ver logs em tempo real
gcloud app logs tail -s default

# Ver logs no console
gcloud app logs read
```

### Passo 6: Configurar Domínio Personalizado (Opcional)

#### 6.1. Adicionar Domínio

```bash
gcloud app domain-mappings create "seudominio.com"
```

#### 6.2. Configurar DNS

No seu provedor DNS, adicione os registos fornecidos pelo Google Cloud.

---

## 🐳 Opção 2: Google Cloud Run

### Passo 1: Criar Dockerfile

Crie `Dockerfile` na raiz:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p certificados Logos

# Expose port
EXPOSE 8080

# Run application
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 run:app
```

### Passo 2: Adicionar Gunicorn

Adicione ao `requirements.txt`:
```
gunicorn==21.2.0
```

### Passo 3: Build e Deploy

```bash
# Build da imagem
gcloud builds submit --tag gcr.io/PROJECT_ID/gestor-eventos

# Deploy no Cloud Run
gcloud run deploy gestor-eventos \
    --image gcr.io/PROJECT_ID/gestor-eventos \
    --platform managed \
    --region europe-west1 \
    --allow-unauthenticated \
    --set-env-vars="FLASK_ENV=production"
```

---

## 🔒 Configurar OAuth Google (Importante!)

Após deploy, atualize as **Redirect URIs** no Google Cloud Console:

### URLs a Adicionar:

1. **App Engine**:
   ```
   https://PROJECT_ID.appspot.com/oauth2callback
   https://PROJECT_ID.appspot.com/google/callback
   ```

2. **Cloud Run**:
   ```
   https://gestor-eventos-XXXX.run.app/oauth2callback
   https://gestor-eventos-XXXX.run.app/google/callback
   ```

3. **Domínio Personalizado**:
   ```
   https://seudominio.com/oauth2callback
   https://seudominio.com/google/callback
   ```

### Como Adicionar:

1. Aceda: https://console.cloud.google.com/apis/credentials
2. Clique nas credenciais OAuth 2.0
3. Em **"URIs de redirecionamento autorizados"**, adicione os URLs acima
4. Clique em **"Guardar"**

📖 Consulte: [docs/GOOGLE_ADICIONAR_URI.md](GOOGLE_ADICIONAR_URI.md)

---

## 📊 Monitorização

### Ver Métricas

```bash
# Abrir dashboard
gcloud app open-console
```

### Ver Logs

```bash
# Logs em tempo real
gcloud app logs tail -s default

# Filtrar por erro
gcloud app logs read --level=error
```

### Ver Custos

Aceda: https://console.cloud.google.com/billing

---

## 💰 Custos Estimados

### App Engine (F1 Instance)
- **Tier Gratuito**: 28 horas/dia
- **Depois**: ~€0.05/hora
- **Estimativa**: €0-20/mês (baixo tráfego)

### Cloud Run
- **Tier Gratuito**: 2M requests/mês
- **CPU**: €0.00002400/vCPU-segundo
- **Memória**: €0.00000250/GiB-segundo
- **Estimativa**: €0-5/mês (baixo tráfego)

### Cloud SQL (se usar)
- **db-f1-micro**: ~€8/mês
- **Alternativa**: Use SQLite (gratuito, mas sem redundância)

---

## 🔧 Comandos Úteis

```bash
# Ver aplicações
gcloud app services list

# Ver versões
gcloud app versions list

# Promover versão
gcloud app versions migrate v1

# Eliminar versão antiga
gcloud app versions delete v0

# Ver configuração
gcloud app describe

# SSH para instância (debug)
gcloud app instances ssh INSTANCE_NAME

# Parar aplicação (parar cobranças)
gcloud app versions stop v1
```

---

## 🆘 Troubleshooting

### Erro: "Module not found"
```bash
# Rebuild requirements
pip freeze > requirements.txt
gcloud app deploy
```

### Erro: "Permission denied"
```bash
# Re-autenticar
gcloud auth login
gcloud config set project PROJECT_ID
```

### Erro: "Database locked"
- Use Cloud SQL em vez de SQLite para produção

### Logs não aparecem
```bash
# Ativar logging
gcloud app logs tail -s default --level=debug
```

---

## 📚 Recursos Adicionais

- [App Engine Documentation](https://cloud.google.com/appengine/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Pricing Calculator](https://cloud.google.com/products/calculator)

---

## ✅ Checklist de Deploy

- [ ] Criar `app.yaml`
- [ ] Criar `.gcloudignore`
- [ ] Atualizar `requirements.txt`
- [ ] Criar projeto no Google Cloud
- [ ] Ativar App Engine
- [ ] Configurar variáveis de ambiente
- [ ] Fazer deploy inicial
- [ ] Configurar Redirect URIs OAuth
- [ ] Testar funcionalidades
- [ ] Configurar domínio (opcional)
- [ ] Configurar monitorização

---

**Pronto!** 🎉 Sua aplicação está no ar!

Para atualizações futuras, basta executar:
```bash
gcloud app deploy
```
