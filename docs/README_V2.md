# GestorEventos v2.0

Sistema moderno de gestão de eventos com API RESTful, autenticação e funcionalidades avançadas.

## Novidades da v2.0

### Melhorias de Arquitetura
- Estrutura modular com separação clara de responsabilidades
- API RESTful para integração com outras aplicações
- Application Factory Pattern para melhor testabilidade
- Suporte para CORS (Cross-Origin Resource Sharing)

### Novas Funcionalidades
- Sistema de autenticação com roles (admin, organizer, viewer)
- Templates de certificados personaliz\u00e1veis
- Sistema de auditoria completo (quem fez o quê e quando)
- Check-in/check-out de participantes
- QR codes nos certificados para validação
- Suporte para eventos multi-dia
- Capacidade máxima de participantes
- Status de eventos (planejado, em andamento, concluído, cancelado)
- Soft deletes (não apaga permanentemente)
- Campos adicionais para participantes (telefone, empresa, observações)

### Melhorias de Base de Dados
- Timestamps automáticos (created_at, updated_at)
- Relacionamentos otimizados com cascade
- Índices para queries mais rápidas
- Suporte para JSON (configurações de templates)

## Estrutura do Projeto

```
GestorEventos/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── event.py
│   │   ├── participant.py
│   │   ├── certificate_template.py
│   │   └── audit_log.py
│   ├── api/                 # API routes
│   │   └── routes/
│   │       ├── events.py
│   │       ├── participants.py
│   │       ├── users.py
│   │       ├── certificates.py
│   │       └── web.py
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── templates/               # Jinja2 templates (v2.0)
├── static/                  # CSS, JS, images
├── migrations/              # Database migrations
├── v1_backup/               # Backup da v1.0
├── run.py                   # Entry point
├── requirements_v2.txt      # Dependencies
└── README_V2.md            # This file
```

## Instalação

### 1. Criar ambiente virtual (se não existir)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependências da v2.0
```bash
pip install -r requirements_v2.txt
```

### 3. Configurar variáveis de ambiente
Crie um ficheiro `.env`:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URI=sqlite:///gestorev2.db

EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 4. Inicializar base de dados
```bash
python run.py init-db
```

Isto cria:
- Todas as tabelas necessárias
- Utilizador admin (admin@gestorev2.local / admin123)
- Template de certificado padrão

## Como Executar

```bash
python run.py
```

A aplicação estará disponível em: http://127.0.0.1:5000

## Credenciais Padrão

- **Email:** admin@gestorev2.local
- **Password:** admin123

**IMPORTANTE:** Altere a password após o primeiro login!

## API Endpoints

### Eventos
- `GET /api/events` - Listar todos os eventos
- `GET /api/events/<id>` - Obter evento específico
- `POST /api/events` - Criar novo evento
- `PUT /api/events/<id>` - Atualizar evento
- `DELETE /api/events/<id>` - Apagar evento

### Participantes
- `GET /api/events/<id>/participants` - Listar participantes do evento
- `POST /api/events/<id>/participants` - Adicionar participante
- `PUT /api/participants/<id>` - Atualizar participante
- `DELETE /api/participants/<id>` - Remover participante
- `POST /api/participants/<id>/checkin` - Fazer check-in
- `POST /api/participants/<id>/checkout` - Fazer check-out

### Certificados
- `POST /api/certificates/generate/<participant_id>` - Gerar certificado
- `POST /api/certificates/send/<participant_id>` - Enviar certificado por email
- `POST /api/certificates/bulk-generate/<event_id>` - Gerar certificados em lote

### Utilizadores
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/users` - Listar utilizadores (admin only)
- `POST /api/users` - Criar utilizador (admin only)

## Modelos de Dados

### User
- nome_completo, email, password_hash
- role: admin, organizer, viewer
- is_active, timestamps, soft delete

### Event
- nome, descrição, datas, duração, local, formadora
- tipo_evento, status, capacidade_maxima
- template_id, timestamps, soft delete

### Participant
- nome, email, telefone, empresa
- status, check-in/out times
- certificado info, observações
- timestamps, soft delete

### CertificateTemplate
- nome, descrição, config (JSON)
- is_active, is_default
- timestamps

### AuditLog
- user_id, action, entity_type, entity_id
- details (JSON), IP, timestamp

## Migrações de Base de Dados

```bash
# Criar uma migração
flask db migrate -m "Description of changes"

# Aplicar migrações
flask db upgrade

# Reverter migração
flask db downgrade
```

## Desenvolvimento

### Executar testes
```bash
pytest
```

### Cobertura de testes
```bash
pytest --cov=app tests/
```

### Formatar código
```bash
black app/
```

### Lint
```bash
flake8 app/
```

## Comparação v1.0 vs v2.0

| Funcionalidade | v1.0 | v2.0 |
|----------------|------|------|
| Arquitetura | Monolítica | Modular |
| API | Não | REST API |
| Autenticação | Não | Sim (JWT) |
| Roles | Não | Sim (3 níveis) |
| Templates certificados | Fixo | Personalizável |
| Auditoria | Não | Completa |
| Check-in/out | Não | Sim |
| QR codes | Não | Sim |
| Soft deletes | Não | Sim |
| Timestamps | Parcial | Completo |
| Testes | Não | Sim |
| Capacidade eventos | Não | Sim |
| Eventos multi-dia | Limitado | Completo |

## Migração da v1.0 para v2.0

Um script de migração será fornecido para:
1. Migrar dados da base de dados v1.0 para v2.0
2. Criar utilizador admin
3. Criar template padrão baseado nas configurações v1.0

## Roadmap v2.1

- [ ] Dashboard com estatísticas e gráficos
- [ ] Notificações em tempo real
- [ ] Integração com calendário (Google Calendar, Outlook)
- [ ] App mobile (React Native)
- [ ] Relatórios avançados com filtros
- [ ] Export multi-formato (PDF, Excel, CSV)
- [ ] Integração com pagamentos
- [ ] Sistema de inscrições online

## Suporte

Para questões ou problemas, contactar Fernando Nuno Vieira.

## Licença

Proprietário - © 2026 Fernando Nuno Vieira
