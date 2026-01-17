# 🚀 Deploy no PythonAnywhere - Guia Completo

**Para: Ana Rita (não-técnico)**
Deploy super simples, sem cartão de crédito!

---

## 📝 Passo 1: Criar Conta (5 minutos)

1. **Acesse:** https://www.pythonanywhere.com/registration/register/beginner/

2. **Preencha:**
   - Username: `anaritamindset` (ou o que preferir)
   - Email: `anaritamindset@gmail.com`
   - Password: (escolha uma senha)

3. **Clique em "Register"**

4. **Confirme o email** (verifique a caixa de entrada)

✅ Conta criada! Gratuita para sempre!

---

## 📦 Passo 2: Fazer Upload do Código (10 minutos)

### Opção A - Via GitHub (Recomendado - Mais Fácil)

1. **Login no PythonAnywhere**
   - Acesse: https://www.pythonanywhere.com/login/

2. **Abra um Bash Console**
   - Clique em "Consoles" no menu
   - Clique em "Bash"

3. **Clone o repositório GitHub:**
   ```bash
   git clone https://github.com/anaritamindset/GestorEventos.git
   cd GestorEventos
   ```

4. **Criar ambiente virtual:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Inicializar base de dados:**
   ```bash
   python run.py init_db
   ```

✅ Código carregado!

### Opção B - Upload Manual (Se não funcionar o GitHub)

1. **Abra "Files" no menu**

2. **Clique em "Upload a file"**

3. **Faça upload de todos os ficheiros** do projeto (pode zipar primeiro)

---

## 🌐 Passo 3: Configurar Web App (5 minutos)

1. **Vá em "Web" no menu**

2. **Clique em "Add a new web app"**

3. **Configurações:**
   - Domain: `anaritamindset.pythonanywhere.com` (ou o username que escolheu)
   - Python version: **Python 3.11**
   - Framework: **Flask**
   - Path: `/home/anaritamindset/GestorEventos/wsgi.py`

4. **Na seção "Virtualenv":**
   - Path: `/home/anaritamindset/GestorEventos/venv`

5. **Na seção "WSGI configuration file":**
   - Clique no link do arquivo
   - **Substitua TUDO** pelo conteúdo abaixo:

```python
import sys
import os

# Caminho do projeto
project_home = '/home/anaritamindset/GestorEventos'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Configurações
os.environ['FLASK_ENV'] = 'production'
os.environ['DEBUG'] = 'False'

# Import da app
from run import app as application
```

6. **Salve o arquivo** (Ctrl+S ou botão "Save")

7. **Volte para a aba "Web"**

8. **Clique no botão verde "Reload anaritamindset.pythonanywhere.com"**

✅ App configurada!

---

## 🔐 Passo 4: Configurar credentials.json (5 minutos)

1. **Vá em "Files"**

2. **Navegue até:** `/home/anaritamindset/GestorEventos/`

3. **Clique em "Upload a file"**

4. **Faça upload do arquivo `credentials.json`**
   - Localize no teu computador em: `/Users/f.nuno/projetos/GestorEventos/credentials.json`

5. **Atualizar Redirect URIs no Google Cloud Console:**
   - Acesse: https://console.cloud.google.com/apis/credentials
   - Selecione seu OAuth 2.0 Client ID
   - Em "Authorized redirect URIs", **adicione**:
     ```
     https://anaritamindset.pythonanywhere.com/google/callback
     ```
   - Clique em "Save"

✅ Credenciais configuradas!

---

## 🎉 Passo 5: Testar a Aplicação!

**Acesse:**
```
https://anaritamindset.pythonanywhere.com
```

**Login padrão:**
- Email: `admin@gestorev2.local`
- Password: `admin123`

⚠️ **IMPORTANTE:** Depois do primeiro login, vá em "Utilizadores" e:
1. Mude a senha do admin
2. Crie um novo utilizador para a Ana Rita

---

## 📊 Limitações da Conta Gratuita

✅ **Inclui:**
- Site sempre online
- 512MB de espaço
- Tráfego ilimitado (dentro do razoável)
- HTTPS automático
- Subdomínio pythonanywhere.com

⏳ **Atenção:**
- Se não usar por **3 meses**, a app é desativada (reativar é fácil - 1 clique)
- CPU limitada (mas suficiente para este projeto)

---

## 🔄 Como Atualizar a Aplicação

Quando fizer mudanças no código:

1. **Fazer push no GitHub:**
   ```bash
   cd /Users/f.nuno/projetos/GestorEventos
   git add .
   git commit -m "Descrição das mudanças"
   git push origin main
   ```

2. **No PythonAnywhere - Bash Console:**
   ```bash
   cd ~/GestorEventos
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt  # Se mudou dependências
   ```

3. **Voltar na aba "Web" e clicar em "Reload"**

✅ App atualizada!

---

## 🆘 Troubleshooting

### Erro 502 Bad Gateway
- Vá em "Web" → "Error log"
- Leia os últimos erros
- Normalmente é problema no `wsgi.py` ou falta de dependências

### Botão "Conectar com Google" não funciona
- Verifique se adicionou o redirect URI no Google Cloud Console
- Verifique se o `credentials.json` foi carregado

### App não carrega
- Vá em "Web" → "Reload"
- Verifique "Error log"
- Verifique se o virtualenv está correto

---

## 📞 Links Úteis

- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **Flask on PythonAnywhere:** https://help.pythonanywhere.com/pages/Flask/
- **Forum:** https://www.pythonanywhere.com/forums/

---

## 🎯 Resumo Rápido

```bash
# 1. Criar conta
https://www.pythonanywhere.com/registration/register/beginner/

# 2. Clonar código (Bash console)
git clone https://github.com/anaritamindset/GestorEventos.git
cd GestorEventos
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py init_db

# 3. Configurar Web App
- Web → Add new web app
- Python 3.11 / Flask
- WSGI: /home/anaritamindset/GestorEventos/wsgi.py
- Virtualenv: /home/anaritamindset/GestorEventos/venv

# 4. Upload credentials.json via Files

# 5. Reload e aceder!
https://anaritamindset.pythonanywhere.com
```

---

**Desenvolvido por Ana Rita - Mindset Wellness**
**Deploy preparado com Claude Code**
**Hospedado gratuitamente no PythonAnywhere**
