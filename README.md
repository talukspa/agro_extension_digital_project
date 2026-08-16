# ¡Hola! 👋 Bienvenidos al Proyecto AgroExtensión Digital 🌱🚜

Este es el repositorio principal de nuestro proyecto `agro_extension_digital_project`.
Nuestra misión es revolucionar la extensión agrícola digital, conectando a agricultores y técnicos con información y herramientas de vanguardia. ¡Vamos a sembrar el futuro juntos! 🚀

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![Terraform](https://img.shields.io/badge/Terraform-1.5+-purple)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Platform-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🏗️ Arquitectura del Proyecto

Este es un monorepo moderno que implementa una arquitectura de microservicios para la extensión agrícola digital, utilizando las mejores prácticas de desarrollo, CI/CD e infraestructura como código.

## 📂 Estructura del Proyecto

### **`agents/`** 🤖
**Agentes Inteligentes de IA**
- **Tecnologías:** Python 3.12, Google ADK, Pydantic v2
- **Propósito:** Agentes conversacionales especializados en agricultura
- **Componentes:**
  - `agent_aa_app/`: Agente de Asistencia Agrícola
  - `agent_pp_app/`: Agente de Planificación de Producción
- **Arquitectura:** Modular con validación de datos y integración con servicios de Google Cloud

### **`webhook-application/`** 📲
**Aplicación de Webhooks de WhatsApp (Completamente Refactorizada)**
- **Tecnologías:** FastAPI, Pydantic v2, HTTPX, Google Cloud Auth
- **Arquitectura:** Modular con separación clara de responsabilidades
- **Características:**
  - ✅ Validación de datos con Pydantic v2
  - ✅ Arquitectura modular (api/, models/, utils/)
  - ✅ Logging estructurado con niveles configurables
  - ✅ Manejo robusto de errores
  - ✅ Configuración centralizada
  - ✅ Dependencias versionadas y restringidas
- **Estructura:**
  ```
  whatsapp_webhook/
  ├── api/           # Routers de FastAPI
  ├── models/        # Modelos de dominio Pydantic v2
  ├── utils/         # Utilidades y configuración
  └── app.py         # Factory de aplicación FastAPI
  ```

### **`cicd/`** ⚙️
**Infraestructura como Código (IaC)**
- **Tecnologías:** Terraform + Terragrunt
- **Ambientes:** Desarrollo (NPE) y Producción (PRD)
- **Características:**
  - 🏗️ Modules reutilizables
  - 🔧 Configuración específica por ambiente
  - 📊 Estado remoto en Google Cloud Storage
  - 🚀 Despliegue automatizado en Google Cloud Run
  - 🔒 Gestión segura de secretos

### **`actions-runner/`** 🏃‍♂️
**Self-Hosted GitHub Actions Runner**
- **Propósito:** Ejecutar CI/CD pipelines en infraestructura propia
- **Configuración:** Automatizada para integración con Google Cloud

## 🛠️ Stack Tecnológico

### **Backend & APIs**
- **Python 3.12** (versión fija para consistencia)
- **FastAPI** (framework web moderno y rápido)
- **Pydantic v2** (validación de datos y serialización)
- **Uvicorn/Gunicorn** (servidores ASGI/WSGI)

### **Infraestructura & Despliegue**
- **Google Cloud Platform** (plataforma principal)
- **Google Cloud Run** (contenedores serverless)
- **Terraform + Terragrunt** (infraestructura como código)
- **Docker** (containerización)
- **GitHub Actions** (CI/CD)

### **Desarrollo & Calidad**
- **uv** (gestor de dependencias Python ultrarrápido)
- **Dev Containers** (entornos de desarrollo consistentes)
- **Structured Logging** (logging configurable por ambiente)
- **Type Safety** (typing completo con Pydantic)

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker & VS Code con extensión Dev Containers
- Cuenta de Google Cloud con permisos apropiados
- Python 3.12 (si no usas Dev Containers)

### 1. Configuración del Entorno de Desarrollo
```bash
# Clona el repositorio
git clone https://github.com/RodrigoVasquez/agro_extension_digital_project.git
cd agro_extension_digital_project

# Abre en VS Code
code .

# VS Code detectará automáticamente el Dev Container
# Selecciona "Reopen in Container" cuando aparezca la notificación
```

### 2. Desarrollo Local

#### Webhook Application
```bash
cd webhook-application

# Instalar dependencias con uv
uv sync

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tus configuraciones

# Ejecutar en modo desarrollo
uv run python main.py
```

#### Agents
```bash
cd agents

# Instalar dependencias
uv sync

# Ejecutar agente
uv run python main.py
```

## 📋 Funcionalidades Principales

### Webhook Application
- ✅ **Procesamiento de Mensajes WhatsApp:** Recepción y respuesta automatizada
- ✅ **Validación Robusta:** Pydantic v2 para validación de datos
- ✅ **Arquitectura Modular:** Separación clara de responsabilidades
- ✅ **Logging Estructurado:** Configuración por ambiente (DEBUG/INFO)
- ✅ **Integración con Agentes:** Comunicación con servicios de IA
- ✅ **Manejo de Errores:** Recuperación graceful y logging detallado

### Intelligent Agents
- 🤖 **Asistencia Agrícola:** Consejos especializados por cultivo
- 📋 **Planificación de Producción:** Optimización de recursos
- 🔗 **Integración Google Cloud:** Aprovecha servicios de IA/ML
- 📊 **Analytics:** Procesamiento de datos agrícolas

### Infrastructure
- 🏗️ **Multi-ambiente:** Desarrollo y producción separados
- 🔄 **CI/CD Automatizado:** Despliegue continuo con GitHub Actions
- 📦 **Containerización:** Docker para todas las aplicaciones
- 🔒 **Seguridad:** Gestión apropiada de secretos y permisos

## 👥 Guía de Contribución y Desarrollo

### Estándares de Código
- **Python:** Sigue PEP 8 y usa type hints
- **Pydantic v2:** Para toda validación de datos
- **Logging:** Usa el sistema estructurado configurado
- **Testing:** Escribe tests para nuevas funcionalidades
- **Documentation:** Documenta funciones y clases importantes

### Flujo de Trabajo Git
```bash
# Crear rama para nueva feature
git checkout -b feature/nueva-funcionalidad

# Hacer commits descriptivos
git commit -m "feat: agregar validación de mensajes WhatsApp"

# Push y crear Pull Request
git push origin feature/nueva-funcionalidad
```

### Estructura de Commits
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bugs
- `docs:` Actualización de documentación
- `refactor:` Refactorización de código
- `test:` Agregado o modificación de tests
- `ci:` Cambios en CI/CD

### Testing
```bash
# Webhook Application
cd webhook-application
uv run pytest tests/

# Agents
cd agents
uv run pytest tests/
```

## 🐳 Entorno de Desarrollo con Dev Containers

Este proyecto está completamente configurado para usar **Dev Containers** en VS Code, proporcionando un entorno de desarrollo consistente, aislado y reproducible para todos los colaboradores.

### ¿Por qué Dev Containers? 🤔

- **Consistencia:** Mismo entorno para todos los desarrolladores
- **Aislamiento:** No interfiere con tu configuración local
- **Rapidez:** Configuración automática sin instalaciones manuales
- **Productividad:** Extensiones y herramientas preconfiguradas

### Características del Dev Container 🧰

**Base:** Ubuntu 22.04.5 LTS

**Herramientas Incluidas:**
- 🌲 **Git:** Última versión con configuración optimizada
- 🐳 **Docker CLI:** Para gestionar contenedores desde el contenedor
- 🏗️ **Terraform + Terragrunt:** Completo stack de IaC
- 🐍 **Python 3.12:** Con uv para gestión de dependencias
- ☁️ **Google Cloud CLI:** Para interactuar con GCP
- 🛠️ **Herramientas Linux:** curl, wget, jq, tree, htop, etc.

**Extensiones VS Code Preinstaladas:**
- Python y Pylance
- Terraform
- Docker
- GitLens
- Thunder Client (para testing de APIs)

### Configuración Rápida ✨

1. **Prerrequisitos:**
   - VS Code instalado
   - Docker Desktop ejecutándose
   - Extensión "Dev Containers" (`ms-vscode-remote.remote-containers`)

2. **Abrir el Proyecto:**
   ```bash
   git clone https://github.com/RodrigoVasquez/agro_extension_digital_project.git
   cd agro_extension_digital_project
   code .
   ```

3. **Iniciar Dev Container:**
   - VS Code detectará automáticamente la configuración
   - Click en "Reopen in Container" cuando aparezca la notificación
   - O usa `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

4. **Primera Construcción:**
   - La primera vez tardará unos minutos en construir la imagen
   - Construcciones posteriores serán mucho más rápidas (caché)

### Comandos Útiles en el Dev Container 🚀

```bash
# Verificar herramientas instaladas
python --version    # Python 3.12.x
terraform --version # Terraform v1.x.x
gcloud --version    # Google Cloud SDK

# Gestión de dependencias con uv
uv --version        # uv 0.x.x

# Verificar Docker
docker --version    # Docker version 24.x.x
```

### Tips de Productividad 💡

- **Terminal Integrado:** Ya configurado con las herramientas necesarias
- **Variables de Entorno:** Configuradas automáticamente para desarrollo
- **Port Forwarding:** Automático para aplicaciones web (8000, 3000, etc.)
- **Git Credentials:** Se mantienen desde tu sistema host

## ⚙️ Guía Completa de Despliegue y Operaciones

### Configuración y Ejecución del Self-Hosted Runner de GitHub Actions 🏃💨

Para que nuestras automatizaciones (GitHub Actions) funcionen en nuestra propia infraestructura (self-hosted), necesitas configurar y luego ejecutar un runner.

#### 1. Configuración Inicial del Runner (Solo la primera vez o si necesitas reconfigurar)

Si es la primera vez que configuras un runner en esta máquina o necesitas registrar uno nuevo:

a.  **Ve a la configuración de Actions en tu repositorio de GitHub:**
    *   Navega a tu repositorio en GitHub: [https://github.com/RodrigoVasquez/agro_extension_digital_project](https://github.com/RodrigoVasquez/agro_extension_digital_project)
    *   Haz clic en `Settings` (Configuración) > `Actions` (Acciones) en el menú lateral izquierdo > `Runners`.
    *   Haz clic en el botón `New self-hosted runner` (Nuevo runner auto-hospedado).
b.  **Sigue las instrucciones de GitHub para descargar y configurar:**
    *   GitHub te proporcionará comandos para descargar el software del runner y luego para configurarlo. El comando de configuración se verá algo así (¡asegúrate de usar el token que te proporcione GitHub!):
        ```bash
        ./config.sh --url https://github.com/RodrigoVasquez/agro_extension_digital_project --token TU_TOKEN_DE_RUNNER_PROPORCIONADO_POR_GITHUB
        ```
    *   Asegúrate de ejecutar este comando dentro del directorio `actions-runner/` de este proyecto. Si el directorio no existe, los comandos de GitHub te guiarán para crearlo y descargar el software del runner.
    *   Puedes asignar etiquetas (labels) al runner durante la configuración si es necesario (por ejemplo, `self-hosted,linux,x64`).

#### 2. Ejecución del Runner (Una vez configurado)

Después de que el runner esté configurado, sigue estos pasos para ejecutarlo:

a.  **Autentícate en Google Cloud (si tus actions interactúan con GCP):**
    ```bash
    gcloud auth login
    ```
b.  **Configura tu proyecto en gcloud (ejemplo para no-producción):**
    ```bash
    gcloud config set project agro-extension-digital-npe
    ```
c.  **Autenticación para aplicaciones por defecto de Google Cloud:**
    ```bash
    gcloud auth application-default login
    ```
d.  **¡Lanza el runner!**
    Asegúrate de estar en el directorio `actions-runner/` donde configuraste y donde reside el script `run.sh`.
    ```bash
    cd actions-runner
    nohup ./run.sh &
    cd .. 
    ```
    El comando `nohup` permite que el runner siga ejecutándose en segundo plano incluso si cierras la terminal, y `&` lo envía al background. La salida se guardará en un archivo `nohup.out` dentro del directorio `actions-runner/`.

**Nota:** Si el runner ya está configurado y solo necesitas iniciarlo, puedes saltar directamente a la sección "2. Ejecución del Runner".

### Creación de Buckets en GCS para el Estado de Terraform 🪣☁️

Terraform necesita un lugar seguro para guardar el "estado" de nuestra infraestructura. Usamos Google Cloud Storage (GCS) para esto.

**Consideraciones Clave Antes de Empezar:** ⚠️

*   **Nombres de Bucket Únicos Globalmente:** Los nombres de los buckets en GCS deben ser únicos en todo el universo de Google Cloud. Si los nombres que te damos ya están pillados, tendrás que inventar unos nuevos (puedes añadir un sufijo único, ¡sé creativo!).
*   **Permisos Necesarios:** La cuenta de Google Cloud que uses debe tener los permisos de IAM adecuados (como `roles/storage.admin`) en los proyectos donde vayas a crear los buckets.
*   **`gcloud` CLI Instalado:** Debes tener la herramienta de línea de comandos de Google Cloud (`gcloud`) instalada y autenticada.

#### Bucket 1: Para el Proyecto `agro-extension-digital-npe` (Ambiente de No-Producción) 🧪

*   **Nombre del Bucket Objetivo:** `agro-extension-digital-npe-tf-state-bucket`
*   **ID del Proyecto Objetivo:** `agro-extension-digital-npe`
*   **Ubicación Objetivo:** `us-central1`

**Comandos:**

```bash
# OPCIONAL: Configura tu gcloud para el proyecto NPE.
# Esto te ahorra tener que escribir --project en los siguientes comandos para esta sección.
# gcloud config set project agro-extension-digital-npe

# 1. Crear el bucket GCS para el proyecto NPE
echo "Intentando crear el bucket 'agro-extension-digital-npe-tf-state-bucket' en el proyecto 'agro-extension-digital-npe'..."
gcloud storage buckets create gs://agro-extension-digital-npe-tf-state-bucket \
  --project=agro-extension-digital-npe \
  --location=us-central1 \
  --uniform-bucket-level-access

# 2. Habilitar el versionado en el bucket NPE
# ¡El versionado es súper recomendado para el estado de Terraform, así puedes recuperar estados anteriores!
echo "Habilitando versionado para el bucket 'agro-extension-digital-npe-tf-state-bucket'..."
gcloud storage buckets update gs://agro-extension-digital-npe-tf-state-bucket \
  --project=agro-extension-digital-npe \
  --versioning

echo "Proceso de creación y configuración de versionado del bucket 'agro-extension-digital-npe-tf-state-bucket' iniciado para el proyecto 'agro-extension-digital-npe'."
```

#### Bucket 2: Para el Proyecto `agro-extension-digital-prd` (Ambiente de Producción) ✨

*   **Nombre del Bucket Objetivo:** `agro-extension-digital-prd-tf-state-bucket`
*   **ID del Proyecto Objetivo:** `agro-extension-digital-prd`
*   **Ubicación Objetivo:** `us-central1` (la mantenemos igual que NPE por simplicidad)

**Comandos:**

```bash
# OPCIONAL: Configura tu gcloud para el proyecto PRD.
# gcloud config set project agro-extension-digital-prd

# 1. Crear el bucket GCS para el proyecto PRD
echo "Intentando crear el bucket 'agro-extension-digital-prd-tf-state-bucket' en el proyecto 'agro-extension-digital-prd'..."
gcloud storage buckets create gs://agro-extension-digital-prd-tf-state-bucket \
  --project=agro-extension-digital-prd \
  --location=us-central1 \
  --uniform-bucket-level-access

# 2. Habilitar el versionado en el bucket PRD
echo "Habilitando versionado para el bucket 'agro-extension-digital-prd-tf-state-bucket'..."
gcloud storage buckets update gs://agro-extension-digital-prd-tf-state-bucket \
  --project=agro-extension-digital-prd \
  --versioning

echo "Proceso de creación y configuración de versionado del bucket 'agro-extension-digital-prd-tf-state-bucket' iniciado para el proyecto 'agro-extension-digital-prd'."
```

Después de crear estos buckets, ¡no olvides configurar tu backend de Terraform en tus archivos `.tf` para que apunten al bucket correcto para cada ambiente! 😉

### Despliegue de Infraestructura con Terragrunt 🌍🔧

Terragrunt es una herramienta que nos ayuda a mantener nuestra configuración de Terraform DRY (Don't Repeat Yourself), organizada y más fácil de manejar, especialmente cuando tenemos múltiples entornos.

**Prerrequisitos:**

1.  **Terragrunt Instalado:** Asegúrate de tener [Terragrunt instalado](https://terragrunt.gruntwork.io/docs/getting-started/install/) en tu máquina.
2.  **Autenticación con Google Cloud:** Debes estar autenticado con `gcloud` y tener los permisos necesarios para desplegar recursos en los proyectos de GCP correspondientes.
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
3.  **Buckets de State Creados:** Asegúrate de haber creado los buckets de GCS para el estado de Terraform como se describe en la sección anterior.

**Pasos para el Despliegue:**

Los comandos de Terragrunt generalmente se ejecutan desde el directorio del entorno específico que quieres gestionar (por ejemplo, `cicd/dev` o `cicd/prd`) o desde un directorio raíz si tienes un `terragrunt.hcl` que los englobe.

1.  **Navega al Directorio del Entorno:**
    *   Para el ambiente de No-Producción (NPE/dev):
        ```bash
        cd cicd/dev
        ```
    *   Para el ambiente de Producción (PRD):
        ```bash
        cd cicd/prd
        ```

2.  **Inicializa Terragrunt (y Terraform):**
    Este comando descarga los providers de Terraform y configura el backend.
    ```bash
    terragrunt init
    ```
    O si quieres inicializar todos los módulos recursivamente (si tienes una estructura con `run-all`):
    ```bash
    terragrunt run-all init
    ```

3.  **Planifica los Cambios:**
    Revisa los cambios que Terragrunt aplicará a tu infraestructura.
    ```bash
    terragrunt plan
    ```
    O para todos los módulos:
    ```bash
    terragrunt run-all plan
    ```

4.  **Aplica los Cambios:**
    Este comando provisionará o modificará tu infraestructura según la configuración.
    ```bash
    terragrunt apply
    ```
    O para todos los módulos (¡usa con precaución, especialmente en producción!):
    ```bash
    terragrunt run-all apply
    ```
    Terragrunt te pedirá confirmación antes de aplicar los cambios.

**Ejemplo de Despliegue Completo para un Entorno (ej. dev):**

```bash
# 1. Asegúrate de estar autenticado en GCP
gcloud auth login
gcloud auth application-default login

# 2. Configura el proyecto de gcloud para el entorno (opcional, pero buena práctica)
gcloud config set project agro-extension-digital-npe # O el ID de tu proyecto dev

# 3. Navega al directorio del entorno
cd cicd/dev

# 4. Inicializa
terragrunt run-all init # O terragrunt init si no usas run-all

# 5. Planifica
terragrunt run-all plan # O terragrunt plan

# 6. Aplica (revisa el plan cuidadosamente antes de este paso)
terragrunt run-all apply # O terragrunt apply
```

**Destruir la Infraestructura (¡CON MUCHO CUIDADO!)** 💣

Si necesitas eliminar la infraestructura gestionada por Terragrunt en un entorno:

```bash
# Navega al directorio del entorno correspondiente (ej. cicd/dev)
cd cicd/dev 
terragrunt run-all destroy # O terragrunt destroy
```
**Siempre revisa el plan de destrucción cuidadosamente antes de confirmar.**

¡Y eso es todo! Con estos pasos deberías poder desplegar tu infraestructura usando Terragrunt. 🚀

## 📊 Monitoreo y Observabilidad

### Logging
- **Niveles por Ambiente:**
  - Development: `DEBUG` (logs detallados)
  - Production: `INFO` (logs esenciales)
- **Formato:** JSON estructurado para agregación
- **Destino:** Google Cloud Logging

### Métricas Clave
- **Webhook Application:**
  - Mensajes procesados por minuto
  - Tiempo de respuesta promedio
  - Errores de validación
  - Integraciones con agentes exitosas

- **Agents:**
  - Consultas procesadas
  - Tiempo de respuesta de IA
  - Accuracy de respuestas

### Health Checks
```bash
# Webhook Application
curl http://localhost:8000/health

# Response: {"status": "healthy", "timestamp": "2025-07-30T..."}
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error de Autenticación con Google Cloud
```bash
# Reautenticar
gcloud auth login
gcloud auth application-default login

# Verificar proyecto activo
gcloud config get-value project
```

#### 2. Problemas con Dependencies
```bash
# Limpiar cache de uv
uv cache clean

# Reinstalar dependencias
rm uv.lock
uv sync
```

#### 3. Webhook No Recibe Mensajes
- Verificar que la URL del webhook esté correctamente configurada en WhatsApp
- Revisar logs para errores de validación
- Confirmar que los tokens de verificación coincidan

#### 4. Terraform State Lock
```bash
# Si el estado está bloqueado
cd cicd/dev
terragrunt force-unlock LOCK_ID
```

### Logs de Debug
```bash
# Ver logs de aplicación
cd webhook-application
uv run python main.py --log-level DEBUG

# Ver logs del runner
tail -f actions-runner/nohup.out

# Logs de Terraform
cd cicd/dev
terragrunt apply -var="log_level=DEBUG"
```

## 📚 API Documentation

### Webhook Endpoints

#### Verificación de Webhook
```http
GET /webhook/aa
GET /webhook/pp

Query Parameters:
- hub.mode=subscribe
- hub.challenge=<challenge_token>
- hub.verify_token=<verify_token>
```

#### Recepción de Mensajes
```http
POST /webhook/aa
POST /webhook/pp

Content-Type: application/json

Body: WhatsApp webhook payload
```

#### Health Check
```http
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2025-07-30T12:00:00Z",
  "version": "0.1.0"
}
```

### Modelos de Datos (Pydantic v2)

#### WhatsAppWebhookPayload
```python
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "string",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "messages": [
              {
                "from": "phone_number",
                "text": {"body": "message_content"},
                "type": "text"
              }
            ]
          }
        }
      ]
    }
  ]
}
```

## 🤝 Contribuir al Proyecto

### Reportar Issues
1. Usar templates de GitHub Issues
2. Incluir logs relevantes
3. Describir pasos para reproducir
4. Especificar ambiente (dev/prod)

### Pull Requests
1. Fork del repositorio
2. Crear rama descriptiva
3. Escribir tests para cambios
4. Seguir convenciones de commits
5. Actualizar documentación si es necesario

### Code Review
- Al menos una aprobación requerida
- Tests deben pasar
- Coverage mínimo del 80%
- Documentación actualizada

## 📞 Soporte

### Contacto del Equipo
- **Tech Lead:** @RodrigoVasquez
- **DevOps:** GitHub Issues
- **Documentación:** Wiki del proyecto

### Recursos Adicionales
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 Guide](https://docs.pydantic.dev/latest/)
- [Terragrunt Documentation](https://terragrunt.gruntwork.io/)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)

---

📝 **Última actualización:** Julio 2025  
🚀 **Versión:** 2.0.0  
👥 **Colaboradores:** Ver [Contributors](https://github.com/RodrigoVasquez/agro_extension_digital_project/graphs/contributors)