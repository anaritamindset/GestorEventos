#!/bin/bash

# Detectar o diretório do script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não está instalado. Por favor, instale o Python 3 e tente novamente."
    echo "Você pode baixar o Python em: https://www.python.org/downloads/"
    read -p "Pressione Enter para sair..."
    exit 1
fi

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
    
    echo "Instalando dependências necessárias..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Iniciar a aplicação
echo "Iniciando Gestor de Eventos..."
python app.py

# Manter a janela aberta em caso de erro
read -p "Pressione Enter para sair..."
