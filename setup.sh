#!/bin/bash
# Setup script for GestorEventos v2.0

echo "🚀 GestorEventos v2.0 - Setup"
echo "================================"
echo ""

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor instala Python 3.8+"
    exit 1
fi

echo "✅ Python3 encontrado: $(python3 --version)"
echo ""

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 A criar virtual environment..."
    python3 -m venv venv

    if [ $? -ne 0 ]; then
        echo "❌ Erro ao criar virtual environment"
        exit 1
    fi

    echo "✅ Virtual environment criado!"
    echo ""
else
    echo "✅ Virtual environment já existe"
    echo ""
fi

# Activate venv
echo "🔧 A ativar virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 A instalar dependências no venv..."
pip install -r requirements_v2.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

echo ""
echo "✅ Dependências instaladas com sucesso!"
echo ""

# Initialize database
echo "🗄️  A inicializar base de dados..."
python run.py init-db

if [ $? -ne 0 ]; then
    echo "❌ Erro ao inicializar base de dados"
    exit 1
fi

echo ""
echo "✅ Base de dados inicializada!"
echo ""
echo "================================"
echo "✅ Setup concluído com sucesso!"
echo ""
echo "Para executar a aplicação:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "Ou simplesmente:"
echo "  ./start.sh"
echo ""
echo "A aplicação estará disponível em: http://localhost:5000"
echo ""
echo "Credenciais padrão:"
echo "  Email: admin@gestorev2.local"
echo "  Password: admin123"
echo "================================"
