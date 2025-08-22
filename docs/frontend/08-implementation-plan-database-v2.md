# 🎯 Plan de Implementación - Esquema de Base de Datos Actualizado

**Proyecto**: agro-extension-digital-npe  
**Versión**: 2.0 - Optimizada para AuthN/AuthZ  
**Fecha**: 2025-08-19  
**Estado**: ✅ Listo para implementar

## 📋 Resumen de Cambios

### 🆕 Nuevas Colecciones
1. **`users`** - Sistema centralizado de autenticación y roles
2. **`audits`** - Gestión completa del proceso de auditorías

### 🔄 Colecciones Actualizadas
1. **`business_profiles`** - Vinculada con users, campos normalizados
2. **`auditors`** - Vinculada con users, estructura optimizada
3. **`registers`** - Estados modernizados, workflow mejorado
4. **`standards`** - Categorizados y versionados
5. **`resources`** - Control de acceso y metadatos
6. **`standard_responses`** - Optimizada para auditores

---

## 🛠️ Archivos Creados/Actualizados

### 📄 Documentación
- ✅ `/docs/frontend/07-updated-database-schema.md` - Esquema completo v2.0

### 🏗️ Infraestructura
- ✅ `/cicd/modules/database/main.tf` - Módulo actualizado con reglas de seguridad
- ✅ `/cicd/modules/database/firestore-security-rules.rules` - Reglas optimizadas
- ✅ `/cicd/modules/database/variables.tf` - Variables actualizadas

### 🔧 Scripts de Migración
- ✅ `/scripts/migrate-database-schema.sh` - Migración automatizada

---

## 🚀 Plan de Implementación

### Fase 1: Preparación (15 min)
```bash
# 1. Backup de la base de datos actual
gcloud firestore export gs://backup-bucket/$(date +%Y%m%d-%H%M%S) \
  --database=agro-extension-db

# 2. Verificar configuración de Terragrunt
cd /workspaces/agro_extension_digital_project/cicd/stacks/dev/database
terragrunt plan
```

### Fase 2: Migración de Datos (30 min)
```bash
# 1. Ejecutar migración en modo DRY_RUN
export PROJECT_ID="tu-proyecto-id"
export ENVIRONMENT="dev"
export DRY_RUN="true"

cd /workspaces/agro_extension_digital_project/scripts
./migrate-database-schema.sh

# 2. Revisar resultado y ejecutar migración real
export DRY_RUN="false"
./migrate-database-schema.sh
```

### Fase 3: Actualización de Infraestructura (20 min)
```bash
# 1. Aplicar nuevos índices y reglas de seguridad
cd /workspaces/agro_extension_digital_project/cicd/stacks/dev/database
terragrunt apply

# 2. Verificar índices
gcloud firestore indexes list --database=agro-extension-db
```

### Fase 4: Validación (15 min)
```bash
# 1. Ejecutar script de validación
cd /workspaces/agro_extension_digital_project/scripts
./validate-secrets.sh

# 2. Verificar reglas de seguridad
# Probar en Firebase Console con simulador
```

---

## 🔍 Checklist de Validación

### ✅ Pre-migración
- [ ] Backup de base de datos creado
- [ ] Variables de entorno configuradas
- [ ] Credenciales de Google Cloud verificadas
- [ ] Terragrunt configurado correctamente

### ✅ Post-migración
- [ ] Colección `users` creada y poblada
- [ ] Colección `audits` creada (vacía inicialmente)
- [ ] Todas las colecciones existentes actualizadas
- [ ] Índices de Firestore creados
- [ ] Reglas de seguridad aplicadas
- [ ] Backups automáticos configurados

### ✅ Funcionalidad
- [ ] Autenticación funciona correctamente
- [ ] Permisos por rol implementados
- [ ] Consultas optimizadas con índices
- [ ] Frontend conecta con nuevo esquema

---

## 🎨 Impacto en el Frontend

### 🔧 Cambios Requeridos en Next.js

#### 1. Hooks de Autenticación Actualizados
```typescript
// src/lib/hooks/useAuth.ts - ACTUALIZAR
export interface User {
  uid: string;
  email: string;
  displayName: string;
  role: 'admin' | 'auditor' | 'business_owner';
  isActive: boolean;
  businessProfileId?: string;
  auditorProfileId?: string;
}
```

