# 📋 Prerrequisitos de Variables de Entorno

## 🔐 Variables de Entorno Requeridas

Este documento detalla todas las variables de entorno que deben configurarse manualmente antes del deployment usando Google Secret Manager.

## 1. Variables de Firebase

### 🔑 Variables Requeridas

Estas variables se obtienen desde la consola de Firebase (`https://console.firebase.google.com`):

1. **FIREBASE_API_KEY** *(Obligatorio)*
   - **Descripción**: Clave API de Firebase para autenticación
   - **Dónde obtenerla**: Firebase Console → Configuración del proyecto → Configuración general → SDK setup and configuration
   - **Formato**: String alfanumérico (ej: `AIzaSyBNlYH01_9Hc5S1J9F40k1hn...`)

2. **FIREBASE_AUTH_DOMAIN** *(Obligatorio)*
   - **Descripción**: Dominio de autenticación de Firebase
   - **Dónde obtenerla**: Firebase Console → Configuración del proyecto → Configuración general
   - **Formato**: `{project-id}.firebaseapp.com`

3. **FIREBASE_PROJECT_ID** *(Obligatorio)*
   - **Descripción**: ID del proyecto Firebase
   - **Dónde obtenerla**: Firebase Console → Configuración del proyecto → Configuración general
   - **Formato**: String kebab-case (ej: `agro-extension-digital-npe`)

4. **FIREBASE_STORAGE_BUCKET** *(Obligatorio)*
   - **Descripción**: Bucket de Firebase Storage
   - **Dónde obtenerla**: Firebase Console → Storage → Configuración
   - **Formato**: `{project-id}.appspot.com`

5. **FIREBASE_MESSAGING_SENDER_ID** *(Obligatorio)*
   - **Descripción**: ID del remitente para Firebase Cloud Messaging
   - **Dónde obtenerla**: Firebase Console → Configuración del proyecto → Cloud Messaging
   - **Formato**: Número (ej: `123456789012`)

6. **FIREBASE_APP_ID** *(Obligatorio)*
   - **Descripción**: ID único de la aplicación Firebase
   - **Dónde obtenerla**: Firebase Console → Configuración del proyecto → Configuración general → Apps
   - **Formato**: `1:123456789012:web:abcdef123456...`

7. **FIREBASE_MEASUREMENT_ID** *(Opcional)*
   - **Descripción**: ID de Google Analytics (solo si Analytics está habilitado)
   - **Dónde obtenerla**: Firebase Console → Analytics → Configuración
   - **Formato**: `G-XXXXXXXXXX`

## 2. Variables del Sistema Backend

### 🤖 WhatsApp & Facebook (Para Agente Virtual)

**Nota**: Estas variables son para la integración con WhatsApp Business que permite a las empresas agrícolas interactuar con el sistema a través de un agente virtual para consultar estándares, subir evidencia, y recibir notificaciones sobre el estado de sus auditorías.

1. **WSP_TOKEN** *(Obligatorio)*
   - **Descripción**: Token de acceso de WhatsApp Business API
   - **Dónde obtenerla**: Facebook Developer Console → WhatsApp → Configuración
   - **Formato**: Token de acceso permanente

2. **WEBHOOK_VERIFY_TOKEN** *(Obligatorio)*
   - **Descripción**: Token de verificación del webhook de WhatsApp
   - **Dónde obtenerla**: Se genera manualmente (string aleatorio seguro)
   - **Formato**: String alfanumérico de 32+ caracteres
   - **Uso**: Verificación de webhooks entre WhatsApp y la aplicación webhook-application/

## 3. Comandos para Configurar Secretos

### 🚀 Script de Configuración Automatizada

