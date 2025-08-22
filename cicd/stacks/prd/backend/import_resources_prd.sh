#!/bin/bash

# Script para importar recursos existentes al estado de Terraform - PRD
# Ejecutar desde: /workspaces/agro_extension_digital_project/cicd/stacks/prd/backend

set -e

echo "🚀 Importando recursos existentes al nuevo estado de Terraform (PRD)..."

# Configurar variables
PROJECT_ID="agro-extension-digital-prd"
REGION="us-central1"

echo "📋 Proyecto: $PROJECT_ID"
echo "🌍 Región: $REGION"
echo ""

# Verificar qué servicios existen
echo "🔍 Verificando servicios existentes..."
gcloud run services list --region=$REGION --project=$PROJECT_ID

echo ""
echo "🔍 Verificando service accounts existentes..."
gcloud iam service-accounts list --project=$PROJECT_ID --filter="email~prd"

echo ""
echo "⚠️  IMPORTANTE: Verificar que los recursos arriba existan antes de continuar"
echo "💡 Si no existen recursos, no ejecutar este script"
echo ""
read -p "¿Continuar con la importación? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Importación cancelada"
    exit 1
fi

# 1. Importar Service Accounts (si existen)
echo "1️⃣ Importando Service Accounts..."
terragrunt import google_service_account.agent_aa_app "projects/$PROJECT_ID/serviceAccounts/agent-aa-sa-prd@agro-extension-digital-prd.iam.gserviceaccount.com" || echo "⚠️  Service account agent-aa-sa-prd no existe"
terragrunt import google_service_account.webhook_app_sa "projects/$PROJECT_ID/serviceAccounts/agent-webhook-sa-prd@agro-extension-digital-prd.iam.gserviceaccount.com" || echo "⚠️  Service account agent-webhook-sa-prd no existe"

# 2. Importar Cloud Run services (si existen)
echo "2️⃣ Importando Cloud Run services..."
terragrunt import google_cloud_run_v2_service.cloud_run_name_agent_aa "projects/$PROJECT_ID/locations/$REGION/services/agent-prd" || echo "⚠️  Service agent-prd no existe"
terragrunt import google_cloud_run_v2_service.cloud_run_name_webhook "projects/$PROJECT_ID/locations/$REGION/services/agent-webhook-prd" || echo "⚠️  Service agent-webhook-prd no existe"

# 3. Importar IAM bindings existentes
echo "3️⃣ Importando IAM bindings existentes..."
terragrunt import google_project_iam_member.agent_aa_sa_role "$PROJECT_ID roles/aiplatform.user serviceAccount:agent-aa-sa-prd@agro-extension-digital-prd.iam.gserviceaccount.com" || echo "⚠️  IAM aiplatform.user no existe"
terragrunt import google_project_iam_member.agent_aa_sa_role_discovery "$PROJECT_ID roles/discoveryengine.user serviceAccount:agent-aa-sa-prd@agro-extension-digital-prd.iam.gserviceaccount.com" || echo "⚠️  IAM discoveryengine.user no existe"

echo ""
echo "✅ Importación de PRD completa!"
echo "🧪 Verificando que todo esté correcto..."

# Verificar que no hay cambios pendientes
terragrunt plan

echo ""
echo "🎉 Estado final de PRD verificado!"
