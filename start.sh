#!/bin/bash
# Start script for GestorEventos v2.0

echo "🚀 A iniciar GestorEventos v2.0..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment não encontrado!"
    echo "Por favor executa primeiro: ./setup.sh"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check if database exists
if [ ! -f "gestorev2.db" ]; then
    echo "⚠️  Base de dados não encontrada. A criar..."
    python run.py init-db
    echo ""
fi

# Start app
echo "✅ A iniciar servidor..."
echo "🌐 Aplicação disponível em: http://localhost:5000"
echo ""
echo "Para parar: Ctrl+C"
echo ""
python run.py
