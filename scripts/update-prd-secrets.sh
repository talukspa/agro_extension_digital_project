#!/bin/bash

# Script para actualizar secretos de WhatsApp en entorno PRD

PROJECT_ID="agro-extension-digital-prd"

echo "🔐 Actualizando token de WhatsApp para producción (PRD)..."
echo "📋 Proyecto: $PROJECT_ID"
echo "📝 Solo se actualizará el token de WhatsApp (wsp-token)"
echo "   El token de verificación del webhook se mantendrá igual."
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

# Verificar que el proyecto esté configurado
current_project=$(gcloud config get-value project)
if [ "$current_project" != "$PROJECT_ID" ]; then
    echo "⚠️  El proyecto configurado es '$current_project', cambiando a '$PROJECT_ID'"
    gcloud config set project "$PROJECT_ID"
fi

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

# Obtener valor del token de WhatsApp
WSP_TOKEN="${WSP_TOKEN:-}"

if [ -z "$WSP_TOKEN" ]; then
    echo "⚠️  WSP_TOKEN no está definido en el entorno"
    echo "   Por favor exporte WSP_TOKEN con el nuevo token de WhatsApp"
    read -p "¿Desea ingresar el token manualmente? (y/n): " response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        read -p "WhatsApp Token: " WSP_TOKEN
    else
        echo "❌ No se puede continuar sin el token de WhatsApp"
        exit 1
    fi
fi

echo ""
echo "💾 ACTUALIZANDO SECRETOS EN GOOGLE SECRET MANAGER..."
echo "==================================================="

# Actualizar token de WhatsApp
create_or_update_secret "wsp-token" "$WSP_TOKEN"

echo ""
echo "🔍 VERIFICACIÓN DEL TOKEN ACTUALIZADO"
echo "======================================"

echo ""
echo "📋 Listado de secretos en el proyecto:"
gcloud secrets list --project=$PROJECT_ID --format="table(name,createTime)"

echo ""
echo "✅ ACTUALIZACIÓN DEL TOKEN DE WHATSAPP COMPLETADA!"
echo ""
echo "🔒 RECORDATORIOS DE SEGURIDAD:"
echo "   - Los secretos están almacenados de forma segura en Google Secret Manager"
echo "   - NO commit estos valores en el repositorio"
echo "   - Rote los tokens regularmente"
echo "   - Mantenga un backup seguro de los valores críticos"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. El token de WhatsApp ha sido actualizado en Secret Manager"
echo "   2. El token se usará automáticamente en el próximo deployment"
echo "   3. Para desplegar los servicios de Cloud Run a PRD:"
echo "      - Opción A: GitHub Actions → 'Deploy with Terragrunt' → entorno=prd"
echo "      - Opción B: Ejecutar manualmente en cicd/prd:"
echo "          cd cicd/prd && terragrunt init && terragrunt apply -auto-approve"
echo ""