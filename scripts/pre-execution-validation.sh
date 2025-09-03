#!/bin/bash

# Script de validación pre-ejecución
# Verifica que todos los componentes estén listos para la implementación

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
CHECKS_TOTAL=0
CHECKS_PASSED=0
CHECKS_FAILED=0

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((CHECKS_PASSED++))
}

warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
    ((CHECKS_FAILED++))
}

check() {
    ((CHECKS_TOTAL++))
    echo -e "${BLUE}[?]${NC} Verificando: $1"
}

# Función principal de validación
validate_system() {
    log "🔍 Iniciando validación del sistema para implementación"
    
    # Verificar herramientas
    validate_tools
    
    # Verificar configuración
    validate_configuration
    
    # Verificar archivos
    validate_files
    
    # Verificar permisos
    validate_permissions
    
    # Verificar conectividad
    validate_connectivity
    
    # Mostrar resumen
    show_summary
}

validate_tools() {
    log "🛠️ Verificando herramientas requeridas..."
    
    check "gcloud CLI"
    if command -v gcloud &> /dev/null; then
        local version=$(gcloud version --format="value(Google Cloud SDK)" 2>/dev/null || echo "unknown")
        success "gcloud CLI instalado (versión: $version)"
    else
        error "gcloud CLI no encontrado - Instalar: https://cloud.google.com/sdk/docs/install"
    fi
    
    check "Terragrunt"
    if command -v terragrunt &> /dev/null; then
        local version=$(terragrunt --version 2>/dev/null | head -n1 || echo "unknown")
        success "Terragrunt instalado ($version)"
    else
        error "Terragrunt no encontrado - Instalar: https://terragrunt.gruntwork.io/docs/getting-started/install/"
    fi
    
    check "Node.js"
    if command -v node &> /dev/null; then
        local version=$(node --version 2>/dev/null || echo "unknown")
        success "Node.js instalado ($version)"
        if [[ "${version}" < "v18" ]]; then
            warning "Se recomienda Node.js >= 18"
        fi
    else
        error "Node.js no encontrado - Instalar: https://nodejs.org/"
    fi
    
    check "pnpm"
    if command -v pnpm &> /dev/null; then
        local version=$(pnpm --version 2>/dev/null || echo "unknown")
        success "pnpm instalado (versión: $version)"
    else
        warning "pnpm no encontrado - Instalar: npm install -g pnpm"
    fi
    
    check "Git"
    if command -v git &> /dev/null; then
        local version=$(git --version 2>/dev/null || echo "unknown")
        success "Git instalado ($version)"
    else
        error "Git no encontrado"
    fi
}

validate_configuration() {
    log "⚙️ Verificando configuración..."
    
    check "Variables de entorno"
    if [[ -n "${PROJECT_ID:-}" ]]; then
        success "PROJECT_ID configurado: $PROJECT_ID"
    else
        error "PROJECT_ID no configurado - Exportar: export PROJECT_ID='tu-proyecto'"
    fi
    
    if [[ -n "${ENVIRONMENT:-}" ]]; then
        success "ENVIRONMENT configurado: $ENVIRONMENT"
    else
        warning "ENVIRONMENT no configurado - Por defecto: dev"
        export ENVIRONMENT="dev"
    fi
    
    check "Autenticación gcloud"
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -n1 &> /dev/null; then
        local account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -n1)
        success "Autenticado con: $account"
    else
        error "No hay cuenta activa - Ejecutar: gcloud auth login"
    fi
    
    check "Proyecto gcloud"
    local current_project=$(gcloud config get-value project 2>/dev/null || echo "")
    if [[ -n "$current_project" ]]; then
        success "Proyecto configurado: $current_project"
        if [[ -n "${PROJECT_ID:-}" && "$current_project" != "$PROJECT_ID" ]]; then
            warning "Proyecto actual ($current_project) != PROJECT_ID ($PROJECT_ID)"
        fi
    else
        error "Proyecto no configurado - Ejecutar: gcloud config set project PROJECT_ID"
    fi
}

