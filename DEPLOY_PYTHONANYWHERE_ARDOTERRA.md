# 🚀 Deploy GestorEventos - ARdoTerra

**Username:** ARdoTerra
**URL:** https://ARdoTerra.pythonanywhere.com

---

## ✅ Passo 1: Fazer Upload do Código

### Opção A - Via GitHub (Recomendado)

1. **Abra um Bash Console:**
   - No PythonAnywhere, clique em **"Consoles"** no menu
   - Clique em **"Bash"**

2. **Clone o repositório:**
   ```bash
   git clone https://github.com/anaritamindset/GestorEventos.git
   cd GestorEventos
   ```

3. **Criar ambiente virtual com Python 3.11:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Inicializar base de dados:**
   ```bash
   flask init-db
   ```

---

## 🔧 Passo 2: Configurar WSGI File

1. **No PythonAnywhere, vá na aba "Web"**

2. **Clique no link:** `/var/www/ardoterra_pythonanywhere_com_wsgi.py`

3. **Substitua TODO o conteúdo** pelo código abaixo:

```python
import sys
import os

# Caminho do projeto
project_home = '/home/ARdoTerra/GestorEventos'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Configurações de ambiente
os.environ['FLASK_ENV'] = 'production'
os.environ['DEBUG'] = 'False'

# Ativar virtualenv
activate_this = '/home/ARdoTerra/GestorEventos/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Import da aplicação Flask
from run import app as application
```

4. **Clique em "Save"** (Ctrl+S ou botão)

---

## 📁 Passo 3: Configurar Virtualenv

1. **Volte para a aba "Web"**

2. **Na seção "Virtualenv"**, no campo **"Enter path to a virtualenv"**, coloque:
   ```
   /home/ARdoTerra/GestorEventos/venv
   ```

3. **Clique no ✓** (tick) para confirmar

---

## 🔄 Passo 4: Configurar Source Code e Working Directory

1. **Na seção "Code":**

   - **Source code:** `/home/ARdoTerra/GestorEventos`
   - **Working directory:** `/home/ARdoTerra/GestorEventos`

---

## 📤 Passo 5: Upload do credentials.json

1. **Vá em "Files" no menu**

2. **Navegue até:** `/home/ARdoTerra/GestorEventos/`

3. **Clique em "Upload a file"**

4. **Selecione o arquivo** `credentials.json` do teu computador
   - Localização: `/Users/f.nuno/projetos/GestorEventos/credentials.json`

5. **Faça upload**

---

## 🌐 Passo 6: Atualizar Google OAuth Redirect URI

1. **Acesse:** https://console.cloud.google.com/apis/credentials

2. **Selecione o OAuth 2.0 Client ID** usado no projeto

3. **Em "Authorized redirect URIs"**, adicione:
   ```
   https://ARdoTerra.pythonanywhere.com/google/callback
   ```

4. **Clique em "Save"**

---

## 🚀 Passo 7: Reload e Testar!

1. **Volte para a aba "Web"**

2. **Clique no botão verde:**
   ```
   Reload ARdoTerra.pythonanywhere.com
   ```

3. **Aguarde 10 segundos**

4. **Acesse:**
   ```
   https://ARdoTerra.pythonanywhere.com
   ```

---

## 🔐 Login Padrão

Depois que o site carregar:

- **Email:** `admin@gestorev2.local`
- **Password:** `admin123`

⚠️ **IMPORTANTE:** Depois do primeiro login:
1. Vá em "Utilizadores"
2. Mude a senha do admin
3. Crie utilizador para Ana Rita

---

## 🐛 Se der erro...

### Ver os logs de erro:

1. **Na aba "Web"**, clique em:
   - **Error log:** `ardoterra.pythonanywhere.com.error.log`

2. **Leia as últimas linhas** para ver o erro

### Erros comuns:

**"ImportError: No module named 'app'"**
- Verifique se o virtualenv está correto: `/home/ARdoTerra/GestorEventos/venv`
- Verifique se o Source code está correto: `/home/ARdoTerra/GestorEventos`

**"credentials.json not found"**
- Verifique se fez upload do `credentials.json`
- Deve estar em: `/home/ARdoTerra/GestorEventos/credentials.json`

**"Database not found"**
- Abra Bash console e rode:
  ```bash
  cd ~/GestorEventos
  source venv/bin/activate
  flask init-db
  ```

---

## 🔄 Como Atualizar Depois

Quando fizer mudanças no código:

1. **Bash Console:**
   ```bash
   cd ~/GestorEventos
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt  # Se mudou dependências
   ```

2. **Aba "Web" → Reload**

---

## 📝 Resumo dos Comandos

```bash
# 1. Clonar código
cd ~
git clone https://github.com/anaritamindset/GestorEventos.git
cd GestorEventos

# 2. Criar virtualenv
python3.11 -m venv venv
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Inicializar base de dados
flask init-db

# 5. Depois, configurar:
# - WSGI file: /var/www/ardoterra_pythonanywhere_com_wsgi.py
# - Virtualenv: /home/ARdoTerra/GestorEventos/venv
# - Source code: /home/ARdoTerra/GestorEventos
# - Working directory: /home/ARdoTerra/GestorEventos
# - Upload credentials.json
# - Reload!
```

---

## ✅ Checklist Final

- [ ] Git clone feito
- [ ] Virtualenv criado (`venv`)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Base de dados inicializada (`flask init-db`)
- [ ] WSGI file configurado
- [ ] Virtualenv configurado na aba Web
- [ ] Source code e Working directory configurados
- [ ] credentials.json carregado
- [ ] Google OAuth redirect URI atualizado
- [ ] Reload feito
- [ ] Site testado e funcionando!

---

**Desenvolvido por Ana Rita - Mindset Wellness**
**Deploy: ARdoTerra.pythonanywhere.com**
