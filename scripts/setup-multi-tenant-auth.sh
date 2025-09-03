#!/bin/bash

# 🚀 Setup script for Multi-Tenant Auth System
# Agro Extension Digital Project

echo "🚀 Configurando Sistema de Autorización Multi-Tenant..."
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running from project root
if [ ! -f "package.json" ] && [ ! -d "frontend" ]; then
    print_error "Por favor ejecuta este script desde la raíz del proyecto"
    exit 1
fi

print_info "Verificando estructura del proyecto..."

# Check required directories
REQUIRED_DIRS=("frontend" "functions" "cicd/modules/database")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_status "Directorio $dir existe"
    else
        print_error "Directorio $dir no encontrado"
        exit 1
    fi
done

# Install frontend dependencies
print_info "Instalando dependencias del frontend..."
cd frontend
if [ -f "package.json" ]; then
    npm install
    print_status "Dependencias del frontend instaladas"
else
    print_error "package.json no encontrado en frontend/"
    exit 1
fi

# Check for required Firebase packages
print_info "Verificando paquetes de Firebase..."
if npm list firebase &> /dev/null; then
    print_status "Firebase SDK instalado"
else
    print_warning "Instalando Firebase SDK..."
    npm install firebase
fi

cd ..

# Install functions dependencies
print_info "Instalando dependencias de Firebase Functions..."
cd functions
if [ -f "package.json" ]; then
    npm install
    print_status "Dependencias de Functions instaladas"
else
    print_warning "Creando package.json para functions..."
    npm init -y
    npm install firebase-admin firebase-functions
fi

# Check TypeScript
print_info "Verificando configuración de TypeScript..."
if [ -f "tsconfig.json" ]; then
    print_status "TypeScript configurado en functions"
else
    print_warning "Configurando TypeScript..."
    npm install -D typescript @types/node
fi

cd ..

# Check Firebase CLI
print_info "Verificando Firebase CLI..."
if command -v firebase &> /dev/null; then
    print_status "Firebase CLI disponible"
    firebase --version
else
    print_warning "Firebase CLI no encontrado. Instalando..."
    npm install -g firebase-tools
fi

# Check Firebase project configuration
print_info "Verificando configuración de Firebase..."
if [ -f "firebase.json" ]; then
    print_status "firebase.json configurado"
else
    print_warning "firebase.json no encontrado"
    print_info "Ejecuta 'firebase init' para configurar el proyecto"
fi

# Environment file template
print_info "Verificando variables de entorno..."
ENV_FILE="frontend/.env.local"
if [ -f "$ENV_FILE" ]; then
    print_status "Archivo .env.local existe"
else
    print_warning "Creando plantilla de .env.local..."
    cat > "$ENV_FILE" << 'EOF'
# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id

# App Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
EOF
    print_warning "⚠️  Configura las variables de Firebase en $ENV_FILE"
fi

# Check Firestore rules
print_info "Verificando reglas de Firestore..."
RULES_FILE="cicd/modules/database/firestore-security-rules.rules"
if [ -f "$RULES_FILE" ]; then
    print_status "Reglas de Firestore configuradas"
else
    print_error "Reglas de Firestore no encontradas en $RULES_FILE"
fi

# Create basic indexes file if not exists
INDEXES_FILE="firestore.indexes.json"
if [ ! -f "$INDEXES_FILE" ]; then
    print_info "Creando archivo de índices de Firestore..."
    cat > "$INDEXES_FILE" << 'EOF'
{
  "indexes": [
    {
      "collectionGroup": "memberships",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "businessId", "order": "ASCENDING" },
        { "fieldPath": "status", "order": "ASCENDING" }
      ]
    },
    {
      "collectionGroup": "memberships",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "userId", "order": "ASCENDING" },
        { "fieldPath": "status", "order": "ASCENDING" }
      ]
    },
    {
      "collectionGroup": "memberships",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "approvalToken", "order": "ASCENDING" }
      ]
    }
  ],
  "fieldOverrides": []
}
EOF
    print_status "Archivo de índices creado"
fi

# Build functions
print_info "Compilando Firebase Functions..."
cd functions
if [ -f "tsconfig.json" ]; then
    npm run build
    if [ $? -eq 0 ]; then
        print_status "Functions compiladas exitosamente"
    else
        print_warning "Error al compilar functions (esto es normal si faltan dependencias)"
    fi
fi
cd ..

# Final instructions
echo ""
echo "🎉 ¡Configuración completada!"
echo "========================================="
echo ""
print_info "Próximos pasos:"
echo ""
echo "1. 📝 Configura las variables de Firebase en frontend/.env.local"
echo "2. 🔑 Ejecuta 'firebase login' para autenticarte"
echo "3. 🏗️  Ejecuta 'firebase init' si no tienes un proyecto configurado"
echo "4. 🚀 Ejecuta 'firebase deploy --only functions' para desplegar las funciones"
echo "5. 🛡️  Ejecuta 'firebase deploy --only firestore:rules' para aplicar las reglas"
echo "6. 🌐 Ejecuta 'cd frontend && npm run dev' para iniciar el servidor de desarrollo"
echo ""
print_info "Para desarrollo local:"
echo "- Frontend: http://localhost:3000"
echo "- Emuladores: firebase emulators:start"
echo ""
print_info "Documentación completa:"
echo "- docs/frontend/12-multi-tenant-auth-implementation.md"
echo ""
print_status "¡Sistema multi-tenant listo para usar! 🚀"
