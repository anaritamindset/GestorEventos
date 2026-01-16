# Sistema de Automação - Gestor Wellness

## 📋 Resumo da Implementação

Foi implementado um sistema completo de automação para o Gestor Wellness que integra Google Forms e Google Sheets, permitindo automatizar a gestão de eventos e participantes.

## ✨ Funcionalidades Implementadas

### 1. **Integração com Google APIs**
- ✅ Autenticação OAuth2 com Google
- ✅ Acesso a Google Forms API
- ✅ Acesso a Google Sheets API (leitura e escrita)
- ✅ Acesso a Google Drive API

### 2. **Gestão Automática de Eventos**
- ✅ Criação automática de Google Forms para inscrição em eventos
- ✅ Criação automática de Google Sheets para armazenar respostas
- ✅ Sincronização de respostas do formulário para a base de dados local
- ✅ Interface visual para gerir a automação

### 3. **Modelo de Dados Atualizado**
Adicionados novos campos ao modelo `Evento`:
- `google_form_id` - ID do Google Form associado
- `google_sheet_id` - ID do Google Sheet associado
- `auto_sync_enabled` - Flag para ativar/desativar sincronização automática

### 4. **Novas Rotas e Páginas**

#### Página de Gestão Automática (`/gestao_automatica`)
- Mostra status da conexão com Google
- Lista todos os eventos com seus status de automação
- Permite criar automação para eventos
- Permite sincronizar respostas manualmente

#### Rotas de Automação:
- `GET /gestao_automatica` - Página principal de automação
- `GET /google_authenticate` - Autenticação com Google
- `POST /create_event_automation/<evento_id>` - Criar Form e Sheet para evento
- `POST /sync_event_responses/<evento_id>` - Sincronizar respostas

## 🔧 Arquivos Criados/Modificados

### Novos Arquivos:
1. **`routes_automation.py`** - Rotas de automação
2. **`templates/gestao_automatica.html`** - Interface de gestão automática
3. **`migrations/`** - Sistema de migrações de base de dados

### Arquivos Modificados:
1. **`app/services/google_service.py`**
   - Expandidos os scopes para incluir Forms e Sheets (escrita)
   - Adicionados métodos:
     - `create_spreadsheet()` - Criar planilha
     - `append_to_spreadsheet()` - Adicionar dados à planilha
     - `create_event_form()` - Criar formulário de evento
     - `get_form_responses()` - Obter respostas do formulário

2. **`models.py`**
   - Adicionados campos de integração Google ao modelo Evento

3. **`app.py`**
   - Registado blueprint de automação

4. **`templates/menu_principal.html`**
   - Atualizado para mostrar "Gestão Local" e "Gestão Automática"
   - Removido badge "Em breve"
   - Link funcional para página de automação

## 🚀 Como Usar

### 1. Primeira Autenticação
1. Aceder ao menu principal
2. Clicar em "Gestão Automática"
3. Clicar em "Conectar com Google"
4. Autorizar a aplicação no browser
5. Será criado um ficheiro `token.pickle` com as credenciais

### 2. Automatizar um Evento
1. Na página de Gestão Automática
2. Encontrar o evento desejado
3. Clicar em "Automatizar"
4. Será criado:
   - Um Google Form com campos Nome e Email
   - Um Google Sheet para armazenar as respostas
5. Os links aparecem na tabela para acesso direto

### 3. Sincronizar Respostas
1. Quando houver novas inscrições no Google Form
2. Clicar em "Sincronizar" no evento
3. As respostas serão importadas para a base de dados
4. Participantes duplicados são ignorados

## 📝 Próximos Passos (Sugestões)

### Automação Adicional:
- [ ] Sincronização automática periódica (cron job)
- [ ] Envio automático de certificados após o evento
- [ ] Notificações por email quando há novas inscrições
- [ ] Dashboard com estatísticas de inscrições em tempo real
- [ ] Integração com Google Calendar para criar eventos
- [ ] Templates personalizáveis para formulários

### Melhorias:
- [ ] Validação de email no formulário
- [ ] Campos personalizados nos formulários
- [ ] Exportação de relatórios
- [ ] Histórico de sincronizações

## ⚙️ Configuração Necessária

### Credenciais Google:
É necessário ter um ficheiro `credentials.json` na raiz do projeto com as credenciais da Google Cloud Console. Para obter:

1. Aceder a [Google Cloud Console](https://console.cloud.google.com/)
2. Criar um projeto novo ou usar existente
3. Ativar as APIs:
   - Google Forms API
   - Google Sheets API
   - Google Drive API
4. Criar credenciais OAuth 2.0
5. Descarregar o ficheiro JSON como `credentials.json`

### Scopes Necessários:
```python
'https://www.googleapis.com/auth/spreadsheets'
'https://www.googleapis.com/auth/drive'
'https://www.googleapis.com/auth/forms.body'
'https://www.googleapis.com/auth/forms.responses.readonly'
```

## 🎯 Benefícios

1. **Redução de Trabalho Manual**: Criação automática de formulários e planilhas
2. **Centralização**: Todos os dados sincronizados numa única base de dados
3. **Rastreabilidade**: Histórico completo de inscrições
4. **Escalabilidade**: Fácil gerir múltiplos eventos simultaneamente
5. **Integração**: Aproveita o ecossistema Google que os utilizadores já conhecem

## 🔒 Segurança

- Autenticação OAuth2 segura
- Tokens armazenados localmente em `token.pickle`
- Permissões granulares (apenas o necessário)
- Validação de dados antes de inserir na BD

---

**Desenvolvido para**: Gestor Wellness  
**Data**: Janeiro 2026  
**Versão**: 1.0
