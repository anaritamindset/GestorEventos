# 🚀 Deploy Rápido - Google App Engine

Guia de início rápido para fazer deploy em 10 minutos.

## ⚡ Passos Rápidos

### 1. Instalar Google Cloud SDK

```bash
# macOS
brew install google-cloud-sdk

# Windows
# Baixe de: https://cloud.google.com/sdk/docs/install

# Linux
curl https://sdk.cloud.google.com | bash
```

### 2. Autenticar

```bash
gcloud auth login
```

### 3. Criar Projeto

```bash
# Criar projeto (escolha um ID único)
gcloud projects create gestor-eventos-prod --name="Gestor Eventos"

# Definir como projeto ativo
gcloud config set project gestor-eventos-prod
```

### 4. Ativar Faturação

1. Aceda: https://console.cloud.google.com/billing
2. Associe um método de pagamento ao projeto
3. **Não se preocupe**: O tier gratuito cobre ~28h/dia

### 5. Criar App Engine

```bash
gcloud app create --region=europe-west1
```

### 6. Configurar Variáveis de Ambiente

```bash
# Copiar exemplo
cp .env.yaml.example .env.yaml

# Editar com suas credenciais
nano .env.yaml
```

Preencha:
- `EMAIL_PASSWORD`: App Password do Gmail da Ana Rita
- `ARDATERRA_PASSWORD`: App Password do Gmail ARdaTerra
- `SECRET_KEY`: String aleatória longa

### 7. Deploy!

```bash
gcloud app deploy
```

Responda **Y** quando perguntado.

### 8. Abrir Aplicação

```bash
gcloud app browse
```

---

## 🔑 Configurar OAuth (Importante!)

Após o deploy, adicione as redirect URIs:

1. Aceda: https://console.cloud.google.com/apis/credentials
2. Clique nas suas credenciais OAuth 2.0
3. Adicione:
   ```
   https://gestor-eventos-prod.appspot.com/oauth2callback
   https://gestor-eventos-prod.appspot.com/google/callback
   ```
4. Guardar

---

## 📊 Ver Logs

```bash
# Logs em tempo real
gcloud app logs tail -s default

# Ver no browser
gcloud app open-console
```

---

## 🔄 Atualizar Aplicação

```bash
# Fazer alterações no código
git add .
git commit -m "Minhas alterações"
git push

# Deploy nova versão
gcloud app deploy
```

---

## 💰 Custos Esperados

**Tier Gratuito**:
- 28 horas de instância/dia
- 1 GB tráfego/dia
- **Custo**: €0

**Se exceder** (improvável para baixo tráfego):
- ~€0.05/hora adicional
- ~€5-15/mês

---

## 🆘 Problemas Comuns

### "Project not found"
```bash
gcloud config set project gestor-eventos-prod
```

### "Billing not enabled"
Ative em: https://console.cloud.google.com/billing

### "Module not found"
```bash
pip freeze > requirements.txt
gcloud app deploy
```

### Logs vazios
```bash
gcloud app logs tail -s default --level=debug
```

---

## ✅ Checklist

- [x] Instalar Google Cloud SDK
- [x] Criar projeto
- [x] Ativar faturação
- [x] Criar App Engine
- [x] Configurar `.env.yaml`
- [x] Deploy
- [x] Configurar OAuth URIs
- [ ] Testar aplicação
- [ ] Monitorizar logs

---

**Pronto!** 🎉

Sua aplicação está no ar em:
`https://gestor-eventos-prod.appspot.com`

Para mais detalhes: [docs/DEPLOY_GOOGLE_CLOUD.md](docs/DEPLOY_GOOGLE_CLOUD.md)
