# Estrutura do Projeto - GestorEventos v2.0

## 📁 Arquivos Raiz

```
GestorEventos/
├── run.py                      # Script principal para iniciar a aplicação
├── requirements.txt            # Dependências Python
├── .gitignore                  # Arquivos ignorados pelo Git
├── LICENSE                     # Licença MIT
├── README.md                   # Documentação principal
├── credentials.json.example    # Exemplo de credenciais Google (NÃO COMMITAR credentials.json!)
├── iniciar_gestor_eventos.command  # Script macOS para iniciar
└── start.sh                    # Script Linux/macOS para iniciar
```

## 📁 Diretórios Principais

### `/app` - Aplicação Principal
```
app/
├── __init__.py                 # Inicialização da aplicação Flask
├── api/
│   └── routes/
│       └── main.py             # Todas as rotas (eventos, participantes, automação)
├── models/
│   ├── event.py                # Modelo de Eventos
│   ├── participant.py          # Modelo de Participantes  
│   ├── user.py                 # Modelo de Utilizadores
│   └── certificate_template.py # Templates de certificados
├── services/
│   ├── google_auth_service.py  # Autenticação OAuth Google
│   ├── google_forms_service.py # Gestão de Google Forms
│   └── excel_import_service.py # Importação de Excel
└── utils/
    └── certificate_generator.py # Geração de certificados PDF
```

### `/templates` - Templates HTML
```
templates/
├── base.html                   # Template base
├── menu_principal.html         # Página inicial
├── eventos.html                # Listagem de eventos
├── criar_evento.html           # Criar novo evento
├── editar_evento.html          # Editar evento
├── detalhe_evento.html         # Detalhes do evento
├── gestao_automatica.html      # Automação Google (NOVO!)
├── utilizadores.html           # Gestão de utilizadores
└── ...
```

### `/static` - Arquivos Estáticos
```
static/
├── css/
│   └── style.css               # Estilos personalizados
└── icons/                      # Ícones e imagens
```

### `/docs` - Documentação
```
docs/
├── GOOGLE_SETUP.md             # Setup Google APIs (IMPORTANTE!)
├── GOOGLE_ADICIONAR_URI.md     # Configurar redirect URIs
├── GOOGLE_FIX_REDIRECT.md      # Troubleshooting
├── AUTOMACAO_README.md         # Guia de automação
├── NOVAS_FUNCIONALIDADES.md    # Changelog
├── SEGURANCA_CREDENCIAIS.md    # Segurança
└── STATUS.md                   # Status do projeto
```

### `/Logos` - Logotipos
```
Logos/
├── ana_rita_m&w_logo_cor.jpeg  # Logo colorido
├── ana_rita_m&w_logo_bw.jpeg   # Logo preto e branco
├── ana_rita_m&w_logo_trnsp.png # Logo transparente
└── ARdaTerra_logo.png          # Logo alternativo
```

### `/exemplos` - Arquivos de Exemplo
```
exemplos/
├── exemplo_import_evento.xlsx  # Exemplo de importação simples
└── exemplo_multi_eventos.xlsx  # Exemplo de múltiplos eventos
```

### `/migrations` - Migrações de Base de Dados
```
migrations/
├── alembic.ini                 # Configuração Alembic
├── env.py                      # Ambiente de migração
└── versions/                   # Versões de migração
```

## 🚫 Arquivos NÃO Versionados (.gitignore)

Estes arquivos são gerados localmente e NÃO devem ser commitados:

```
# Credenciais (SENSÍVEL!)
credentials.json                # Credenciais Google OAuth
token.json                      # Token de autenticação Google
.env                            # Variáveis de ambiente

# Base de Dados
*.db                            # SQLite databases
gestorev2.db

# Python
__pycache__/                    # Cache Python
*.pyc
venv/                           # Ambiente virtual

# Uploads e Gerados
uploads/                        # Arquivos enviados
certificados/                   # Certificados gerados
*.log                           # Logs
```

## 🔐 Arquivos Sensíveis - IMPORTANTE!

### ⚠️ NUNCA commite estes arquivos:

1. **`credentials.json`** - Contém client_id e client_secret do Google
2. **`token.json`** - Token de autenticação gerado após login
3. **`*.db`** - Bases de dados com dados dos clientes
4. **`.env`** - Variáveis de ambiente (emails, passwords)

### ✅ Use em vez disso:

- `credentials.json.example` - Template sem dados sensíveis
- `.env.example` - Template de variáveis de ambiente

## 📝 Como Adicionar Novas Funcionalidades

### 1. Nova Rota
Adicionar em: `app/api/routes/main.py`

### 2. Novo Modelo
Criar em: `app/models/seu_modelo.py`

### 3. Novo Serviço
Criar em: `app/services/seu_servico.py`

### 4. Nova Página
Criar template em: `templates/sua_pagina.html`

## 🚀 Comandos Úteis

```bash
# Iniciar aplicação
python3 run.py

# Criar migração
flask db migrate -m "descrição"

# Aplicar migração
flask db upgrade

# Instalar dependências
pip install -r requirements.txt

# Atualizar dependências
pip freeze > requirements.txt
```

## 📚 Documentação de Referência

- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **Google APIs**: https://developers.google.com/apis-explorer
- **ReportLab**: https://www.reportlab.com/docs/reportlab-userguide.pdf

---

**Última atualização:** 15 de Janeiro de 2026  
**Versão:** 2.0  
**Autor:** Ana Rita - Mindset Wellness
