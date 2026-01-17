# 📤 Como fazer Push para GitHub (anaritamindset)

O código está commitado localmente mas precisa ser enviado para o GitHub.

## ✅ Mudanças Prontas para Push:

```
- Dockerfile (novo)
- .dockerignore (novo)
- DEPLOY_CLOUD_RUN.md (novo)
- requirements.txt (atualizado com gunicorn)
- app/services/google_forms_service.py (melhorado)
```

## 🔐 Opção 1: Via GitHub CLI (Recomendado)

### Passo 1: Login com conta anaritamindset

```bash
gh auth logout
gh auth login
```

Quando aparecer as opções:
1. **What account do you want to log into?** → `GitHub.com`
2. **What is your preferred protocol?** → `HTTPS`
3. **Authenticate Git with your GitHub credentials?** → `Yes`
4. **How would you like to authenticate?** → `Login with a web browser`

Siga o código que aparecer e faça login com a conta **anaritamindset@gmail.com**

### Passo 2: Fazer Push

```bash
cd /Users/f.nuno/projetos/GestorEventos
git push origin main
```

---

## 🔑 Opção 2: Via Personal Access Token

### Passo 1: Criar Token

1. Acesse: https://github.com/settings/tokens/new
2. Login com conta **anaritamindset**
3. Configurar:
   - **Note:** `GestorEventos Deploy`
   - **Expiration:** `90 days`
   - **Scopes:** Marque `repo` (acesso completo)
4. Clique **"Generate token"**
5. **COPIE o token** (começa com `ghp_...`)

### Passo 2: Fazer Push com Token

```bash
cd /Users/f.nuno/projetos/GestorEventos

# Opção A: Push direto (vai pedir credenciais)
git push origin main
# Username: anaritamindset
# Password: [COLE O TOKEN AQUI]

# Opção B: Configurar remote com token
git remote set-url origin https://SEU_TOKEN@github.com/anaritamindset/GestorEventos.git
git push origin main
```

⚠️ **Substitua `SEU_TOKEN` pelo token copiado!**

---

## 🖥️ Opção 3: Via GitHub Desktop (Mais fácil)

1. Abra **GitHub Desktop**
2. Faça login com conta **anaritamindset**
3. Vá em **File > Add Local Repository**
4. Selecione a pasta: `/Users/f.nuno/projetos/GestorEventos`
5. Clique em **"Push origin"**

---

## ✅ Verificar se deu certo

Acesse: https://github.com/anaritamindset/GestorEventos

Deve aparecer:
- ✅ Commit recente: "Add Google Cloud Run deployment configuration"
- ✅ Arquivos novos: `Dockerfile`, `.dockerignore`, `DEPLOY_CLOUD_RUN.md`

---

## 🚀 Depois do Push

Depois que o push estiver completo, volte e vamos fazer o deploy no Google Cloud Run!

```bash
# Verificar que deu push
git status

# Deve mostrar: "Your branch is up to date with 'origin/main'."
```
