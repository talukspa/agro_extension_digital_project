#!/bin/bash

# Script para configurar todos los secretos de Firebase y WhatsApp
# usando Google Secret Manager

PROJECT_ID="agro-extension-digital-npe"

echo "🔐 Configurando secretos para CiruelaCertificada..."
echo "📋 Proyecto: $PROJECT_ID"
echo ""

# Verificar autenticación
current_user=$(gcloud config get-value account)
if [ -z "$current_user" ]; then
    echo "❌ No hay usuario autenticado en gcloud"
    echo "   Ejecute: gcloud auth login"
    exit 1
fi

echo "👤 Usuario autenticado: $current_user"
echo ""

# Función para crear o actualizar un secreto
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if [ -z "$secret_value" ]; then
        echo "⚠️  Valor vacío para $secret_name, saltando..."
        return
    fi
    
    # Verificar si el secreto existe
    if gcloud secrets describe $secret_name --project=$PROJECT_ID &>/dev/null; then
        echo "📝 Actualizando secreto existente: $secret_name"
        echo -n "$secret_value" | gcloud secrets versions add $secret_name --data-file=- --project=$PROJECT_ID
        if [ $? -eq 0 ]; then
            echo "✅ $secret_name actualizado exitosamente"
        else
            echo "❌ Error al actualizar $secret_name"
        fi
    else
        echo "🆕 Creando nuevo secreto: $secret_name"
        echo -n "$secret_value" | gcloud secrets create $secret_name --data-file=- --project=$PROJECT_ID
        if [ $? -eq 0 ]; then
            echo "✅ $secret_name creado exitosamente"
        else
            echo "❌ Error al crear $secret_name"
        fi
    fi
}

# Función para leer entrada segura
read_secret() {
    local prompt=$1
    local var_name=$2
    local is_optional=${3:-false}
    
    if [ "$is_optional" = true ]; then
        read -p "$prompt (opcional, ENTER para saltar): " value
    else
        read -p "$prompt: " value
        while [ -z "$value" ]; do
            echo "⚠️  Este valor es requerido"
            read -p "$prompt: " value
        done
    fi
    
    eval $var_name=\"$value\"
}

echo "🔥 CONFIGURACIÓN DE SECRETOS DE FIREBASE"
echo "==============================================="
echo ""
echo "📋 Para obtener estos valores, visite Firebase Console:"
echo "   https://console.firebase.google.com/project/$PROJECT_ID/settings/general"
echo ""

# Firebase Secrets
read_secret "Firebase API Key" FIREBASE_API_KEY
read_secret "Firebase Auth Domain [$PROJECT_ID.firebaseapp.com]" FIREBASE_AUTH_DOMAIN
if [ -z "$FIREBASE_AUTH_DOMAIN" ]; then
    FIREBASE_AUTH_DOMAIN="$PROJECT_ID.firebaseapp.com"
fi

read_secret "Firebase Project ID [$PROJECT_ID]" FIREBASE_PROJECT_ID  
if [ -z "$FIREBASE_PROJECT_ID" ]; then
    FIREBASE_PROJECT_ID="$PROJECT_ID"
fi

read_secret "Firebase Storage Bucket [$PROJECT_ID.appspot.com]" FIREBASE_STORAGE_BUCKET
if [ -z "$FIREBASE_STORAGE_BUCKET" ]; then
    FIREBASE_STORAGE_BUCKET="$PROJECT_ID.appspot.com"
fi

read_secret "Firebase Messaging Sender ID" FIREBASE_MESSAGING_SENDER_ID
read_secret "Firebase App ID" FIREBASE_APP_ID
read_secret "Firebase Measurement ID" FIREBASE_MEASUREMENT_ID true

echo ""
echo "📱 CONFIGURACIÓN DE SECRETOS DE WHATSAPP"
echo "==============================================="
echo ""
echo "📋 Para obtener estos valores:"
echo "   - WhatsApp Token: Facebook Developer Console > WhatsApp > Configuración"
echo "   - Verify Token: Genere una cadena aleatoria segura"
echo ""

read_secret "WhatsApp Token" WSP_TOKEN
read_secret "Webhook Verify Token" WEBHOOK_VERIFY_TOKEN

echo ""
echo "💾 CREANDO SECRETOS EN GOOGLE SECRET MANAGER..."
echo "==============================================="

# Crear secretos de Firebase
create_or_update_secret "firebase-api-key" "$FIREBASE_API_KEY"
create_or_update_secret "firebase-auth-domain" "$FIREBASE_AUTH_DOMAIN"
create_or_update_secret "firebase-project-id" "$FIREBASE_PROJECT_ID"
create_or_update_secret "firebase-storage-bucket" "$FIREBASE_STORAGE_BUCKET"
create_or_update_secret "firebase-messaging-sender-id" "$FIREBASE_MESSAGING_SENDER_ID"
create_or_update_secret "firebase-app-id" "$FIREBASE_APP_ID"
create_or_update_secret "firebase-measurement-id" "$FIREBASE_MEASUREMENT_ID"

# Crear secretos de WhatsApp
create_or_update_secret "wsp-token" "$WSP_TOKEN"
create_or_update_secret "webhook-verify-token" "$WEBHOOK_VERIFY_TOKEN"

echo ""
echo "🔍 VERIFICACIÓN DE SECRETOS CREADOS"
echo "==============================================="

echo ""
echo "📋 Listado de secretos en el proyecto:"
gcloud secrets list --project=$PROJECT_ID --format="table(name,createTime)"

echo ""
echo "✅ CONFIGURACIÓN DE SECRETOS COMPLETADA!"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Verificar secretos: ./scripts/validate-secrets.sh"
echo "   2. Ejecutar deployment: ./scripts/deploy-frontend.sh dev"
echo ""
echo "🔒 RECORDATORIOS DE SEGURIDAD:"
echo "   - Los secretos están almacenados de forma segura en Google Secret Manager"
echo "   - NO commit estos valores en el repositorio"
echo "   - Rote los tokens regularmente"
echo "   - Mantenga un backup seguro de los valores críticos"
