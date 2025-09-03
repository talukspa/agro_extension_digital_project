#!/bin/bash

# Script de deployment completo para CiruelaCertificada Frontend
# Automatiza todo el proceso de build y deploy a Google Cloud Run

set -e

PROJECT_ID="agro-extension-digital-npe"
REPOSITORY="us-central1-docker.pkg.dev/${PROJECT_ID}/agents"
IMAGE_NAME="agent-frontend-app"
TAG="latest"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con color
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_message $BLUE "🍇 CiruelaCertificada - Frontend Deployment Script"
print_message $BLUE "=================================================="
echo ""

# Verificar argumentos
ENVIRONMENT=${1:-dev}
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prd" ]]; then
    print_message $RED "❌ Entorno inválido. Use 'dev' o 'prd'"
    echo "Uso: $0 [dev|prd]"
    exit 1
fi

print_message $YELLOW "🎯 Entorno objetivo: $ENVIRONMENT"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ] && [ ! -d "frontend" ]; then
    print_message $RED "❌ Error: Ejecutar desde el directorio raíz del proyecto"
    echo "El script debe ejecutarse desde /workspaces/agro_extension_digital_project"
    exit 1
fi

# Navegar al directorio correcto si es necesario
if [ -d "frontend" ]; then
    FRONTEND_DIR="frontend"
    ROOT_DIR="."
else
    FRONTEND_DIR="."
    ROOT_DIR=".."
fi

print_message $BLUE "📂 Directorio frontend: $FRONTEND_DIR"

# Verificar prerrequisitos
print_message $YELLOW "🔍 Verificando prerrequisitos..."

# Verificar herramientas
REQUIRED_TOOLS=("gcloud" "docker" "terragrunt" "pnpm")
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v $tool &> /dev/null; then
        print_message $RED "❌ $tool no está instalado"
        exit 1
    fi
    print_message $GREEN "✅ $tool está disponible"
done

# Verificar autenticación
print_message $YELLOW "🔑 Verificando autenticación Google Cloud..."
current_user=$(gcloud config get-value account 2>/dev/null)
if [ -z "$current_user" ]; then
    print_message $RED "❌ No hay sesión activa de gcloud"
    echo "Ejecute: gcloud auth login && gcloud auth application-default login"
    exit 1
fi

current_project=$(gcloud config get-value project 2>/dev/null)
if [ "$current_project" != "$PROJECT_ID" ]; then
    print_message $YELLOW "⚠️  Configurando proyecto: $PROJECT_ID"
    gcloud config set project $PROJECT_ID
fi

print_message $GREEN "✅ Autenticado como: $current_user"
print_message $GREEN "✅ Proyecto configurado: $PROJECT_ID"

# Verificar secretos
print_message $YELLOW "🔐 Verificando secretos requeridos..."
if [ -f "$ROOT_DIR/scripts/validate-secrets.sh" ]; then
    if ! $ROOT_DIR/scripts/validate-secrets.sh; then
        print_message $RED "❌ Faltan secretos requeridos"
        echo "Ejecute: $ROOT_DIR/scripts/setup-secrets.sh"
        exit 1
    fi
    print_message $GREEN "✅ Todos los secretos están configurados"
else
    print_message $YELLOW "⚠️  Script de validación de secretos no encontrado, continuando..."
fi

# Configurar Docker para Artifact Registry
print_message $YELLOW "🐳 Configurando Docker para Artifact Registry..."
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
print_message $GREEN "✅ Docker configurado"

# Instalar dependencias
print_message $YELLOW "📦 Instalando dependencias..."
cd $FRONTEND_DIR
pnpm install --frozen-lockfile
print_message $GREEN "✅ Dependencias instaladas"

# Ejecutar tests de tipos
print_message $YELLOW "🔍 Verificando tipos TypeScript..."
if ! pnpm type-check; then
    print_message $RED "❌ Errores de tipos encontrados"
    read -p "¿Continuar de todas formas? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