validate_files() {
    log "📁 Verificando estructura de archivos..."
    
    # Documentación
    check "Documentación frontend"
    local docs_path="/workspaces/agro_extension_digital_project/docs/frontend"
    if [[ -d "$docs_path" ]]; then
        success "Directorio de documentación existe"
        
        local required_docs=(
            "00-setup-guide.md"
            "01-authN-authZ.md"
            "07-updated-database-schema.md"
            "09-master-execution-plan.md"
        )
        
        for doc in "${required_docs[@]}"; do
            if [[ -f "$docs_path/$doc" ]]; then
                success "Documento encontrado: $doc"
            else
                error "Documento faltante: $doc"
            fi
        done
    else
        error "Directorio de documentación no encontrado: $docs_path"
    fi
    
    # Scripts
    check "Scripts de automatización"
    local scripts_path="/workspaces/agro_extension_digital_project/scripts"
    if [[ -d "$scripts_path" ]]; then
        success "Directorio de scripts existe"
        
        local required_scripts=(
            "setup-secrets.sh"
            "validate-secrets.sh"
            "migrate-database-schema.sh"
            "deploy-frontend.sh"
        )
        
        for script in "${required_scripts[@]}"; do
            if [[ -f "$scripts_path/$script" ]]; then
                if [[ -x "$scripts_path/$script" ]]; then
                    success "Script ejecutable: $script"
                else
                    warning "Script no ejecutable: $script (ejecutar: chmod +x)"
                fi
            else
                error "Script faltante: $script"
            fi
        done
    else
        error "Directorio de scripts no encontrado: $scripts_path"
    fi
    
    # Infraestructura
    check "Módulos Terraform"
    local modules_path="/workspaces/agro_extension_digital_project/cicd/modules"
    if [[ -d "$modules_path" ]]; then
        success "Directorio de módulos existe"
        
        if [[ -f "$modules_path/database/main.tf" ]]; then
            if [[ -s "$modules_path/database/main.tf" ]]; then
                success "Módulo de base de datos configurado"
            else
                error "Módulo de base de datos está vacío"
            fi
        else
            error "Módulo de base de datos no encontrado"
        fi
        
        if [[ -f "$modules_path/database/firestore-security-rules.rules" ]]; then
            success "Reglas de seguridad Firestore encontradas"
        else
            warning "Reglas de seguridad Firestore no encontradas"
        fi
    else
        error "Directorio de módulos no encontrado: $modules_path"
    fi
    
    # Stacks Terragrunt
    check "Configuración Terragrunt"
    local stacks_path="/workspaces/agro_extension_digital_project/cicd/stacks"
    if [[ -d "$stacks_path" ]]; then
        success "Directorio de stacks existe"
        
        for env in dev prd; do
            if [[ -d "$stacks_path/$env" ]]; then
                success "Configuración para ambiente: $env"
            else
                warning "Configuración faltante para ambiente: $env"
            fi
        done
    else
        error "Directorio de stacks no encontrado: $stacks_path"
    fi
    
    # Frontend
    check "Aplicación Frontend"
    local frontend_path="/workspaces/agro_extension_digital_project/frontend"
    if [[ -d "$frontend_path" ]]; then
        success "Directorio frontend existe"
        
        if [[ -f "$frontend_path/package.json" ]]; then
            success "package.json encontrado"
        else
            error "package.json no encontrado en frontend"
        fi
        
        if [[ -f "$frontend_path/next.config.ts" || -f "$frontend_path/next.config.js" ]]; then
            success "Configuración Next.js encontrada"
        else
            warning "Configuración Next.js no encontrada"
        fi
    else
        error "Directorio frontend no encontrado: $frontend_path"
    fi
}

validate_permissions() {
    log "🔐 Verificando permisos..."
    
    if [[ -z "${PROJECT_ID:-}" ]]; then
        warning "PROJECT_ID no configurado - saltando verificación de permisos"
        return
    fi
    
    check "Permisos Firestore"
    if gcloud firestore databases list --project="$PROJECT_ID" &>/dev/null; then
        success "Permisos de Firestore confirmados"
    else
        error "Sin permisos de Firestore - Rol requerido: roles/datastore.owner"
    fi
    
    check "Permisos Secret Manager"
    if gcloud secrets list --project="$PROJECT_ID" &>/dev/null; then
        success "Permisos de Secret Manager confirmados"
    else
        error "Sin permisos de Secret Manager - Rol requerido: roles/secretmanager.admin"
    fi
    
    check "Permisos Cloud Run"
    if gcloud run services list --project="$PROJECT_ID" &>/dev/null; then
        success "Permisos de Cloud Run confirmados"
    else
        error "Sin permisos de Cloud Run - Rol requerido: roles/run.admin"
    fi
    
    check "Permisos IAM"
    if gcloud projects get-iam-policy "$PROJECT_ID" --flatten="bindings[].members" --filter="bindings.members:user:$(gcloud config get-value account)" &>/dev/null; then
        success "Permisos IAM confirmados"
    else
        warning "No se pudieron verificar permisos IAM"
    fi
}