#### 2. Servicios de Base de Datos
```typescript
// src/lib/services/firestore.ts - ACTUALIZAR
export const getUserProfile = async (uid: string) => {
  const userDoc = await db.collection('users').doc(uid).get();
  return userDoc.data() as User;
};

export const getBusinessProfile = async (businessProfileId: string) => {
  const profileDoc = await db.collection('business_profiles').doc(businessProfileId).get();
  return profileDoc.data() as BusinessProfile;
};
```

#### 3. Componentes de Autorización
```typescript
// src/components/auth/RoleGuard.tsx - ACTUALIZAR
export const RoleGuard: React.FC<RoleGuardProps> = ({ 
  allowedRoles, 
  children 
}) => {
  const { user } = useAuth();
  
  if (!user || !allowedRoles.includes(user.role)) {
    return <UnauthorizedAccess />;
  }
  
  return <>{children}</>;
};
```

---

## 🚨 Riesgos y Mitigaciones

### ⚠️ Riesgos Identificados

1. **Pérdida de Datos**
   - Mitigación: Backup automático antes de migración
   - Rollback: Restauración desde backup

2. **Inconsistencia de Datos**
   - Mitigación: Migración en modo DRY_RUN primero
   - Validación: Scripts de verificación automatizados

3. **Downtime del Sistema**
   - Mitigación: Migración en horario de baja actividad
   - Plan B: Rollback inmediato si hay problemas

4. **Conflictos de Permisos**
   - Mitigación: Testing exhaustivo de reglas de seguridad
   - Monitoreo: Logs de acceso en tiempo real

---

## 📊 Métricas de Éxito

### 🎯 KPIs Técnicos
- ✅ 100% de datos migrados sin pérdida
- ✅ Tiempo de consulta < 500ms (mejora del 60%)
- ✅ 0 errores de permisos después de 24h
- ✅ Backups automáticos funcionando

### 🎯 KPIs de Usuario
- ✅ Login funciona para todos los usuarios
- ✅ Navegación por rol sin errores
- ✅ Acceso a datos según permisos
- ✅ Performance percibida mejorada

---

## 🔄 Plan de Rollback

### En caso de problemas críticos:

```bash
# 1. Detener tráfico a la aplicación
gcloud run services update frontend-service --no-traffic

# 2. Restaurar base de datos desde backup
gsutil ls gs://backup-bucket/ | grep $(date +%Y%m%d)
gcloud firestore import gs://backup-bucket/[BACKUP_ID]

# 3. Revertir Terragrunt
cd /workspaces/agro_extension_digital_project/cicd/stacks/dev/database
git checkout HEAD~1 -- .
terragrunt apply

# 4. Restaurar tráfico
gcloud run services update frontend-service --traffic=100
```

---

## 📞 Contactos de Soporte

### 🔧 Equipo Técnico
- **DevOps**: Responsable de infraestructura y despliegue
- **Backend**: Responsable de API y base de datos
- **Frontend**: Responsable de interfaz y autenticación

### 📱 Escalación
1. **Nivel 1**: Desarrollador de turno
2. **Nivel 2**: Tech Lead
3. **Nivel 3**: Arquitecto de Soluciones

---

## 📅 Timeline Recomendado

### 🕐 Horario Sugerido
- **Inicio**: Viernes 18:00 (horario de baja actividad)
- **Duración Total**: 1.5 horas
- **Finalización**: Viernes 19:30
- **Monitoreo**: Hasta Lunes 09:00

### 📋 Agenda Detallada
```
18:00 - 18:15  Backup y preparación
18:15 - 18:45  Migración de datos
18:45 - 19:05  Actualización infraestructura
19:05 - 19:20  Validación y testing
19:20 - 19:30  Documentación y cierre
```

---

## ✅ Próximos Pasos

1. **Revisar documentación**: Validar esquema actualizado
2. **Coordinar equipo**: Agendar ventana de migración
3. **Preparar ambiente**: Configurar variables y credenciales
4. **Ejecutar migración**: Seguir plan de implementación
5. **Monitorear sistema**: Verificar funcionamiento 24h
6. **Actualizar frontend**: Implementar cambios en Next.js

---

## 📝 Notas Finales

Esta actualización del esquema representa una mejora significativa en:
- **Seguridad**: Reglas granulares por rol y recurso
- **Performance**: Índices optimizados para consultas frecuentes
- **Escalabilidad**: Estructura preparada para crecimiento
- **Mantenibilidad**: Código y datos organizados y documentados

El esquema está **listo para implementación** y alineado con los objetivos del sistema de autenticación y autorización del proyecto CiruelaCertificada.