print_message $GREEN "✅ Verificación de tipos completada"

# Linting
print_message $YELLOW "🧹 Ejecutando linting..."
if ! pnpm lint; then
    print_message $YELLOW "⚠️  Problemas de linting encontrados"
    read -p "¿Continuar de todas formas? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
print_message $GREEN "✅ Linting completado"

# Build de Next.js
print_message $YELLOW "🔨 Construyendo aplicación Next.js..."
if ! pnpm build; then
    print_message $RED "❌ Error en el build de Next.js"
    exit 1
fi
print_message $GREEN "✅ Build de Next.js completado"

# Build de imagen Docker
print_message $YELLOW "🐳 Construyendo imagen Docker..."
FULL_IMAGE_NAME="${REPOSITORY}/${IMAGE_NAME}:${TAG}"
if ! docker build -t "$FULL_IMAGE_NAME" .; then
    print_message $RED "❌ Error al construir imagen Docker"
    exit 1
fi
print_message $GREEN "✅ Imagen Docker construida: $FULL_IMAGE_NAME"

# Push de la imagen
print_message $YELLOW "📤 Subiendo imagen a Artifact Registry..."
if ! docker push "$FULL_IMAGE_NAME"; then
    print_message $RED "❌ Error al subir imagen"
    exit 1
fi
print_message $GREEN "✅ Imagen subida exitosamente"

# Deploy con Terragrunt
print_message $YELLOW "🚀 Desplegando con Terragrunt..."
cd "$ROOT_DIR/cicd/stacks/${ENVIRONMENT}/frontend"

# Verificar que el archivo terragrunt.hcl existe
if [ ! -f "terragrunt.hcl" ]; then
    print_message $RED "❌ Archivo terragrunt.hcl no encontrado en $(pwd)"
    exit 1
fi

# Inicializar Terragrunt si es necesario
if [ ! -d ".terragrunt-cache" ]; then
    print_message $YELLOW "🔧 Inicializando Terragrunt..."
    terragrunt init
fi

# Planificar deployment
print_message $YELLOW "📋 Planificando deployment..."
if ! terragrunt plan; then
    print_message $RED "❌ Error en el plan de Terragrunt"
    exit 1
fi

# Aplicar deployment
print_message $YELLOW "🔄 Aplicando deployment..."
if ! terragrunt apply -auto-approve; then
    print_message $RED "❌ Error en el deployment"
    exit 1
fi

print_message $GREEN "✅ Deployment completado exitosamente!"

# Obtener URL del servicio
print_message $YELLOW "🌐 Obteniendo URL del servicio..."
SERVICE_URL=$(gcloud run services describe "frontend-app-${ENVIRONMENT}" \
    --region=us-central1 \
    --project=${PROJECT_ID} \
    --format="value(status.url)" 2>/dev/null || echo "No disponible")

echo ""
print_message $GREEN "🎉 DEPLOYMENT COMPLETADO EXITOSAMENTE!"
print_message $BLUE "=================================================="
echo ""
print_message $BLUE "📊 Resumen del deployment:"
echo "   • Entorno: $ENVIRONMENT"
echo "   • Imagen: $FULL_IMAGE_NAME"
echo "   • Servicio: frontend-app-${ENVIRONMENT}"
echo "   • Región: us-central1"
echo "   • Proyecto: $PROJECT_ID"
echo ""
print_message $BLUE "🌐 URL del servicio:"
echo "   $SERVICE_URL"
echo ""
print_message $YELLOW "🔧 Comandos útiles:"
echo "   • Ver logs: gcloud run services logs read frontend-app-${ENVIRONMENT} --region=us-central1"
echo "   • Ver servicio: gcloud run services describe frontend-app-${ENVIRONMENT} --region=us-central1"
echo "   • Rollback: terragrunt destroy (⚠️  cuidado!)"
echo ""
print_message $GREEN "✨ ¡CiruelaCertificada está listo para usar!"
