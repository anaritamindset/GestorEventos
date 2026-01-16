# 🔒 Credenciais e Segurança - Gestor Wellness

## ⚠️ IMPORTANTE - INFORMAÇÃO CONFIDENCIAL

Este documento contém informações sobre a localização e gestão de credenciais sensíveis do projeto.

## 📍 Localização das Credenciais

### 1. **Credenciais OAuth do Google**

**Ficheiro**: `credentials.json` (na raiz do projeto)
- ✅ Protegido pelo `.gitignore`
- ✅ NÃO será enviado para repositórios Git
- 🔑 Client ID: Obtido da Google Cloud Console
- 🔐 Client Secret: Armazenado de forma segura no ficheiro

**Uso**: Autenticação inicial com Google APIs (Forms, Sheets, Drive)

### 2. **Token de Acesso Google**

**Ficheiro**: `token.pickle` (criado após primeira autenticação)
- ✅ Protegido pelo `.gitignore`
- ✅ NÃO será enviado para repositórios Git
- 🔄 Renovado automaticamente quando expira
- 📝 Contém o token OAuth2 para acesso às APIs

**Criação**: Gerado automaticamente ao clicar em "Conectar com Google"

### 3. **Credenciais de Email**

**Ficheiro**: `.env` (na raiz do projeto)
- ✅ Protegido pelo `.gitignore`
- ✅ NÃO será enviado para repositórios Git

**Conteúdo**:
```
EMAIL_USER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_app_google
GOOGLE_CLIENT_ID=seu_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu_client_secret
```

## 🛡️ Medidas de Segurança Implementadas

### ✅ Proteção de Ficheiros
1. **`.gitignore`** configurado para excluir:
   - `.env`
   - `credentials.json`
   - `token.pickle`
   - Base de dados (`*.db`, `*.sqlite`)
   - Uploads e certificados

### ✅ Boas Práticas
- Credenciais nunca hardcoded no código
- Uso de variáveis de ambiente
- Tokens armazenados localmente
- OAuth2 para autenticação segura

## 🔄 Backup das Credenciais

### Onde fazer backup (SEGURO):
1. ✅ Gestor de passwords (1Password, LastPass, Bitwarden)
2. ✅ Ficheiro encriptado local
3. ✅ Cofre digital pessoal

### Onde NÃO fazer backup:
1. ❌ Repositórios Git (GitHub, GitLab, etc.)
2. ❌ Email
3. ❌ Serviços de cloud públicos não encriptados
4. ❌ Mensagens de chat

## 🔧 Recuperação de Credenciais

### Se perder o `credentials.json`:
1. Aceder à [Google Cloud Console](https://console.cloud.google.com/)
2. Ir para "APIs & Services" > "Credentials"
3. Encontrar o OAuth 2.0 Client ID
4. Fazer download do JSON novamente

### Se perder o `token.pickle`:
- Não há problema! Será recriado na próxima autenticação
- Basta clicar em "Conectar com Google" novamente

### Se perder a senha de email:
1. Aceder às configurações da conta Google
2. Ir para "Segurança" > "Senhas de apps"
3. Gerar nova senha de app
4. Atualizar no ficheiro `.env`

## 📋 Checklist de Segurança

Antes de partilhar o projeto:
- [ ] Verificar que `.gitignore` está ativo
- [ ] Confirmar que `.env` não está no Git
- [ ] Confirmar que `credentials.json` não está no Git
- [ ] Confirmar que `token.pickle` não está no Git
- [ ] Remover quaisquer credenciais hardcoded

## 🚨 Em Caso de Comprometimento

Se suspeitar que as credenciais foram expostas:

### Google OAuth:
1. Aceder à [Google Cloud Console](https://console.cloud.google.com/)
2. Revogar o Client ID atual
3. Criar novo OAuth Client ID
4. Atualizar `credentials.json`
5. Apagar `token.pickle`
6. Fazer nova autenticação

### Email:
1. Aceder às configurações da conta Google
2. Revogar a senha de app atual
3. Gerar nova senha de app
4. Atualizar `.env`

## 📞 Contactos Úteis

- **Google Cloud Support**: https://cloud.google.com/support
- **Google Account Security**: https://myaccount.google.com/security

---

**Última atualização**: 13 de janeiro de 2026  
**Responsável**: Fernando Nuno  
**Projeto**: Gestor Wellness - Sistema de Automação
