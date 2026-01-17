# 📋 Resumo - Deploy GestorEventos v2.0

## ✅ O que foi preparado

### 1. Arquivos de Containerização
- ✅ **Dockerfile** - Containeriza a aplicação Flask
- ✅ **.dockerignore** - Exclui arquivos desnecessários
- ✅ **requirements.txt** - Atualizado com gunicorn

### 2. Scripts e Guias
- ✅ **deploy.sh** - Script automático de deploy
- ✅ **DEPLOY_CLOUD_RUN.md** - Guia completo passo a passo
- ✅ **PUSH_GITHUB.md** - Guia para fazer push

### 3. Código Commitado
- ✅ Commit local criado com todas as mudanças
- ⏳ **Pendente:** Push para GitHub (precisa autenticar)

### 4. Google Cloud SDK
- ⏳ **Instalando:** gcloud CLI via Homebrew (em progresso)

---

## 🚀 Próximos Passos

### Passo 1: Push para GitHub ⏳

**Escolha uma opção do guia `PUSH_GITHUB.md`:**

#### Opção Mais Fácil - GitHub CLI:
```bash
gh auth logout
gh auth login
# Siga instruções e faça login com anaritamindset@gmail.com
git push origin main
```

#### Ou via Personal Access Token:
1. Criar token em: https://github.com/settings/tokens/new
2. Login com `anaritamindset`
3. Marcar scope `repo`
4. Copiar token
5. Fazer push:
```bash
git push origin main
# Username: anaritamindset
# Password: [COLAR TOKEN]
```

---

### Passo 2: Deploy no Google Cloud Run 🎯

#### Aguardar instalação do gcloud CLI
```bash
# Verificar se instalação terminou
which gcloud

# Se não estiver no PATH, adicionar:
export PATH=/usr/local/share/google-cloud-sdk/bin:"$PATH"
```

#### Opção A - Deploy Automático (Recomendado):
```bash
cd /Users/f.nuno/projetos/GestorEventos
./deploy.sh
```

#### Opção B - Deploy Manual:
```bash
# 1. Login
gcloud auth login

# 2. Criar projeto
gcloud projects create gestor-eventos-app

# 3. Configurar
gcloud config set project gestor-eventos-app

# 4. Ativar APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 5. Deploy
gcloud run deploy gestor-eventos \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated
```

---

### Passo 3: Configurar Credenciais Google ��

Depois do deploy, você receberá uma URL tipo:
```
https://gestor-eventos-XXXXXX.europe-west1.run.app
```

#### 3.1. Atualizar Redirect URIs
1. Acesse: https://console.cloud.google.com/apis/credentials
2. Selecione seu OAuth 2.0 Client ID
3. Adicione em "Authorized redirect URIs":
   ```
   https://gestor-eventos-XXXXXX.europe-west1.run.app/google/callback
   ```

#### 3.2. Adicionar credentials.json como Secret
```bash
gcloud secrets create google-credentials \
  --data-file=credentials.json

gcloud run services update gestor-eventos \
  --update-secrets=/app/credentials.json=google-credentials:latest
```

---

## 📊 Custos Estimados

### Tier Gratuito (Always Free):
```
✅ 2 milhões de requisições/mês
✅ 360.000 GB-segundos
✅ 180.000 vCPU-segundos
```

**Para este projeto = GRÁTIS na prática!**

---

## 🔍 Comandos Úteis

### Ver logs:
```bash
gcloud run services logs read gestor-eventos --limit 100
```

### Ver status:
```bash
gcloud run services describe gestor-eventos
```

### Atualizar aplicação:
```bash
./deploy.sh
```

---

## 📞 Suporte

### Documentação:
- Cloud Run: https://cloud.google.com/run/docs
- Pricing: https://cloud.google.com/run/pricing

### Repositório:
- GitHub: https://github.com/anaritamindset/GestorEventos

---

## ✨ Status Atual

- [✅] Código preparado para deploy
- [✅] Dockerfile criado
- [✅] Script de deploy criado
- [⏳] gcloud CLI instalando
- [⏳] Push para GitHub pendente
- [⏳] Deploy no Cloud Run pendente

**Está quase tudo pronto! Só faltam os passos 1 e 2!** 🎉

---

**Desenvolvido por Ana Rita - Mindset Wellness**
**Deploy preparado com Claude Code**
