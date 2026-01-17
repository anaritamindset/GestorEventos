#!/bin/bash

# Script de Deploy Automático para Google Cloud Run
# GestorEventos v2.0

set -e  # Exit on error

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
PROJECT_ID="gestor-eventos-app"
SERVICE_NAME="gestor-eventos"
REGION="europe-west1"

echo -e "${BLUE}🚀 Deploy GestorEventos para Google Cloud Run${NC}\n"

# 1. Verificar se gcloud está instalado
echo -e "${YELLOW}📋 Verificando pré-requisitos...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI não encontrado!${NC}"
    echo "Instale com: brew install google-cloud-sdk"
    exit 1
fi
echo -e "${GREEN}✅ gcloud CLI encontrado${NC}"

# 2. Verificar autenticação
echo -e "\n${YELLOW}🔐 Verificando autenticação...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Não autenticado. Fazendo login...${NC}"
    gcloud auth login
fi
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1)
echo -e "${GREEN}✅ Autenticado como: $ACCOUNT${NC}"

# 3. Configurar projeto
echo -e "\n${YELLOW}📦 Configurando projeto...${NC}"
echo "Projeto: $PROJECT_ID"

# Verificar se projeto existe
if ! gcloud projects describe $PROJECT_ID &> /dev/null; then
    echo -e "${YELLOW}⚠️  Projeto não existe. Criando...${NC}"
    gcloud projects create $PROJECT_ID --name="Gestor Eventos"
    echo -e "${GREEN}✅ Projeto criado${NC}"
fi

gcloud config set project $PROJECT_ID
echo -e "${GREEN}✅ Projeto configurado${NC}"

# 4. Ativar APIs necessárias
echo -e "\n${YELLOW}🔧 Ativando APIs necessárias...${NC}"
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
echo -e "${GREEN}✅ APIs ativadas${NC}"

# 5. Build e Deploy
echo -e "\n${YELLOW}🐳 Fazendo build e deploy...${NC}"
echo "Região: $REGION"
echo "Serviço: $SERVICE_NAME"
echo ""

gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --quiet

# 6. Obter URL do serviço
echo -e "\n${GREEN}✅ Deploy concluído!${NC}\n"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Aplicação deployada com sucesso!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${BLUE}🌐 URL da aplicação:${NC}"
echo -e "${GREEN}$SERVICE_URL${NC}\n"

# 7. Próximos passos
echo -e "${YELLOW}📋 Próximos passos:${NC}\n"
echo "1. Adicionar redirect URI no Google Cloud Console:"
echo "   ${SERVICE_URL}/google/callback"
echo ""
echo "2. Configurar credentials.json como secret:"
echo "   ${BLUE}gcloud secrets create google-credentials --data-file=credentials.json${NC}"
echo ""
echo "3. Ver logs:"
echo "   ${BLUE}gcloud run services logs read $SERVICE_NAME --limit 100${NC}"
echo ""
echo -e "${GREEN}✨ Pronto para usar!${NC}\n"
