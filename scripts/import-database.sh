#!/bin/bash

# Script para importar la base de datos Firestore existente en Terragrunt
# Este script debe ejecutarse para conectar el recurso existente con Terraform

set -e

# Configuración
PROJECT_ID="agro-extension-digital-npe"
DATABASE_NAME="agro-extension-db"
ENVIRONMENT=${1:-dev}

echo "🔥 Importando base de datos Firestore en Terragrunt..."
echo "📋 Proyecto: $PROJECT_ID"
echo "🗄️ Base de datos: $DATABASE_NAME"
echo "🏗️ Ambiente: $ENVIRONMENT"
echo ""

# Verificar autenticación
current_user=$(gcloud config get-value account)
if [ -z "$current_user" ]; then
    echo "❌ No hay usuario autenticado en gcloud"
    echo "   Ejecute: gcloud auth login"
    exit 1
fi

echo "👤 Usuario autenticado: $current_user"

# Verificar que la base de datos existe
echo "🔍 Verificando que la base de datos existe..."
if ! gcloud firestore databases describe $DATABASE_NAME --project=$PROJECT_ID &>/dev/null; then
    echo "❌ La base de datos $DATABASE_NAME no existe en el proyecto $PROJECT_ID"
    echo "   Primero debe crear la base de datos manualmente o ejecutar 'terragrunt apply'"
    exit 1
fi

echo "✅ Base de datos $DATABASE_NAME encontrada"

# Navegar al directorio de Terragrunt
TERRAGRUNT_DIR="/workspaces/agro_extension_digital_project/cicd/stacks/$ENVIRONMENT/database"

if [ ! -d "$TERRAGRUNT_DIR" ]; then
    echo "❌ Directorio de Terragrunt no encontrado: $TERRAGRUNT_DIR"
    exit 1
fi

echo "📁 Navegando a: $TERRAGRUNT_DIR"
cd "$TERRAGRUNT_DIR"

# Inicializar Terragrunt
echo "🚀 Inicializando Terragrunt..."
terragrunt init

# Generar el resource address correcto para Firestore
RESOURCE_ADDRESS="google_firestore_database.agro_extension_db"
DATABASE_RESOURCE_ID="projects/$PROJECT_ID/databases/$DATABASE_NAME"

echo ""
echo "📥 IMPORTANDO RECURSO DE BASE DE DATOS"
echo "==============================================="
echo "Resource Address: $RESOURCE_ADDRESS"
echo "Database ID: $DATABASE_RESOURCE_ID"
echo ""

# Intentar importar el recurso
echo "⬇️ Ejecutando importación..."
if terragrunt import "$RESOURCE_ADDRESS" "$DATABASE_RESOURCE_ID"; then
    echo "✅ Base de datos importada exitosamente!"
else
    echo "⚠️ Error durante la importación. Esto puede ser normal si el recurso ya está importado."
    echo "   Verificando estado actual..."
fi

echo ""
echo "📊 VERIFICANDO ESTADO DESPUÉS DE LA IMPORTACIÓN"
echo "==============================================="

# Verificar que el recurso está en el state
echo "🔍 Verificando recursos en el state..."
terragrunt state list

echo ""
echo "📋 Verificando configuración específica de la base de datos..."
if terragrunt state show "$RESOURCE_ADDRESS" 2>/dev/null; then
    echo "✅ Recurso de base de datos está correctamente importado"
else
    echo "⚠️ Recurso no encontrado en el state, pero puede estar configurado correctamente"
fi

echo ""
echo "🔄 EJECUTANDO PLAN PARA VERIFICAR SINCRONIZACIÓN"
echo "==============================================="

# Ejecutar plan para ver si hay diferencias
echo "📝 Ejecutando 'terragrunt plan' para verificar sincronización..."
if terragrunt plan -detailed-exitcode; then
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✅ ¡Perfecto! La configuración está sincronizada con la infraestructura existente"
    elif [ $exit_code -eq 2 ]; then
        echo "⚠️ Hay diferencias entre la configuración y la infraestructura actual"
        echo "   Revise el plan anterior y considere ejecutar 'terragrunt apply' si los cambios son deseados"
    fi
else
    echo "❌ Error al ejecutar el plan. Revise la configuración."
    exit 1
fi

echo ""
echo "✅ IMPORTACIÓN COMPLETADA"
echo "========================"
echo "📋 Próximos pasos:"
echo "   1. Revisar el plan mostrado arriba"
echo "   2. Si hay cambios deseados, ejecutar: terragrunt apply"
echo "   3. Si todo está correcto, la base de datos ya está gestionada por Terragrunt"
echo ""
echo "🔗 Para verificar el estado:"
echo "   terragrunt state list"
echo "   terragrunt state show $RESOURCE_ADDRESS"
echo ""
echo "🚀 Para aplicar cambios:"
echo "   terragrunt apply"
