# Corrigir Erro: redirect_uri_mismatch

## Problema
Erro 400: redirect_uri_mismatch ao tentar autenticar com Google.

## Solução Rápida

### Opção 1: Adicionar URI no Google Cloud Console (RECOMENDADO)

1. Aceda a [Google Cloud Console](https://console.cloud.google.com/)
2. Vá a "APIs & Services" > "Credentials"
3. Clique nas credenciais OAuth 2.0 que criou
4. Na secção "Authorized redirect URIs", adicione **TODOS** estes URIs:
   ```
   http://localhost:5000/google/callback
   http://127.0.0.1:5000/google/callback
   http://localhost/google/callback
   ```
5. Clique em "SAVE"
6. Aguarde 5 minutos (pode demorar até as alterações propagarem)
7. Tente autenticar novamente

### Opção 2: Verificar credentials.json

Abra o ficheiro `credentials.json` e verifique se tem:

```json
{
  "web": {
    "redirect_uris": [
      "http://localhost:5000/google/callback",
      "http://127.0.0.1:5000/google/callback"
    ]
  }
}
```

Se não tiver, baixe novamente o ficheiro do Google Cloud Console após adicionar os URIs.

### Opção 3: Usar ngrok (para produção/testes externos)

Se quiser testar com um URL público:

1. Instale ngrok: `brew install ngrok`
2. Execute: `ngrok http 5000`
3. Copie o URL HTTPS fornecido (ex: https://abc123.ngrok.io)
4. Adicione no Google Cloud Console: `https://abc123.ngrok.io/google/callback`
5. Aceda à aplicação através do URL do ngrok

## Verificação

Depois de adicionar os URIs no Google Cloud Console:

1. Aceda a: http://127.0.0.1:5000/gestao_automatica
2. Clique em "Conectar com Google"
3. Deve funcionar sem erros

## URIs Necessários

Para desenvolvimento local, certifique-se que tem **TODOS** estes URIs no Google Cloud Console:

✓ `http://localhost:5000/google/callback`
✓ `http://127.0.0.1:5000/google/callback`
✓ `http://localhost/google/callback`

## Ainda com Problemas?

Se ainda tiver erros, limpe a cache do browser:
- Chrome: Ctrl+Shift+Delete > Cookies
- Safari: Preferências > Privacidade > Gerir dados de websites
- Firefox: Ctrl+Shift+Delete > Cookies

Depois tente novamente.
