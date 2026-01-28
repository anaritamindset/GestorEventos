# 🎯 Gestor de Eventos v2.1

Sistema completo de gestão de eventos multi-tenant, participantes, certificados personalizados e automação com Google Forms/Sheets.

<img src="https://img.shields.io/badge/Flask-3.1.0-green" alt="Flask">
<img src="https://img.shields.io/badge/Python-3.14-blue" alt="Python">
<img src="https://img.shields.io/badge/SQLAlchemy-2.0-orange" alt="SQLAlchemy">
<img src="https://img.shields.io/badge/Google_APIs-Enabled-red" alt="Google APIs">
<img src="https://img.shields.io/badge/Multi--Tenant-✓-purple" alt="Multi-Tenant">

## ✨ Funcionalidades Principais

### 🏢 Multi-Tenancy (NOVO!)
- ✅ **Múltiplas organizações** no mesmo sistema
- ✅ **Branding personalizado** por organização (cores, logos, selos)
- ✅ **Certificados personalizados** com identidade visual única
- ✅ **Separação completa de dados** entre organizações
- ✅ **Homepage moderna** com seleção de organizações

### 📅 Gestão de Eventos
- ✅ Criar, editar e eliminar eventos
- ✅ Suporte para eventos multi-dia
- ✅ Importação de eventos via Excel
- ✅ Soft delete (eventos não são apagados permanentemente)

### 👥 Gestão de Participantes
- ✅ Adicionar participantes manualmente ou via Excel
- ✅ Controlo de presença
- ✅ Informações completas (nome, email, telefone, empresa)
- ✅ Observações personalizadas

### 🤖 Automação com Google (NOVO!)
- ✅ **Autenticação OAuth 2.0** com Google
- ✅ **Criação automática de Google Forms** para inscrições
- ✅ **Sincronização de respostas** dos formulários
- ✅ **Deteção de formulários existentes** no Google Drive
- ✅ **Extração automática de datas** dos nomes dos formulários
- ✅ **Associação de formulários existentes** a eventos

### 📄 Certificados
- ✅ Geração de certificados PDF personalizados
- ✅ **Branding por organização** (cores, logos, selos/lacres)
- ✅ Templates personalizáveis com identidade visual
- ✅ **Validação online** com QR codes
- ✅ Envio automático por email
- ✅ Download individual ou em lote

### 📊 Importação de Dados
- ✅ **Importação via Excel** (formato único ou múltiplos eventos)
- ✅ Validação automática de dados
- ✅ Suporte para formatos flexíveis de datas

## 🚀 Instalação Rápida

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/GestorEventos.git
cd GestorEventos
```

### 2. Criar Ambiente Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Google API (Opcional - Para Automação)
1. Aceda ao [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto e ative as APIs:
   - Google Forms API
   - Google Sheets API
   - Google Drive API
3. Crie credenciais OAuth 2.0
4. Baixe o ficheiro `credentials.json` para a raiz do projeto

📖 **Guia completo:** [docs/GOOGLE_SETUP.md](docs/GOOGLE_SETUP.md)

### 5. Executar a Aplicação
```bash
python3 run.py
```

Aceda a: **http://127.0.0.1:5000**

### 6. Configurar Organizações (Opcional)

Para adicionar ou modificar organizações:

```bash
# Editar configuração das organizações
nano seed_organizations.py

# Aplicar alterações à base de dados
python seed_organizations.py
```

O script `seed_organizations.py` permite configurar:
- Nome e subtítulo da organização
- Cores primária e secundária (branding)
- Logos (principal e selo/lacre)
- Configurações de email SMTP
- Assinaturas para certificados

## 🏢 Organizações Configuradas

O sistema atualmente suporta duas organizações:

### 🧘 Ana Rita - Mindset & Wellness
- **Foco**: Eventos de mindfulness e desenvolvimento pessoal
- **Cores**: Verde suave (#9DB5A5) + Lilás suave (#C8B8D8)
- **Email**: anaritamindset@gmail.com

### 🌿 ARdaTerra
- **Foco**: Eventos de aromaterapia e óleos essenciais
- **Cores**: Verde terra (#8B9D7C) + Castanho dourado (#D4A574)
- **Email**: ardoterra@gmail.com

## 📁 Estrutura do Projeto

```
GestorEventos/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── main.py          # Rotas principais e automação
│   ├── models/
│   │   ├── event.py             # Modelo de Eventos
│   │   ├── participant.py       # Modelo de Participantes
│   │   └── user.py              # Modelo de Utilizadores
│   ├── services/
│   │   ├── google_auth_service.py      # Autenticação Google OAuth
│   │   ├── google_forms_service.py     # Gestão de Google Forms
│   │   └── excel_import_service.py     # Importação de Excel
│   ├── templates/                # Templates Jinja2
│   └── static/                   # CSS, JS, imagens
├── docs/                         # Documentação
│   ├── GOOGLE_SETUP.md          # Setup Google APIs
│   ├── GOOGLE_ADICIONAR_URI.md  # Adicionar redirect URIs
│   └── AUTOMACAO_README.md      # Guia de automação
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## 🔐 Segurança

**IMPORTANTE:** Nunca commite ficheiros sensíveis para o repositório!

Ficheiros protegidos pelo `.gitignore`:
- ✅ `credentials.json` - Credenciais Google OAuth
- ✅ `token.json` - Token de autenticação Google
- ✅ `*.db` - Bases de dados SQLite
- ✅ `.env` - Variáveis de ambiente

## 📚 Documentação Adicional

- **[Configuração Google APIs](docs/GOOGLE_SETUP.md)** - Setup completo das APIs Google
- **[Adicionar Redirect URIs](docs/GOOGLE_ADICIONAR_URI.md)** - Configurar OAuth
- **[Guia de Automação](docs/AUTOMACAO_README.md)** - Usar Google Forms/Sheets
- **[Novas Funcionalidades](docs/NOVAS_FUNCIONALIDADES.md)** - Changelog completo

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| **Flask** | 3.1.0 | Framework web |
| **SQLAlchemy** | 2.0.40 | ORM para base de dados |
| **Pandas** | 2.2.3 | Processamento de Excel |
| **ReportLab** | 4.3.1 | Geração de PDFs |
| **Google APIs** | - | Forms, Sheets, Drive |

## 🎨 Interface

### Design Moderno e Elegante
- ✨ **Paleta de cores wellness** (verde-sálvia, lavanda, pêssego suave)
- 📱 **100% Responsivo** (desktop, tablet, mobile)
- 🎯 **Navegação intuitiva** com dropdown menus
- 🎨 **Gradientes suaves** e sombras elegantes
- ⚡ **Transições animadas** e feedback visual imediato
- 📋 **Formulários modernos** com validação em tempo real
- 🃏 **Cards interativos** com efeitos hover

### Componentes UI
- **Homepage**: Seleção de organizações com logos e branding
- **Formulários**: Layout em grid de 2 colunas, radio buttons estilizados
- **Navegação**: Dropdown elegante com indicadores de página ativa
- **Tabelas**: Ordenação, pesquisa e paginação integradas
- **Modais**: Confirmações e avisos com design consistente

## 🤝 Contribuir

Contribuições são bem-vindas! Para contribuir:

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📧 Suporte

Em caso de dúvidas ou problemas:
- 📧 Email: anaritamindset@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/GestorEventos/issues)

## 📝 Licença

Este projeto está sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido com ❤️ por Ana Rita** | [Website](https://anaritamindset.com) 