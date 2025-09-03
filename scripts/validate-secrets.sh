#!/bin/bash

# Script para validar que todos los secretos requeridos estén configurados
# antes del deployment

PROJECT_ID="agro-extension-digital-npe"

echo "🔍 Validando secretos requeridos para CiruelaCertificada..."

# Función para verificar si un secreto existe
check_secret() {
    local secret_name=$1
    local is_optional=${2:-false}
    
    if gcloud secrets describe $secret_name --project=$PROJECT_ID &>/dev/null; then
        echo "✅ $secret_name existe"
        return 0
    else
        if [ "$is_optional" = true ]; then
            echo "⚠️  $secret_name NO existe (opcional)"
            return 0
        else
            echo "❌ $secret_name NO existe - REQUERIDO"
            return 1
        fi
    fi
}

# Variables de entorno requeridas
REQUIRED_SECRETS=(
    "firebase-api-key"
    "firebase-auth-domain" 
    "firebase-project-id"
    "firebase-storage-bucket"
    "firebase-messaging-sender-id"
    "firebase-app-id"
    "wsp-token"
    "webhook-verify-token"
)

# Variables opcionales
OPTIONAL_SECRETS=(
    "firebase-measurement-id"
)

echo ""
echo "🔐 Verificando secretos requeridos..."
missing_secrets=0

for secret in "${REQUIRED_SECRETS[@]}"; do
    if ! check_secret $secret; then
        missing_secrets=$((missing_secrets + 1))
    fi
done

echo ""
echo "📝 Verificando secretos opcionales..."
for secret in "${OPTIONAL_SECRETS[@]}"; do
    check_secret $secret true
done

echo ""
echo "🔑 Verificando permisos de acceso..."

# Verificar que el usuario actual tenga permisos para acceder a los secretos
current_user=$(gcloud config get-value account)
if [ -z "$current_user" ]; then
    echo "❌ No hay usuario autenticado en gcloud"
    echo "   Ejecute: gcloud auth login"
    exit 1
fi

echo "👤 Usuario actual: $current_user"

# Verificar permisos IAM básicos
echo "🛡️  Verificando permisos IAM..."
required_roles=(
    "roles/secretmanager.secretAccessor"
    "roles/run.admin"
    "roles/storage.admin"
)

missing_roles=0
for role in "${required_roles[@]}"; do
    if gcloud projects get-iam-policy $PROJECT_ID \
        --flatten="bindings[].members" \
        --filter="bindings.role:$role AND bindings.members:user:$current_user" \
        --format="value(bindings.role)" | grep -q "$role"; then
        echo "✅ $role"
    else
        echo "❌ $role - FALTA"
        missing_roles=$((missing_roles + 1))
    fi
done

echo ""
echo "📊 Resumen de validación:"
echo "   Secretos faltantes: $missing_secrets"
echo "   Roles faltantes: $missing_roles"

if [ $missing_secrets -gt 0 ]; then
    echo ""
    echo "❌ FALTAN SECRETOS REQUERIDOS"
    echo "   Para configurar los secretos, ejecute:"
    echo "   ./scripts/setup-secrets.sh"
    echo ""
    echo "   O configure manualmente usando:"
    echo "   gcloud secrets create SECRET_NAME --data-file=- --project=$PROJECT_ID"
    exit 1
fi

if [ $missing_roles -gt 0 ]; then
    echo ""
    echo "❌ FALTAN PERMISOS IAM"
    echo "   Contacte al administrador para agregar los roles faltantes, o ejecute:"
    for role in "${required_roles[@]}"; do
        echo "   gcloud projects add-iam-policy-binding $PROJECT_ID \\"
        echo "       --member=\"user:$current_user\" \\"
        echo "       --role=\"$role\""
    done
    exit 1
fi

echo ""
echo "✅ TODOS LOS SECRETOS Y PERMISOS ESTÁN CONFIGURADOS CORRECTAMENTE"
echo "🚀 Puede proceder con el deployment"

# Verificar herramientas necesarias
echo ""
echo "🔧 Verificando herramientas requeridas..."
tools=("gcloud" "docker" "terragrunt")
missing_tools=0

for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        echo "✅ $tool está instalado"
    else
        echo "❌ $tool NO está instalado"
        missing_tools=$((missing_tools + 1))
    fi
done

if [ $missing_tools -gt 0 ]; then
    echo ""
    echo "❌ FALTAN HERRAMIENTAS REQUERIDAS"
    echo "   Instale las herramientas faltantes antes de continuar"
    exit 1
fi

echo ""
echo "🎉 VALIDACIÓN COMPLETADA EXITOSAMENTE"
echo "   Todo está listo para el deployment!"
