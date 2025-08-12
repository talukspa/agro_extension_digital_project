# Cloud Run Performance Optimizations

Este documento describe las optimizaciones de rendimiento aplicadas a los servicios de Cloud Run en este proyecto, basadas en las mejores prácticas oficiales de Google Cloud.

## Optimizaciones Implementadas

### 1. **CPU Startup Boost**

- **Variable**: `startup_cpu_boost_agent_aa`, `startup_cpu_boost_webhook`
- **Descripción**: Aumenta temporalmente la asignación de CPU durante el inicio de la instancia para reducir la latencia de inicio
- **Valor**: `true` (habilitado en todos los entornos)
- **Beneficio**: Reduce significativamente el tiempo de arranque en frío

### 2. **Instancias Mínimas**

- **Variables**: `min_instance_count_agent_aa`, `min_instance_count_webhook`
- **Descripción**: Mantiene un número mínimo de instancias en ejecución para evitar arranques en frío
- **Valores**:
  - **Desarrollo**: 1 instancia mínima para ambos servicios
  - **Producción**: 2 instancias mínimas para alta disponibilidad
- **Beneficio**: Elimina la latencia de arranque en frío para la mayoría de las solicitudes

### 3. **Configuración de Recursos Optimizada**

#### Agent AA Service

- **Memoria**:
  - Dev: 2Gi
  - Prod: 4Gi (más recursos para cargas de trabajo de producción)
- **CPU**:
  - Dev: 2 cores
  - Prod: 4 cores
- **CPU Idle**:
  - Dev: `false` (ahorro de costos)
  - Prod: `true` (mejor tiempo de respuesta)

#### Webhook Service

- **Memoria**:
  - Dev: 1Gi
  - Prod: 2Gi
- **CPU**:
  - Dev: 1 core
  - Prod: 2 cores
- **CPU Idle**:
  - Dev: `false` (ahorro de costos)
  - Prod: `true` (mejor tiempo de respuesta)

### 4. **Configuración de Concurrencia**

- **Agent AA**:
  - Dev: 50 solicitudes concurrentes por instancia
  - Prod: 80 solicitudes concurrentes por instancia
- **Webhook**:
  - Dev: 80 solicitudes concurrentes por instancia
  - Prod: 100 solicitudes concurrentes por instancia
- **Beneficio**: Optimiza el uso de recursos y el rendimiento según el tipo de servicio

### 5. **Execution Environment Gen2**

- **Variable**: `execution_environment`
- **Valor**: `EXECUTION_ENVIRONMENT_GEN2`
- **Beneficio**: Proporciona mejor rendimiento y capacidades mejoradas

### 6. **Health Checks Optimizados**

#### Startup Probes

- **Propósito**: Verificar que el contenedor ha iniciado correctamente
- **Configuración**:
  - Delay inicial: 10-15s
  - Timeout: 5-10s
  - Período: 10s
  - Umbral de falla: 3-5 intentos

#### Liveness Probes

- **Propósito**: Verificar que el contenedor sigue funcionando
- **Configuración**:
  - Delay inicial: 30-60s
  - Timeout: 5-10s
  - Período: 30-60s
  - Umbral de falla: 3-5 intentos

### 7. **Escalado Automático**

- **Máximo de instancias**:
  - Dev: 5 (Agent AA), 3 (Webhook)
  - Prod: 20 (Agent AA), 10 (Webhook)
- **Beneficio**: Permite manejar picos de tráfico mientras controla costos

### 8. **Traffic Management**

- **Configuración**: 100% del tráfico a la revisión más reciente
- **Beneficio**: Permite implementaciones simples y rollbacks rápidos

## Consideraciones por Entorno

### Desarrollo

- **Enfoque**: Equilibrio entre rendimiento y costo
- **CPU Idle**: Deshabilitado para ahorrar costos
- **Instancias mínimas**: 1 para funcionalidad básica
- **Logging**: DEBUG para debugging detallado

### Producción

- **Enfoque**: Máximo rendimiento y disponibilidad
- **CPU Idle**: Habilitado para mejor tiempo de respuesta
- **Instancias mínimas**: 2 para alta disponibilidad
- **Recursos**: Aumentados para manejar carga de producción
- **Logging**: INFO para balance entre información y rendimiento

## Monitoreo de Rendimiento

Para monitorear la efectividad de estas optimizaciones, revisa las siguientes métricas en Google Cloud Monitoring:

1. **Latencia de arranque en frío**: `run.googleapis.com/container/startup_latencies`
2. **Tiempo de respuesta**: `run.googleapis.com/request_latencies`
3. **Uso de CPU**: `run.googleapis.com/container/cpu/utilizations`
4. **Uso de memoria**: `run.googleapis.com/container/memory/utilizations`
5. **Número de instancias**: `run.googleapis.com/container/instance_count`
6. **Tiempo facturable de instancia**: `run.googleapis.com/container/billable_instance_time`

## Próximos Pasos

1. **Load Testing**: Realizar pruebas de carga para validar las configuraciones de concurrencia
2. **Fine-tuning**: Ajustar los valores basándose en métricas reales de producción
3. **Cost Optimization**: Revisar métricas de facturación para optimizar la relación costo-rendimiento
4. **Monitoring**: Implementar alertas para métricas clave de rendimiento

## Variables de Configuración

Todas las variables de optimización están documentadas en `modules/agent/variables.tf` con valores por defecto apropiados. Los valores específicos por entorno se configuran en:

- `dev/terragrunt.hcl` para desarrollo
- `prd/terragrunt.hcl` para producción

## Referencias

- [Google Cloud Run Performance Best Practices](https://cloud.google.com/run/docs/tips/general#optimize_performance)
- [Cloud Run Concurrency Guide](https://cloud.google.com/run/docs/about-concurrency)
- [Cloud Run Resource Limits](https://cloud.google.com/run/docs/configuring/memory-limits)
- [Cloud Run Health Checks](https://cloud.google.com/run/docs/configuring/healthchecks)
