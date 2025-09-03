#!/bin/bash

# Script de despliegue completo para el entorno de desarrollo
# Incluye la configuración post-deployment para dominios de autenticación

set -e

STACK_PATH="/workspaces/agro_extension_digital_project/cicd/stacks/dev"
PROJECT_ID="agro-extension-digital-npe"

echo "🚀 Iniciando despliegue completo del entorno de desarrollo..."

# Función para verificar dependencias
check_dependencies() {
    echo "🔍 Verificando dependencias..."
    
    # Verificar Terragrunt
    if ! command -v terragrunt &> /dev/null; then
        echo "❌ Terragrunt no está instalado"
        exit 1
    fi
    
    # Verificar gcloud
    if ! command -v gcloud &> /dev/null; then
        echo "❌ Google Cloud SDK no está instalado"
        exit 1
    fi
    
    # Verificar autenticación
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 &> /dev/null; then
        echo "❌ No hay una cuenta autenticada en gcloud"
        echo "💡 Ejecuta: gcloud auth login"
        exit 1
    fi
    
    echo "✅ Dependencias verificadas"
}

# Función para desplegar módulos base
deploy_base_modules() {
    echo "📦 Desplegando módulos base..."
    
    # Secrets
    echo "🔐 Desplegando secrets..."
    cd "$STACK_PATH/secrets"
    terragrunt apply -auto-approve
    
    # Database
    echo "🗄️ Desplegando database..."
    cd "$STACK_PATH/database"
    terragrunt apply -auto-approve
    
    # Backend (si existe)
    if [ -d "$STACK_PATH/backend" ]; then
        echo "⚙️ Desplegando backend..."
        cd "$STACK_PATH/backend"
        terragrunt apply -auto-approve
    fi
    
    # Frontend
    echo "🌐 Desplegando frontend..."
    cd "$STACK_PATH/frontend"
    terragrunt apply -auto-approve
    
    echo "✅ Módulos base desplegados"
}

# Función para ejecutar post-deployment
run_post_deployment() {
    echo "🔧 Ejecutando configuración post-deployment..."
    
    cd "$STACK_PATH/post-deployment"
    
    # Aplicar configuración post-deployment
    terragrunt apply -auto-approve
    
    echo "✅ Post-deployment completado"
}

# Función para verificar el despliegue
verify_deployment() {
    echo "🧪 Verificando despliegue..."
    
    # Verificar frontend
    FRONTEND_URL=$(cd "$STACK_PATH/frontend" && terragrunt output -raw service_url)
    echo "🌐 Frontend URL: $FRONTEND_URL"
    
    # Verificar que el frontend responda
    if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" | grep -q "200\|301\|302"; then
        echo "✅ Frontend responde correctamente"
    else
        echo "⚠️ Frontend no responde como se esperaba"
    fi
    
    # Verificar dominios autorizados
    echo "🔐 Verificando dominios autorizados..."
    DOMAIN=$(echo "$FRONTEND_URL" | sed 's|https\?://||')
    
    if gcloud alpha identity domains list --project="$PROJECT_ID" --format="value(domain)" | grep -q "$DOMAIN"; then
        echo "✅ Dominio autorizado configurado correctamente"
    else
        echo "⚠️ Dominio no encontrado en lista de autorizados"
    fi
    
    echo "✅ Verificación completada"
}

# Función principal
main() {
    echo "🎯 Proyecto: $PROJECT_ID"
    echo "📁 Stack path: $STACK_PATH"
    echo ""
    
    check_dependencies
    deploy_base_modules
    run_post_deployment
    verify_deployment
    
    echo ""
    echo "🎉 ¡Despliegue completo exitoso!"
    echo ""
    echo "📋 URLs importantes:"
    FRONTEND_URL=$(cd "$STACK_PATH/frontend" && terragrunt output -raw service_url 2>/dev/null || echo "No disponible")
    echo "   🌐 Frontend: $FRONTEND_URL"
    echo ""
    echo "📝 Próximos pasos:"
    echo "   1. Probar la aplicación en el navegador"
    echo "   2. Verificar autenticación OAuth"
    echo "   3. Probar funcionalidades multi-tenant"
}

# Ejecutar función principal
main "$@"