```bash
#!/bin/bash

# Script para configurar todos los secretos de Firebase y WhatsApp
PROJECT_ID="agro-extension-digital-npe"

echo "🔐 Configurando secretos para Agro Extension Digital..."

# Función para crear o actualizar un secreto
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2
    
    # Verificar si el secreto existe
    if gcloud secrets describe $secret_name --project=$PROJECT_ID &>/dev/null; then
        echo "📝 Actualizando secreto existente: $secret_name"
        echo -n "$secret_value" | gcloud secrets versions add $secret_name --data-file=- --project=$PROJECT_ID
    else
        echo "🆕 Creando nuevo secreto: $secret_name"
        echo -n "$secret_value" | gcloud secrets create $secret_name --data-file=- --project=$PROJECT_ID
    fi
}

# Firebase Secrets
echo "🔥 Configurando secretos de Firebase..."
echo "Por favor, ingrese los valores obtenidos de Firebase Console:"

read -p "Firebase API Key: " FIREBASE_API_KEY
create_or_update_secret "firebase-api-key" "$FIREBASE_API_KEY"

read -p "Firebase Auth Domain: " FIREBASE_AUTH_DOMAIN
create_or_update_secret "firebase-auth-domain" "$FIREBASE_AUTH_DOMAIN"

read -p "Firebase Project ID: " FIREBASE_PROJECT_ID
create_or_update_secret "firebase-project-id" "$FIREBASE_PROJECT_ID"

read -p "Firebase Storage Bucket: " FIREBASE_STORAGE_BUCKET
create_or_update_secret "firebase-storage-bucket" "$FIREBASE_STORAGE_BUCKET"

read -p "Firebase Messaging Sender ID: " FIREBASE_MESSAGING_SENDER_ID
create_or_update_secret "firebase-messaging-sender-id" "$FIREBASE_MESSAGING_SENDER_ID"

read -p "Firebase App ID: " FIREBASE_APP_ID
create_or_update_secret "firebase-app-id" "$FIREBASE_APP_ID"

read -p "Firebase Measurement ID (opcional, enter para saltar): " FIREBASE_MEASUREMENT_ID
if [ ! -z "$FIREBASE_MEASUREMENT_ID" ]; then
    create_or_update_secret "firebase-measurement-id" "$FIREBASE_MEASUREMENT_ID"
fi

# WhatsApp Secrets
echo "📱 Configurando secretos de WhatsApp..."

read -p "WhatsApp Token: " WSP_TOKEN
create_or_update_secret "wsp-token" "$WSP_TOKEN"

read -p "Webhook Verify Token: " WEBHOOK_VERIFY_TOKEN
create_or_update_secret "webhook-verify-token" "$WEBHOOK_VERIFY_TOKEN"

echo "✅ Todos los secretos han sido configurados exitosamente!"
echo "🔍 Verificar secretos creados:"
echo "gcloud secrets list --project=$PROJECT_ID"
```

### 🔧 Comandos Individuales

```bash
# Configurar PROJECT_ID
PROJECT_ID="agro-extension-digital-npe"

# === FIREBASE SECRETS ===
# Crear secretos de Firebase (ejecutar uno por uno)

# 1. Firebase API Key
echo -n "YOUR_FIREBASE_API_KEY" | gcloud secrets create firebase-api-key --data-file=- --project=$PROJECT_ID

# 2. Firebase Auth Domain  
echo -n "agro-extension-digital-npe.firebaseapp.com" | gcloud secrets create firebase-auth-domain --data-file=- --project=$PROJECT_ID

# 3. Firebase Project ID
echo -n "agro-extension-digital-npe" | gcloud secrets create firebase-project-id --data-file=- --project=$PROJECT_ID

# 4. Firebase Storage Bucket
echo -n "agro-extension-digital-npe.appspot.com" | gcloud secrets create firebase-storage-bucket --data-file=- --project=$PROJECT_ID

# 5. Firebase Messaging Sender ID
echo -n "YOUR_MESSAGING_SENDER_ID" | gcloud secrets create firebase-messaging-sender-id --data-file=- --project=$PROJECT_ID

# 6. Firebase App ID
echo -n "YOUR_FIREBASE_APP_ID" | gcloud secrets create firebase-app-id --data-file=- --project=$PROJECT_ID

# 7. Firebase Measurement ID (opcional)
echo -n "YOUR_MEASUREMENT_ID" | gcloud secrets create firebase-measurement-id --data-file=- --project=$PROJECT_ID

# === WHATSAPP SECRETS ===
# Crear secretos de WhatsApp

# WhatsApp Token
echo -n "YOUR_WHATSAPP_TOKEN" | gcloud secrets create wsp-token --data-file=- --project=$PROJECT_ID

# Webhook Verify Token
echo -n "YOUR_VERIFY_TOKEN" | gcloud secrets create webhook-verify-token --data-file=- --project=$PROJECT_ID
```

