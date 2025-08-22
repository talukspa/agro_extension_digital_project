#!/bin/bash

# Script mejorado para importar recursos existentes al nuevo estado de Terraform
# Ejecutar desde: /workspaces/agro_extension_digital_project/cicd/stacks/dev/backend

set -e

echo "🚀 Importando recursos existentes al nuevo estado de Terraform..."

# Configurar variables
PROJECT_ID="agro-extension-digital-npe"
REGION="us-central1"

echo "📋 Proyecto: $PROJECT_ID"
echo "🌍 Región: $REGION"
echo ""

# 1. Importar Service Accounts
echo "1️⃣ Importando Service Accounts..."
terragrunt import google_service_account.agent_aa_app "projects/$PROJECT_ID/serviceAccounts/agent-aa-sa-dev@agro-extension-digital-npe.iam.gserviceaccount.com"
terragrunt import google_service_account.webhook_app_sa "projects/$PROJECT_ID/serviceAccounts/agent-webhook-sa-dev@agro-extension-digital-npe.iam.gserviceaccount.com"

# 2. Importar Cloud Run services
echo "2️⃣ Importando Cloud Run services..."
terragrunt import google_cloud_run_v2_service.cloud_run_name_agent_aa "projects/$PROJECT_ID/locations/$REGION/services/agent-dev"
terragrunt import google_cloud_run_v2_service.cloud_run_name_webhook "projects/$PROJECT_ID/locations/$REGION/services/agent-webhook-dev"

# 3. Importar solo los IAM bindings que realmente existen
echo "3️⃣ Importando IAM bindings existentes..."

# Project-level IAM members que SÍ existen
terragrunt import google_project_iam_member.agent_aa_sa_role "$PROJECT_ID roles/aiplatform.user serviceAccount:agent-aa-sa-dev@agro-extension-digital-npe.iam.gserviceaccount.com"
terragrunt import google_project_iam_member.agent_aa_sa_role_discovery "$PROJECT_ID roles/discoveryengine.user serviceAccount:agent-aa-sa-dev@agro-extension-digital-npe.iam.gserviceaccount.com"

# 4. Verificar IAM bindings de Cloud Run
echo "4️⃣ Verificando permisos de Cloud Run..."

# Verificar si existen los bindings de Cloud Run antes de importar
echo "🔍 Verificando binding noauth para webhook..."
if gcloud run services get-iam-policy agent-webhook-dev --region=$REGION --project=$PROJECT_ID --format="value(bindings[].members)" | grep -q "allUsers"; then
    echo "✅ Binding noauth existe, importando..."
    terragrunt import google_cloud_run_v2_service_iam_binding.noauth_webhook "projects/$PROJECT_ID/locations/$REGION/services/agent-webhook-dev roles/run.invoker"
else
    echo "⚠️  Binding noauth no existe, se creará en apply"
fi

echo "🔍 Verificando binding webhook->agent..."
if gcloud run services get-iam-policy agent-dev --region=$REGION --project=$PROJECT_ID --format="value(bindings[].members)" | grep -q "agent-webhook-sa-dev"; then
    echo "✅ Binding webhook->agent existe, importando..."
    terragrunt import google_cloud_run_v2_service_iam_member.webhook_invokes_agent_aa "projects/$PROJECT_ID/locations/$REGION/services/agent-dev roles/run.invoker serviceAccount:agent-webhook-sa-dev@agro-extension-digital-npe.iam.gserviceaccount.com"
else
    echo "⚠️  Binding webhook->agent no existe, se creará en apply"
fi

echo ""
echo "✅ Importación completa!"
echo "🧪 Verificando que todo esté correcto..."

# Verificar que no hay cambios pendientes
terragrunt plan

echo ""
echo "🎉 Si el plan muestra pocos cambios, la importación fue exitosa!"