validate_connectivity() {
    log "🌐 Verificando conectividad..."
    
    check "Conectividad Google Cloud APIs"
    if curl -s -f "https://www.googleapis.com/discovery/v1/apis" &>/dev/null; then
        success "APIs de Google Cloud accesibles"
    else
        error "No se puede acceder a APIs de Google Cloud"
    fi
    
    check "Conectividad Firebase"
    if curl -s -f "https://firebase.googleapis.com/v1beta1/projects" &>/dev/null; then
        success "APIs de Firebase accesibles"
    else
        warning "No se puede acceder a APIs de Firebase"
    fi
    
    check "Conectividad GitHub (para clonado)"
    if curl -s -f "https://api.github.com" &>/dev/null; then
        success "GitHub accesible"
    else
        warning "GitHub no accesible (puede afectar dependencias)"
    fi
    
    check "Conectividad npm registry"
    if curl -s -f "https://registry.npmjs.org/" &>/dev/null; then
        success "npm registry accesible"
    else
        warning "npm registry no accesible (puede afectar instalación de dependencias)"
    fi
}

show_summary() {
    echo
    log "📊 Resumen de validación"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "Total de verificaciones: ${BLUE}$CHECKS_TOTAL${NC}"
    echo -e "Exitosas: ${GREEN}$CHECKS_PASSED${NC}"
    echo -e "Fallidas: ${RED}$CHECKS_FAILED${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ $CHECKS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✅ SISTEMA LISTO PARA IMPLEMENTACIÓN${NC}"
        echo -e "${GREEN}   Todos los componentes están configurados correctamente${NC}"
        echo
        echo -e "${BLUE}📋 Próximos pasos:${NC}"
        echo "   1. Revisar el plan de ejecución en docs/frontend/09-master-execution-plan.md"
        echo "   2. Coordinar ventana de mantenimiento con el equipo"
        echo "   3. Ejecutar las fases del plan en orden secuencial"
        echo
        echo -e "${YELLOW}⚠️  Recordatorio:${NC}"
        echo "   - Verificar que PROJECT_ID esté configurado correctamente"
        echo "   - Asegurar backup de datos antes de comenzar"
        echo "   - Tener plan de rollback preparado"
        
    elif [[ $CHECKS_FAILED -le 3 ]]; then
        echo -e "${YELLOW}⚠️  SISTEMA PARCIALMENTE LISTO${NC}"
        echo -e "${YELLOW}   Hay algunos problemas menores que deben resolverse${NC}"
        echo
        echo -e "${BLUE}📋 Acciones recomendadas:${NC}"
        echo "   1. Resolver los errores marcados arriba"
        echo "   2. Ejecutar este script nuevamente"
        echo "   3. Proceder con implementación cuando todo esté verde"
        
    else
        echo -e "${RED}❌ SISTEMA NO LISTO PARA IMPLEMENTACIÓN${NC}"
        echo -e "${RED}   Hay problemas críticos que deben resolverse${NC}"
        echo
        echo -e "${BLUE}📋 Acciones requeridas:${NC}"
        echo "   1. Resolver TODOS los errores listados arriba"
        echo "   2. Verificar documentación en docs/frontend/"
        echo "   3. Contactar al equipo técnico si necesitas ayuda"
        echo "   4. Re-ejecutar validación antes de continuar"
    fi
    
    echo
    log "🔗 Recursos útiles:"
    echo "   - Plan de ejecución: docs/frontend/09-master-execution-plan.md"
    echo "   - Guía de setup: docs/frontend/00-setup-guide.md"
    echo "   - Esquema de DB: docs/frontend/07-updated-database-schema.md"
    echo
}

# Ejecutar validación
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              🔍 VALIDACIÓN PRE-IMPLEMENTACIÓN                 ║"
    echo "║                    CiruelaCertificada                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    validate_system
    
    # Exit code basado en resultados
    if [[ $CHECKS_FAILED -eq 0 ]]; then
        exit 0
    elif [[ $CHECKS_FAILED -le 3 ]]; then
        exit 1
    else
        exit 2
    fi
}

# Ejecutar si es llamado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
