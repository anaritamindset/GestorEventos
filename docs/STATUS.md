# Status do Projeto - Gestor de Eventos Wellness

**Data**: 14 de Janeiro de 2026
**Versão**: 2.0
**Status**: ✅ Funcional

---

## 📋 Resumo

Sistema de gestão de eventos wellness com suporte para importação de eventos via Excel. O sistema suporta tanto eventos únicos quanto múltiplos eventos no mesmo ficheiro.

---

## 🎯 Funcionalidades Implementadas

### ✅ Gestão de Eventos
- [x] Criar eventos manualmente via formulário web
- [x] Listar todos os eventos
- [x] Ver detalhes de evento com participantes
- [x] Editar eventos existentes
- [x] Apagar eventos (soft delete)

### ✅ Importação de Excel
- [x] **Formato Single Event** (2 sheets separadas):
  - Sheet 1: Informação do Evento (key-value pairs)
  - Sheet 2: Participantes (tabela)

- [x] **Formato Multi-Event** (cada sheet = 1 evento):
  - Info do evento no topo (key-value pairs)
  - Participantes em baixo (tabela com headers)
  - Suporte para múltiplos eventos no mesmo ficheiro

### ✅ Campos Suportados

**Evento:**
- Nome (obrigatório)
- Data (DD/MM/YY ou DD/MM/YYYY)
- Duração (em minutos, convertido para horas)
- Descrição
- Formadora
- Local

**Participantes:**
- Nome (obrigatório)
- Email
- Telefone
- Empresa
- Observações

---

## 🗂️ Estrutura do Projeto

```
GestorEventos/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── event.py          # Model v2 (data_inicio, data_fim, duracao_horas)
│   │   ├── participant.py
│   │   └── user.py
│   ├── services/
│   │   └── excel_import_service.py  # ✅ Corrigido e melhorado
│   └── api/
│       └── routes/
│           └── main.py       # ✅ Suporta multi-event
├── templates/
│   ├── base.html             # ✅ Menu limpo (sem Utilizadores)
│   ├── menu_principal.html
│   ├── eventos.html
│   ├── criar_evento.html     # Com upload de Excel
│   ├── detalhe_evento.html
│   └── editar_evento.html
├── instance/
│   └── app.db               # SQLite database
├── uploads/                 # Temp files (auto-cleanup)
├── venv/                    # Python virtual environment
├── run.py                   # Entry point
├── requirements_v2.txt      # Dependencies
└── exemplo_multi_eventos.xlsx  # ✅ Ficheiro de exemplo
```

---

## 🐛 Problemas Corrigidos

### Issue #1: Excel Import Failing
**Problema**: Ao carregar ficheiro Excel, campos `nome` e `data` retornavam vazios.

**Causa Raiz**:
1. Pandas estava a usar primeira linha como header (transformando "Nome" em coluna)
2. Parser não suportava formato de data DD/MM/YY (só DD/MM/YYYY)

**Solução**:
```python
# excel_import_service.py linha 99
event_df = pd.read_excel(excel_file, sheet_name=0, header=None)

# Adicionado formato de data de 2 dígitos (linhas 231-240)
date_formats = [
    '%d/%m/%y',      # DD/MM/YY (e.g., 15/01/26)
    '%d-%m-%y',
    '%d/%m/%Y',      # DD/MM/YYYY
    # ...
]
```

### Issue #2: Model Field Mismatch
**Problema**: Código usava campos do modelo v1 (`data`, `duracao`) mas BD tinha modelo v2.

**Solução**:
```python
# main.py linhas 117-133
evento = Event(
    nome=event_data.get('nome', 'Evento Importado'),
    data_inicio=data_inicio,      # v2 field
    data_fim=data_fim,            # v2 field
    duracao_horas=duracao_horas,  # v2 field (convertido de minutos)
    # ...
)
```

### Issue #3: Menu com Utilizadores
**Problema**: Menu tinha link para Utilizadores que não estava a ser usado.

**Solução**:
```html
<!-- base.html linha 126-128 -->
<div class="nav-menu">
    <a href="{{ url_for('main.index') }}">Início</a>
    <a href="{{ url_for('main.eventos') }}">Eventos</a>
    <!-- Utilizadores removido -->
</div>
```

---

## 📊 Modelos de Dados (v2)

### Event
```python
id              Integer (PK)
nome            String(200) NOT NULL
descricao       Text
data_inicio     Date NOT NULL         # ⚠️ NOT NULL
data_fim        Date (nullable)
duracao_horas   Integer NOT NULL
local           String(200)
formadora       String(100)
tipo_evento     String(50) = 'formacao'
status          String(50) = 'planejado'
deleted_at      DateTime (soft delete)
created_at      DateTime
updated_at      DateTime
```

### Participant
```python
id              Integer (PK)
evento_id       Integer (FK -> Event)
nome            String(200) NOT NULL
email           String(200)
telefone        String(20)
empresa         String(200)
observacoes     Text
deleted_at      DateTime (soft delete)
created_at      DateTime
updated_at      DateTime
```

---

## 📁 Formato de Ficheiros Excel

