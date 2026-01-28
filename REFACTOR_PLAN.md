# Plano de Refactoring - Gestor Wellness

## Melhorias Implementadas

### ✅ 1. Constantes Centralizadas (`app/constants.py`)
- Criado ficheiro de constantes para valores magic numbers
- Organizado em classes lógicas:
  - `CertificateLayout`: Dimensões e espaçamento
  - `CertificateText`: Textos e templates
  - `DefaultColors`: Cores padrão
  - `FilePaths`: Caminhos de ficheiros
  - `EmailConfig`: Configuração de email

## Melhorias Recomendadas (Futuro)

### 📋 2. Certificate Service Refactoring

**Problemas atuais:**
- Método `_create_pdf()` muito grande (~200 linhas)
- Lógica de layout misturada com renderização
- Difícil de testar e manter

**Solução proposta:**
```python
# Dividir em métodos menores:
- _render_borders()
- _render_logo()
- _render_title()
- _render_body_text()
- _render_signature()
- _render_seal()
- _format_date_portuguese()
- _build_certificate_text()
```

### 📋 3. Main Routes Refactoring (960 linhas)

**Problemas:**
- Ficheiro muito grande
- Responsabilidades misturadas
- Difícil de navegar

**Solução proposta:**
```
app/api/routes/
├── main.py (homepage, menu)
├── events.py (CRUD eventos)
├── participants.py (gestão participantes)
├── certificates.py (geração/envio certificados)
├── google_integration.py (OAuth, Forms, Drive)
└── automation.py (automação Google)
```

### 📋 4. Type Hints

**Adicionar type hints para:**
- Parâmetros de funções
- Valores de retorno
- Variáveis complexas

**Exemplo:**
```python
from typing import Optional, Dict, List, Tuple
from app.models import Organization, Event, Participant

def generate_certificate(
    self,
    participant_id: int,
    template_id: Optional[int] = None
) -> str:
    """
    Generate certificate PDF for a participant

    Args:
        participant_id: Participant ID
        template_id: Optional template ID (uses default if None)

    Returns:
        Path to generated PDF file

    Raises:
        ValueError: If participant or event not found
    """
    ...
```

### 📋 5. Error Handling

**Melhorias:**
- Criar custom exceptions (`CertificateGenerationError`, `EmailSendError`)
- Centralizar logging
- Adicionar retry logic para operações de rede
- Validação de input mais robusta

**Exemplo:**
```python
class CertificateError(Exception):
    """Base exception for certificate operations"""
    pass

class ParticipantNotFoundError(CertificateError):
    """Raised when participant is not found"""
    pass

class TemplateNotFoundError(CertificateError):
    """Raised when template is not found"""
    pass
```

### 📋 6. Configuration Management

**Criar:**
- `config/development.py`
- `config/production.py`
- `config/testing.py`

**Centralizar:**
- Database URLs
- SMTP settings
- File paths
- Debug flags
- Secret keys

### 📋 7. Service Layer Patterns

**Implementar:**
- Repository pattern para database access
- Factory pattern para certificate templates
- Strategy pattern para diferentes tipos de eventos

### 📋 8. Testing

**Adicionar:**
- Unit tests para services
- Integration tests para routes
- Fixtures para test data
- Mock objects para external services

```python
# tests/services/test_certificate_service.py
def test_generate_certificate_success():
    service = CertificateService()
    path = service.generate_certificate(participant_id=1)
    assert os.path.exists(path)
    assert path.endswith('.pdf')
```

### 📋 9. Documentation

**Melhorar:**
- Docstrings em todas as classes/métodos
- README com setup instructions
- API documentation
- Architecture diagrams

### 📋 10. Code Quality Tools

**Integrar:**
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking
- `pytest` - Testing
- `pre-commit` - Git hooks

## Prioridades

1. **Alta** - Usar constantes em certificate_service ✅
2. **Alta** - Dividir main.py em blueprints separados
3. **Média** - Adicionar type hints
4. **Média** - Melhorar error handling
5. **Baixa** - Testes completos
6. **Baixa** - Documentation completa

## Notas

- O código está funcional e bem organizado
- Refactoring deve ser incremental
- Testes são críticos antes de mudanças grandes
- Manter backward compatibility durante transição
