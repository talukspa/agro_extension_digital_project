#!/bin/bash

# Script maestro para deployment completo de CiruelaCertificada
# Incluye: secretos, base de datos, frontend

set -e

PROJECT_ID="agro-extension-digital-npe"
ENVIRONMENT=${1:-dev}

echo "🍇 DEPLOYMENT COMPLETO - CiruelaCertificada"
echo "=============================================="
echo "📋 Proyecto: $PROJECT_ID"
echo "🏗️ Ambiente: $ENVIRONMENT"
echo ""

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar herramientas necesarias
echo "🔧 Verificando herramientas requeridas..."
required_tools=("gcloud" "docker" "terragrunt" "pnpm")
missing_tools=()

for tool in "${required_tools[@]}"; do
    if command_exists "$tool"; then
        echo "✅ $tool está instalado"
    else
        echo "❌ $tool NO está instalado"
        missing_tools+=("$tool")
    fi
done

if [ ${#missing_tools[@]} -ne 0 ]; then
    echo ""
    echo "❌ FALTAN HERRAMIENTAS REQUERIDAS"
    echo "   Instale las siguientes herramientas antes de continuar:"
    printf '   - %s\n' "${missing_tools[@]}"
    exit 1
fi

echo ""
echo "📁 Navegando al directorio del proyecto..."
cd /workspaces/agro_extension_digital_project

# Paso 1: Validar prerrequisitos
echo ""
echo "🔍 PASO 1: VALIDANDO PRERREQUISITOS"
echo "===================================="
if ./scripts/validate-secrets.sh; then
    echo "✅ Todos los secretos están configurados"
else
    echo "❌ Secretos faltantes detectados"
    echo ""
    echo "🔐 ¿Desea configurar los secretos ahora? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🚀 Ejecutando configuración de secretos..."
        ./scripts/setup-secrets.sh
        echo ""
        echo "✅ Secretos configurados. Validando nuevamente..."
        ./scripts/validate-secrets.sh
    else
        echo "❌ No se puede continuar sin los secretos configurados"
        echo "   Ejecute manualmente: ./scripts/setup-secrets.sh"
        exit 1
    fi
fi

# Paso 2: Importar y configurar base de datos
echo ""
echo "🗄️ PASO 2: CONFIGURANDO BASE DE DATOS"
echo "======================================"
echo "🔥 Importando base de datos Firestore..."
if ./scripts/import-database.sh "$ENVIRONMENT"; then
    echo "✅ Base de datos configurada exitosamente"
else
    echo "⚠️ Hubo problemas con la importación de la base de datos"
    echo "   Continuando con el deployment..."
fi

# Paso 3: Deploy del frontend
echo ""
echo "🌐 PASO 3: DEPLOYMENT DEL FRONTEND"
echo "==================================="
echo "🚀 Ejecutando deployment del frontend..."
if ./scripts/deploy-frontend.sh "$ENVIRONMENT"; then
    echo "✅ Frontend desplegado exitosamente"
else
    echo "❌ Error en el deployment del frontend"
    exit 1
fi

# Paso 4: Verificación final
echo ""
echo "🔍 PASO 4: VERIFICACIÓN FINAL"
echo "=============================="

echo "📋 Verificando servicios desplegados..."

# Verificar Cloud Run service
SERVICE_NAME="frontend-app-$ENVIRONMENT"
if gcloud run services describe "$SERVICE_NAME" --region=us-central1 --project="$PROJECT_ID" &>/dev/null; then
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region=us-central1 \
        --project="$PROJECT_ID" \
        --format="value(status.url)")
    echo "✅ Servicio Cloud Run: $SERVICE_NAME"
    echo "🌐 URL: $SERVICE_URL"
else
    echo "❌ No se pudo verificar el servicio Cloud Run"
fi

# Verificar base de datos
if gcloud firestore databases describe agro-extension-db --project="$PROJECT_ID" &>/dev/null; then
    echo "✅ Base de datos Firestore: agro-extension-db"
else
    echo "❌ No se pudo verificar la base de datos Firestore"
fi

# Verificar algunos secretos clave
echo "🔐 Verificando secretos críticos..."
critical_secrets=("firebase-api-key" "firebase-project-id" "wsp-token")
for secret in "${critical_secrets[@]}"; do
    if gcloud secrets describe "$secret" --project="$PROJECT_ID" &>/dev/null; then
        echo "✅ Secreto: $secret"
    else
        echo "❌ Secreto faltante: $secret"
    fi
done

echo ""
echo "🎉 DEPLOYMENT COMPLETADO"
echo "========================"
echo ""
echo "📋 Resumen del deployment:"
echo "   Ambiente: $ENVIRONMENT"
echo "   Proyecto: $PROJECT_ID"
echo "   Frontend URL: ${SERVICE_URL:-'No disponible'}"
echo "   Base de datos: agro-extension-db"
echo ""
echo "🔗 Enlaces útiles:"
echo "   Cloud Console: https://console.cloud.google.com/run?project=$PROJECT_ID"
echo "   Firebase Console: https://console.firebase.google.com/project/$PROJECT_ID"
echo "   Logs: https://console.cloud.google.com/logs/query?project=$PROJECT_ID"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Probar la aplicación en: ${SERVICE_URL:-'URL del servicio'}"
echo "   2. Verificar logs en caso de problemas"
echo "   3. Configurar usuarios iniciales en Firebase Auth"
echo "   4. Cargar datos de prueba en Firestore"
echo ""
echo "🆘 Soporte:"
echo "   - Documentación: /docs/frontend/"
echo "   - Troubleshooting: /docs/frontend/05-deployment-checklist.md"
echo "   - Base de datos: /docs/frontend/06-database-management.md"