### Opção A: Single Event (Formato Antigo)
```
Sheet 1: "Informação do Evento"
┌──────────────┬──────────────────────────┐
│ Nome         │ Workshop Óleos Essenciais│
│ Data         │ 15/01/26                 │
│ Duração      │ 120                      │
│ Descrição    │ Workshop introdutório... │
│ Formadora    │ Ana Rita Vieira          │
│ Local        │ Centro Wellness Lisboa   │
└──────────────┴──────────────────────────┘

Sheet 2: "Participantes"
┌──────────────┬──────────────────────┬────────────┬──────────┬──────────────┐
│ Nome         │ Email                │ Telefone   │ Empresa  │ Observações  │
├──────────────┼──────────────────────┼────────────┼──────────┼──────────────┤
│ Maria Silva  │ maria.silva@email.com│ 912345678  │ Empresa A│ ...          │
│ João Santos  │ joao.santos@email.com│ 913456789  │ Empresa B│              │
└──────────────┴──────────────────────┴────────────┴──────────┴──────────────┘
```

### Opção B: Multi-Event (Formato Novo) ✨
```
Sheet "Evento 1"
┌──────────────┬──────────────────────────┐
│ Nome         │ Workshop Óleos Essenciais│
│ Data         │ 15/01/26                 │
│ Duração      │ 120                      │
│ Formadora    │ Ana Rita Vieira          │
│ Local        │ Centro Wellness Lisboa   │
├──────────────┴──────────────────────────┤
│              (linha vazia)               │
├──────────────┬──────────────────────────┤
│ Nome         │ Email                │...│ <- Header
├──────────────┼──────────────────────┼───┤
│ Maria Silva  │ maria.silva@email.com│...│
│ João Santos  │ joao.santos@email.com│...│
└──────────────┴──────────────────────┴───┘

Sheet "Evento 2"
(mesma estrutura)
```

---

## 🚀 Como Usar

### Iniciar Aplicação
```bash
cd /Users/f.nuno/projetos/GestorEventos
source venv/bin/activate
python3 run.py
```

Aceder: http://localhost:5000

### Importar Eventos via Excel

1. **Criar/Abrir ficheiro Excel** com um dos formatos suportados
2. **Navegar**: Início → Eventos → "Criar Novo Evento"
3. **Upload**: Secção "Importar de Excel" → Escolher ficheiro → "Importar Excel"
4. **Resultado**:
   - Single event: Redireciona para detalhes do evento criado
   - Multi-event: Redireciona para lista de eventos

### Ficheiros de Exemplo
- `exemplo_import_evento.xlsx` - Single event (1 evento, 5 participantes)
- `exemplo_multi_eventos.xlsx` - Multi-event (2 eventos, 5 participantes total)

---

## 🔧 Configuração Técnica

### Dependências Principais
```
Flask==3.1.0
Flask-SQLAlchemy==3.1.1
pandas==2.2.3
openpyxl==3.1.5
Werkzeug==3.1.3
```

### Base de Dados
- **Tipo**: SQLite
- **Localização**: `instance/app.db`
- **Schema**: v2 (com data_inicio/data_fim/duracao_horas)

### Upload de Ficheiros
- **Pasta temp**: `uploads/`
- **Cleanup**: Automático após processamento
- **Formatos**: `.xlsx`, `.xls`

---

## 📝 Notas de Desenvolvimento

### Detecção Automática de Formato
O sistema deteta automaticamente se o Excel é:
- **Multi-event**: Se a primeira sheet tem uma linha com ≥2 headers de participantes (Nome + Email/Telefone)
- **Single event**: Caso contrário (formato legado com 2 sheets separadas)

```python
# excel_import_service.py linhas 145-157
def _find_participant_section(self, df: pd.DataFrame) -> int:
    for idx, row in df.iterrows():
        row_lower = [str(cell).lower().strip() for cell in row if pd.notna(cell)]

        has_nome = any('nome' in cell or 'name' in cell for cell in row_lower)
        has_email = any('email' in cell or 'e-mail' in cell for cell in row_lower)
        has_telefone = any('telefone' in cell or 'phone' in cell for cell in row_lower)

        if sum([has_nome, has_email, has_telefone]) >= 2:
            return idx  # Found participant header row

    return None
```

### Conversões Automáticas
- **Data**: DD/MM/YY → datetime → date (para BD)
- **Duração**: minutos (Excel) → horas (BD)
- **Strings**: Strip whitespace, handle NaN/empty

---

## ⚠️ Limitações Conhecidas

1. **Datas**: Só suporta formato português (DD/MM/YY ou DD/MM/YYYY)
2. **Validação**: Campos obrigatórios são validados mas sem feedback detalhado
3. **Error Handling**: Erros de parse mostram mensagem genérica ao utilizador
4. **File Size**: Sem limite explícito de tamanho de ficheiro
5. **Concorrência**: Upload simultâneo de múltiplos ficheiros pode causar race conditions

---

## 🎨 Design

### Paleta de Cores (Wellness Theme)
```css
--sage-green: #9DB5A5
--lavender: #C8B8D8
--soft-peach: #F5D4C5
--warm-cream: #FFF8F0
--deep-sage: #5F7A6C
```

### Fontes
- **Headings**: 'Cormorant Garamond', serif
- **Body**: 'Inter', sans-serif

---

## 🔜 Próximos Passos (Sugestões)

- [ ] Adicionar validação de campos obrigatórios com feedback visual
- [ ] Implementar preview do Excel antes de importar
- [ ] Suportar exportação de eventos para Excel
- [ ] Adicionar filtros e pesquisa na lista de eventos
- [ ] Implementar autenticação de utilizadores
- [ ] Adicionar testes automatizados
- [ ] Documentar API endpoints
- [ ] Adicionar logs estruturados

---

## 📞 Informações de Suporte

**Aplicação**: http://localhost:5000
**Logs**: Console do terminal onde `run.py` está a correr
**BD Browser**: Usar SQLite browser para `instance/app.db`

---

*Documento gerado automaticamente em 14/01/2026*