### 🔍 Verificación de Secretos

```bash
# Listar todos los secretos
gcloud secrets list --project=agro-extension-digital-npe

# Verificar un secreto específico (sin mostrar el valor)
gcloud secrets describe firebase-api-key --project=agro-extension-digital-npe

# Probar acceso a un secreto (mostrará el valor)
gcloud secrets versions access latest --secret=firebase-api-key --project=agro-extension-digital-npe
```

## 4. Permisos Requeridos

### 🛡️ IAM Roles Necesarios

El usuario o service account que ejecute Terragrunt necesita:

```bash
# Roles mínimos requeridos
gcloud projects add-iam-policy-binding agro-extension-digital-npe \
    --member="user:your-email@domain.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding agro-extension-digital-npe \
    --member="user:your-email@domain.com" \
    --role="roles/secretmanager.admin"

# Para Terragrunt deployment
gcloud projects add-iam-policy-binding agro-extension-digital-npe \
    --member="user:your-email@domain.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding agro-extension-digital-npe \
    --member="user:your-email@domain.com" \
    --role="roles/storage.admin"
```

## 5. Validación Pre-Deploy

### ✅ Checklist de Prerrequisitos

Antes de ejecutar `terragrunt apply`, verificar:

```bash
# 1. Autenticación
gcloud auth list
gcloud config get-value project

# 2. Verificar secretos existen
SECRETS=(
    "firebase-api-key"
    "firebase-auth-domain" 
    "firebase-project-id"
    "firebase-storage-bucket"
    "firebase-messaging-sender-id"
    "firebase-app-id"
    "wsp-token"
    "webhook-verify-token"
)

for secret in "${SECRETS[@]}"; do
    if gcloud secrets describe $secret --project=agro-extension-digital-npe &>/dev/null; then
        echo "✅ $secret existe"
    else
        echo "❌ $secret NO existe - DEBE crearse"
    fi
done

# 3. Verificar permisos
gcloud projects get-iam-policy agro-extension-digital-npe \
    --flatten="bindings[].members" \
    --format='table(bindings.role)' \
    --filter="bindings.members:$(gcloud config get-value account)"
```

## 6. Troubleshooting

### 🐛 Problemas Comunes

**Error: "Permission denied on secret"**
```bash
# Solución: Verificar y agregar permisos
gcloud projects add-iam-policy-binding agro-extension-digital-npe \
    --member="user:$(gcloud config get-value account)" \
    --role="roles/secretmanager.secretAccessor"
```

**Error: "Secret not found"**
```bash
# Solución: Crear el secreto faltante
echo -n "YOUR_SECRET_VALUE" | gcloud secrets create SECRET_NAME --data-file=- --project=agro-extension-digital-npe
```

**Error: "run_cmd failed"**
```bash
# Solución: Verificar instalación de gcloud y autenticación
gcloud --version
gcloud auth application-default login
```

---

## 📝 Notas Importantes

1. **Seguridad**: Nunca commits secretos en git. Siempre usar Google Secret Manager.
2. **Rotación**: Rotar secretos regularmente, especialmente tokens de WhatsApp.
3. **Environments**: Los mismos secretos se usan en dev y prod (Firebase maneja esto internamente).
4. **Backup**: Mantener un backup seguro de los valores de secretos.
5. **Integración WhatsApp**: Los tokens de WhatsApp son para el agente virtual que permite a empresas agrícolas interactuar con el sistema de estándares sin necesidad de acceder directamente a la interfaz web.
6. **Base de Datos**: Firebase se conecta automáticamente a la base de datos `agro-extension-db` configurada para gestionar business_profiles, auditors, responses, y standards.

## 🔗 Enlaces Útiles

- [Firebase Console](https://console.firebase.google.com)
- [Facebook Developer Console](https://developers.facebook.com)
- [Google Secret Manager](https://console.cloud.google.com/security/secret-manager)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
