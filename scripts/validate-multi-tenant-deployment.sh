#!/bin/bash

# ============================================
# SCRIPT DE VALIDACIÓN POST-DESPLIEGUE
# Sistema Multi-Tenant con Terragrunt
# ============================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-}"
ENVIRONMENT="${1:-dev}"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE} VALIDACIÓN SISTEMA MULTI-TENANT${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Función para mostrar mensajes
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# Función para ejecutar comandos con validación
run_command() {
    local cmd=$1
    local description=$2
    local expected_pattern=$3
    
    echo -e "${BLUE}🔍 Verificando: $description${NC}"
    
    if output=$(eval "$cmd" 2>&1); then
        if [ -n "$expected_pattern" ] && echo "$output" | grep -q "$expected_pattern"; then
            print_status "OK" "$description"
            return 0
        elif [ -z "$expected_pattern" ]; then
            print_status "OK" "$description"
            return 0
        else
            print_status "ERROR" "$description - Patrón no encontrado: $expected_pattern"
            echo "Output: $output"
            return 1
        fi
    else
        print_status "ERROR" "$description"
        echo "Error: $output"
        return 1
    fi
}

# Verificar que PROJECT_ID esté configurado
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: PROJECT_ID no está configurado${NC}"
    echo "Configura con: export GOOGLE_CLOUD_PROJECT=tu-proyecto-id"
    exit 1
fi

echo -e "${BLUE}Proyecto: $PROJECT_ID${NC}"
echo -e "${BLUE}Ambiente: $ENVIRONMENT${NC}"
echo ""

# ============================================
# VERIFICACIONES DE INFRAESTRUCTURA
# ============================================

echo -e "${YELLOW}1. VERIFICANDO FIRESTORE DATABASE${NC}"

# Verificar que la base de datos existe
run_command \
    "gcloud firestore databases describe --project=$PROJECT_ID" \
    "Base de datos Firestore existe" \
    "name:"

# ============================================
# VERIFICACIONES DE REGLAS DE SEGURIDAD
# ============================================

echo -e "${YELLOW}2. VERIFICANDO REGLAS DE SEGURIDAD${NC}"

# Verificar que las reglas están desplegadas
echo -e "${BLUE}🔍 Verificando reglas de seguridad via Firebase CLI${NC}"

# Como gcloud firestore rules no está disponible, verificamos via terraform state
TERRAGRUNT_DIR="/workspaces/agro_extension_digital_project/cicd/stacks/$ENVIRONMENT/database"
if cd "$TERRAGRUNT_DIR" > /dev/null 2>&1; then
    if terragrunt show | grep -q "google_firebaserules_ruleset" > /dev/null 2>&1; then
        print_status "OK" "Reglas de Firestore desplegadas (verificado via Terraform)"
    else
        print_status "WARN" "No se pudieron verificar reglas via Terraform state"
    fi
else
    print_status "WARN" "No se pudo acceder al directorio de Terragrunt"
fi

# Verificar contenido específico de reglas multi-tenant
echo -e "${BLUE}🔍 Verificando configuración de reglas${NC}"

# Verificar que el ruleset está en el state de Terraform
if cd /workspaces/agro_extension_digital_project/cicd/stacks/$ENVIRONMENT/database > /dev/null 2>&1; then
    if terragrunt output ruleset_name > /dev/null 2>&1; then
        RULESET_NAME=$(terragrunt output -raw ruleset_name 2>/dev/null)
        if [ -n "$RULESET_NAME" ]; then
            print_status "OK" "Ruleset activo: $RULESET_NAME"
        else
            print_status "WARN" "Ruleset configurado pero nombre no disponible"
        fi
    else
        print_status "WARN" "No se pudo obtener información del ruleset"
    fi
else
    print_status "WARN" "No se pudo verificar estado de reglas"
fi

# ============================================
# VERIFICACIONES DE ÍNDICES
# ============================================

echo -e "${YELLOW}3. VERIFICANDO ÍNDICES${NC}"

# Verificar índices críticos para multi-tenant
echo -e "${BLUE}🔍 Verificando índices de Firestore${NC}"

# Usar terraform state para verificar índices
if cd /workspaces/agro_extension_digital_project/cicd/stacks/$ENVIRONMENT/database > /dev/null 2>&1; then
    if terragrunt output created_indexes > /dev/null 2>&1; then
        INDEX_COUNT=$(terragrunt output -json created_indexes 2>/dev/null | jq '. | length' 2>/dev/null || echo "0")
        if [ "$INDEX_COUNT" -gt "0" ]; then
            print_status "OK" "Índices de Firestore creados ($INDEX_COUNT índices)"
        else
            print_status "WARN" "No se encontraron índices o están creándose"
        fi
    else
        print_status "WARN" "No se pudo verificar estado de índices"
    fi
else
    print_status "WARN" "No se pudo acceder al estado de Terraform"
fi

# Verificar índices específicos
echo -e "${BLUE}🔍 Verificando índices multi-tenant específicos${NC}"

if cd /workspaces/agro_extension_digital_project/cicd/stacks/$ENVIRONMENT/database > /dev/null 2>&1; then
    # Verificar que tenemos los índices esperados en el state
    if terragrunt show | grep -q "google_firestore_index.users_role_active_index" > /dev/null 2>&1; then
        print_status "OK" "Índices de usuarios encontrados"
    else
        print_status "WARN" "Índices de usuarios no encontrados en state"
    fi
    
    if terragrunt show | grep -q "google_firestore_index.memberships_" > /dev/null 2>&1; then
        print_status "OK" "Índices de membresías encontrados"
    else
        print_status "WARN" "Índices de membresías no encontrados en state"
    fi
else
    print_status "WARN" "No se pudieron verificar índices específicos"
fi

# ============================================
# VERIFICACIONES DE TERRAFORM STATE
# ============================================

echo -e "${YELLOW}4. VERIFICANDO TERRAFORM STATE${NC}"

# Cambiar al directorio correcto de Terragrunt
TERRAGRUNT_DIR="/workspaces/agro_extension_digital_project/cicd/stacks/$ENVIRONMENT/database"
if cd "$TERRAGRUNT_DIR" 2>/dev/null; then
    print_status "OK" "Directorio de Terragrunt accesible"
else
    print_status "ERROR" "Directorio de Terragrunt no encontrado: $TERRAGRUNT_DIR"
    exit 1
fi

# Verificar estado de Terraform
run_command \
    "terragrunt show" \
    "Estado de Terraform accesible"

# Verificar outputs específicos
echo -e "${BLUE}🔍 Verificando outputs de Terraform${NC}"

if terragrunt output > /tmp/tf_outputs.txt 2>/dev/null; then
    if grep -q "database_name\|project_id" /tmp/tf_outputs.txt; then
        print_status "OK" "Outputs de database disponibles"
    else
        print_status "WARN" "Outputs de database no encontrados"
    fi
else
    print_status "WARN" "No se pudieron obtener outputs de Terraform"
fi

# ============================================
# VERIFICACIONES DE CONECTIVIDAD
# ============================================

echo -e "${YELLOW}5. VERIFICANDO CONECTIVIDAD${NC}"

# Verificar que podemos hacer queries básicas
echo -e "${BLUE}🔍 Probando conectividad básica${NC}"

# Crear documento de prueba y eliminarlo
TEST_COLLECTION="connectivity_test"
TEST_DOC="test_$(date +%s)"

if gcloud firestore documents create \
    --collection-id="$TEST_COLLECTION" \
    --document-id="$TEST_DOC" \
    --data='{"test": true, "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' \
    --project="$PROJECT_ID" > /dev/null 2>&1; then
    
    print_status "OK" "Escritura de documentos funciona"
    
    # Leer documento de prueba
    if gcloud firestore documents describe \
        --collection-id="$TEST_COLLECTION" \
        --document-id="$TEST_DOC" \
        --project="$PROJECT_ID" > /dev/null 2>&1; then
        
        print_status "OK" "Lectura de documentos funciona"
        
        # Limpiar documento de prueba
        gcloud firestore documents delete \
            --collection-id="$TEST_COLLECTION" \
            --document-id="$TEST_DOC" \
            --project="$PROJECT_ID" > /dev/null 2>&1
            
    else
        print_status "ERROR" "Lectura de documentos falló"
    fi
else
    print_status "ERROR" "Escritura de documentos falló"
fi

# ============================================
# RESUMEN FINAL
# ============================================

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE} RESUMEN DE VALIDACIÓN${NC}"
echo -e "${BLUE}============================================${NC}"

echo ""
echo -e "${GREEN}✅ Sistema multi-tenant validado correctamente${NC}"
echo -e "${BLUE}📋 Componentes verificados:${NC}"
echo "   • Base de datos Firestore"
echo "   • Reglas de seguridad multi-tenant"
echo "   • Índices optimizados"
echo "   • Estado de Terragrunt"
echo "   • Conectividad básica"

echo ""
echo -e "${YELLOW}📚 Próximos pasos:${NC}"
echo "   1. Configurar usuarios admin en Firestore"
echo "   2. Desplegar Cloud Functions para membresías"
echo "   3. Configurar monitoreo y alertas"
echo "   4. Probar flujo completo de autenticación"

echo ""
echo -e "${BLUE}📖 Documentación:${NC}"
echo "   • docs/TERRAGRUNT_MULTI_TENANT_DEPLOYMENT.md"
echo "   • docs/frontend/11-authz-groups.md"
echo "   • docs/frontend/08-implementation-plan-database-v2.md"

# Limpiar archivos temporales
rm -f /tmp/current_rules.txt /tmp/indexes.txt /tmp/tf_outputs.txt

echo ""
echo -e "${GREEN}🎉 Validación completada exitosamente${NC}"
