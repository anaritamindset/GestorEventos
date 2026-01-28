#!/bin/bash
# Deploy script for Google App Engine
# Usage: ./deploy.sh

set -e  # Exit on error

echo "🚀 Starting deployment to Google App Engine..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK not found!${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${GREEN}✓${NC} Google Cloud SDK found"

# Check if .env.yaml exists
if [ ! -f ".env.yaml" ]; then
    echo -e "${YELLOW}⚠️  .env.yaml not found${NC}"
    echo "Creating from template..."
    cp .env.yaml.example .env.yaml
    echo -e "${YELLOW}⚠️  Please edit .env.yaml with your credentials before deploying!${NC}"
    echo "Press any key to open .env.yaml in editor..."
    read -n 1
    ${EDITOR:-nano} .env.yaml
fi

echo -e "${GREEN}✓${NC} Environment file found"

# Check if user is logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to gcloud${NC}"
    echo "Logging in..."
    gcloud auth login
fi

echo -e "${GREEN}✓${NC} Authenticated with Google Cloud"

# Get current project
PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT" ]; then
    echo -e "${YELLOW}⚠️  No project selected${NC}"
    echo "Available projects:"
    gcloud projects list
    echo ""
    read -p "Enter project ID (or press Enter to create new): " PROJECT

    if [ -z "$PROJECT" ]; then
        read -p "Enter new project ID: " PROJECT
        echo "Creating project..."
        gcloud projects create $PROJECT
    fi

    gcloud config set project $PROJECT
fi

echo -e "${GREEN}✓${NC} Using project: $PROJECT"

# Check if App Engine is initialized
if ! gcloud app describe &> /dev/null; then
    echo -e "${YELLOW}⚠️  App Engine not initialized${NC}"
    echo "Available regions:"
    echo "  europe-west1 (Belgium) - Recommended for Portugal"
    echo "  europe-west2 (London)"
    echo "  europe-west3 (Frankfurt)"
    read -p "Enter region [europe-west1]: " REGION
    REGION=${REGION:-europe-west1}

    echo "Creating App Engine..."
    gcloud app create --region=$REGION
fi

echo -e "${GREEN}✓${NC} App Engine initialized"

# Update requirements.txt
echo "Updating requirements.txt..."
pip freeze > requirements.txt

echo -e "${GREEN}✓${NC} Requirements updated"

# Show what will be deployed
echo ""
echo -e "${YELLOW}📦 Deployment Summary:${NC}"
echo "  Project: $PROJECT"
echo "  Runtime: python39"
echo "  Region: $(gcloud app describe --format='value(locationId)' 2>/dev/null)"
echo ""

# Ask for confirmation
read -p "Deploy to production? (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Deploy
echo ""
echo "🚀 Deploying application..."
gcloud app deploy --quiet

# Get the URL
URL=$(gcloud app describe --format='value(defaultHostname)' 2>/dev/null)

echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo ""
echo "🌐 Your application is available at:"
echo "   https://$URL"
echo ""
echo "📊 View logs:"
echo "   gcloud app logs tail -s default"
echo ""
echo "🔍 Open in browser:"
echo "   gcloud app browse"
echo ""
echo -e "${YELLOW}⚠️  Don't forget to configure OAuth redirect URIs:${NC}"
echo "   https://$URL/oauth2callback"
echo "   https://$URL/google/callback"
echo ""
echo "Configure at: https://console.cloud.google.com/apis/credentials"
echo ""
