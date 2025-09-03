#!/bin/bash

# Script para configurar dominios autorizados en Firebase Authentication
# Este script agrega el dominio de Cloud Run a la lista de dominios autorizados

set -e

# Variables de entorno (pueden ser configuradas por Terraform)
PROJECT_ID="${PROJECT_ID:-agro-extension-digital-npe}"
FRONTEND_DOMAIN="${FRONTEND_DOMAIN:-frontend-dev-890639421110.us-central1.run.app}"
ENVIRONMENT="${ENVIRONMENT:-dev}"

echo "🔧 Configurando dominios autorizados para Firebase Authentication..."
echo "📋 Proyecto: $PROJECT_ID"
echo "🌐 Dominio frontend: $FRONTEND_DOMAIN"
echo "🏷️  Entorno: $ENVIRONMENT"

# Verificar que estamos autenticados
echo "📋 Verificando autenticación..."
gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1

# Configurar el proyecto
echo "🎯 Configurando proyecto: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Obtener los dominios autorizados actuales
echo "📖 Obteniendo dominios autorizados actuales..."
CURRENT_DOMAINS=$(gcloud alpha identity domains list --format="value(domain)" 2>/dev/null || echo "")

# Verificar si el dominio ya existe
if echo "$CURRENT_DOMAINS" | grep -q "$FRONTEND_DOMAIN"; then
    echo "✅ El dominio $FRONTEND_DOMAIN ya está autorizado"
else
    echo "➕ Agregando dominio autorizado: $FRONTEND_DOMAIN"
    
    # Agregar el dominio autorizado usando Firebase CLI
    if command -v firebase &> /dev/null; then
        echo "🔥 Usando Firebase CLI..."
        firebase login --no-localhost
        firebase use $PROJECT_ID
        
        # Configurar dominio autorizado
        echo "🌐 Configurando dominio autorizado..."
        
        # Crear un archivo temporal de configuración
        cat > /tmp/firebase_auth_config.json << EOF
{
  "signIn": {
    "allowDuplicateEmails": false
  },
  "authorizedDomains": [
    "localhost",
    "agro-extension-digital-npe.firebaseapp.com",
    "agro-extension-digital-npe.web.app",
    "$FRONTEND_DOMAIN"
  ]
}
EOF
        
        echo "📄 Configuración a aplicar:"
        cat /tmp/firebase_auth_config.json
        
        # Aplicar configuración usando gcloud
        echo "🚀 Aplicando configuración..."
        gcloud alpha identity platforms configs update \
            --config-file=/tmp/firebase_auth_config.json \
            --project=$PROJECT_ID
            
        # Limpiar archivo temporal
        rm /tmp/firebase_auth_config.json
        
        echo "✅ Dominio autorizado agregado exitosamente!"
    else
        echo "❌ Firebase CLI no está instalado"
        echo "💡 Instalando Firebase CLI..."
        npm install -g firebase-tools
        
        # Reintentar
        echo "🔄 Reintentando..."
        $0
    fi
fi

echo ""
echo "🎉 Configuración completada!"
echo "📋 Dominios autorizados configurados:"
echo "   - localhost"
echo "   - agro-extension-digital-npe.firebaseapp.com"
echo "   - agro-extension-digital-npe.web.app"
echo "   - $FRONTEND_DOMAIN"
echo ""
echo "🌐 Ahora puedes usar OAuth en: https://$FRONTEND_DOMAIN"
