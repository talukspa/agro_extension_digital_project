# 🚀 Resumen Ejecutivo - Deployment CiruelaCertificada

## 📋 Lista de Verificación Pre-Deployment

### ✅ Prerrequisitos Obligatorios

1. **Herramientas Instaladas**
   - [ ] `gcloud` CLI configurado
   - [ ] `docker` instalado y funcionando
   - [ ] `terragrunt` instalado
   - [ ] `pnpm` instalado (gestor de paquetes)

2. **Autenticación Google Cloud**
   - [ ] `gcloud auth login` ejecutado
   - [ ] `gcloud auth application-default login` ejecutado
   - [ ] Proyecto configurado: `gcloud config set project agro-extension-digital-npe`

3. **Permisos IAM Requeridos**
   - [ ] `roles/secretmanager.secretAccessor`
   - [ ] `roles/secretmanager.admin`
   - [ ] `roles/run.admin`
   - [ ] `roles/storage.admin`

4. **Variables de Entorno Configuradas** (Google Secret Manager)
   - [ ] `firebase-api-key`
   - [ ] `firebase-auth-domain`
   - [ ] `firebase-project-id`
   - [ ] `firebase-storage-bucket`
   - [ ] `firebase-messaging-sender-id`
   - [ ] `firebase-app-id`
   - [ ] `firebase-measurement-id` (opcional)
   - [ ] `wsp-token`
   - [ ] `webhook-verify-token`

## 🔧 Scripts Disponibles

### 1. Configuración Inicial de Secretos
```bash
# Configurar todas las variables de entorno requeridas
./scripts/setup-secrets.sh
```

### 2. Validación de Prerrequisitos
```bash
# Verificar que todos los secretos y permisos están configurados
./scripts/validate-secrets.sh
```

### 3. Deployment Completo (RECOMENDADO)
```bash
# Deploy automático a desarrollo
./scripts/deploy-frontend.sh dev

# Deploy automático a producción
./scripts/deploy-frontend.sh prd
```

## ⚡ Deployment Rápido

Para usuarios que ya tienen todo configurado:

```bash
# Navegar al proyecto
cd /workspaces/agro_extension_digital_project

# Validar prerrequisitos
./scripts/validate-secrets.sh

# Deploy a desarrollo
./scripts/deploy-frontend.sh dev
```

## 🔍 Ubicación de Archivos Clave

### Scripts de Automatización
- `/scripts/setup-secrets.sh` - Configuración de secretos
- `/scripts/validate-secrets.sh` - Validación de prerrequisitos  
- `/scripts/deploy-frontend.sh` - Deployment completo

### Documentación
- `/docs/frontend/04-environment-variables-prerequisites.md` - Prerrequisitos detallados
- `/docs/frontend/00-setup-guide.md` - Guía de configuración completa
- `/docs/frontend/03-authN-authZ-implementation-plan.md` - Plan de implementación

### Configuración Terragrunt
- `/cicd/stacks/dev/frontend/terragrunt.hcl` - Configuración desarrollo
- `/cicd/stacks/prd/frontend/terragrunt.hcl` - Configuración producción
- `/cicd/stacks/common.yaml` - Variables compartidas
- `/cicd/modules/frontend/` - Módulo Terraform reutilizable

## 🛠️ Variables de Entorno en Terragrunt

Las variables de Firebase se obtienen automáticamente de Google Secret Manager usando `run_cmd`:

```hcl
# Ejemplo en terragrunt.hcl
inputs = {
  firebase_api_key = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=firebase-api-key", "--project=${local.project_id}")
  firebase_auth_domain = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=firebase-auth-domain", "--project=${local.project_id}")
  # ... más variables
}
```

## 🎯 Entornos de Deployment

### Desarrollo (dev)
- **URL**: Generada automáticamente por Cloud Run
- **Proyecto**: `agro-extension-digital-npe`
- **Servicio**: `frontend-app-dev`
- **Región**: `us-central1`
- **Min Scale**: 0 (scale-to-zero)
- **Max Scale**: 10

### Producción (prd)  
- **URL**: Generada automáticamente por Cloud Run
- **Proyecto**: `agro-extension-digital-npe`
- **Servicio**: `frontend-app-prd`
- **Región**: `us-central1`
- **Min Scale**: 1 (siempre activo)
- **Max Scale**: 100

## 🚨 Troubleshooting Rápido

### Error: "Permission denied on secret"
```bash
# Verificar permisos
gcloud projects get-iam-policy agro-extension-digital-npe

# Agregar permisos faltantes
gcloud projects add-iam-policy-binding agro-extension-digital-npe \
    --member="user:$(gcloud config get-value account)" \
    --role="roles/secretmanager.secretAccessor"
```

### Error: "Secret not found"
```bash
# Ejecutar configuración de secretos
./scripts/setup-secrets.sh
```

### Error: "gcloud not authenticated"
```bash
# Autenticarse
gcloud auth login
gcloud auth application-default login
```

### Error: "Terragrunt command not found"
```bash
# Instalar Terragrunt (Linux/Mac)
curl -LO https://github.com/gruntwork-io/terragrunt/releases/latest/download/terragrunt_linux_amd64
chmod +x terragrunt_linux_amd64
sudo mv terragrunt_linux_amd64 /usr/local/bin/terragrunt
```

## 📊 Post-Deployment

### Verificar el Deployment
```bash
# Ver logs del servicio
gcloud run services logs read frontend-app-dev --region=us-central1

# Describir el servicio
gcloud run services describe frontend-app-dev --region=us-central1

# Obtener URL del servicio
gcloud run services describe frontend-app-dev \
    --region=us-central1 \
    --format="value(status.url)"
```

### Monitoreo
- **Cloud Console**: https://console.cloud.google.com/run
- **Logs**: https://console.cloud.google.com/logs
- **Monitoring**: https://console.cloud.google.com/monitoring

## 🔄 Workflow Recomendado

1. **Primera vez**:
   ```bash
   ./scripts/setup-secrets.sh      # Configurar secretos
   ./scripts/validate-secrets.sh   # Validar configuración
   ./scripts/deploy-frontend.sh dev # Deploy a desarrollo
   ```

2. **Deployments posteriores**:
   ```bash
   ./scripts/validate-secrets.sh   # Verificar prerrequisitos
   ./scripts/deploy-frontend.sh dev # Deploy rápido
   ```

3. **Deploy a producción**:
   ```bash
   ./scripts/validate-secrets.sh     # Verificar prerrequisitos
   ./scripts/deploy-frontend.sh prd  # Deploy a producción
   ```

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisar logs de deployment
2. Consultar documentación detallada en `/docs/frontend/`
3. Verificar configuración de Terragrunt en `/cicd/stacks/`
4. Validar permisos IAM y secretos
