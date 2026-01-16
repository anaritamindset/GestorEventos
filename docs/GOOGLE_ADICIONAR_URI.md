# Como Adicionar o Redirect URI no Google Cloud Console

## ⚠️ URI Necessário
```
http://127.0.0.1:5000/google/callback
```

## 📋 Passo a Passo (5 minutos)

### 1. Aceder ao Google Cloud Console
Abra o browser e vá para:
```
https://console.cloud.google.com/
```

### 2. Ir para Credentials
- No menu lateral esquerdo, clique em **"APIs & Services"**
- Depois clique em **"Credentials"**

### 3. Editar as Credenciais OAuth 2.0
Na página de Credentials, encontre a secção **"OAuth 2.0 Client IDs"**

Verá algo como:
```
Web client 1
Client ID: 123456789-abc...
```

**Clique no nome** (ex: "Web client 1") OU clique no ícone do **lápis** ✏️ à direita

### 4. Adicionar o Redirect URI

Na página de edição:

1. Desça até encontrar a secção **"Authorized redirect URIs"**

2. Clique no botão **"+ ADD URI"**

3. Cole exatamente este URI na caixa que aparece:
   ```
   http://127.0.0.1:5000/google/callback
   ```

4. (Opcional) Adicione também este URI alternativo:
   ```
   http://localhost:5000/google/callback
   ```

### 5. Salvar as Alterações

1. No fundo da página, clique no botão azul **"SAVE"**

2. Aguarde a mensagem de confirmação:
   ```
   ✓ OAuth client updated
   ```

### 6. Aguardar Propagação (IMPORTANTE!)

⏱️ **Aguarde 5 minutos** antes de testar novamente.

As alterações no Google podem demorar alguns minutos a propagar globalmente.

### 7. Testar a Autenticação

Depois de aguardar 5 minutos:

1. Abra o browser e vá para:
   ```
   http://127.0.0.1:5000/gestao_automatica
   ```

2. Clique no botão **"Conectar com Google"**

3. Autorize a aplicação quando solicitado

4. ✅ **Sucesso!** Será redirecionado de volta com a mensagem:
   ```
   Autenticação com Google realizada com sucesso!
   ```

## 🔍 Verificar URIs Configurados

Para confirmar que adicionou corretamente:

1. Volte à página de edição das credenciais OAuth
2. Na secção "Authorized redirect URIs", deve ver:
   ```
   ✓ http://127.0.0.1:5000/google/callback
   ✓ http://localhost:5000/google/callback (opcional)
   ```

## ❌ Ainda com Erros?

### Erro: "redirect_uri_mismatch"
- Verifique se copiou o URI **EXATAMENTE** como mostrado (incluindo http://)
- Aguarde 5-10 minutos após salvar
- Limpe a cache do browser (Ctrl+Shift+Delete)

### Erro: "Access blocked: This app's request is invalid"
- Vá para "OAuth consent screen"
- Adicione seu email (f.nuno.ss@gmail.com) na secção **"Test users"**
- Clique em "SAVE"

### Erro: "Credentials file not found"
- Baixe o ficheiro `credentials.json` do Google Cloud Console
- Coloque na raiz do projeto: `/Users/f.nuno/projetos/GestorEventos/credentials.json`

## 📸 Screenshots de Referência

A página de edição deve parecer com isto:

```
Edit OAuth client ID

Application type: Web application
Name: [Web client 1]

Authorized JavaScript origins
[Lista de origens...]

Authorized redirect URIs
http://127.0.0.1:5000/google/callback  [✕]
http://localhost:5000/google/callback  [✕]
                                       [+ ADD URI]

[CANCEL]  [SAVE]
```

## ✅ Checklist Final

Antes de testar, confirme:

- [ ] Adicionou `http://127.0.0.1:5000/google/callback` nos redirect URIs
- [ ] Clicou em "SAVE" no Google Cloud Console
- [ ] Aguardou pelo menos 5 minutos
- [ ] Adicionou seu email como "Test user" (se a app estiver em modo de teste)
- [ ] O ficheiro `credentials.json` está na raiz do projeto
- [ ] O servidor Flask está a correr em http://127.0.0.1:5000

Pronto! Agora pode usar a Gestão Automática! 🎉
