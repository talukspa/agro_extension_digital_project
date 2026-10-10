# Caso de uso integral — Agente de WhatsApp "Agente PP"

### El copiloto de certificación que acompaña al productor de extremo a extremo

**Plataforma Ciruela Certificada** · Estándar de Sustentabilidad para la Industria de Ciruelas Deshidratadas
Documento técnico-funcional · Basado en la demo interactiva v3 · Junio 2026

---

## 1. Resumen ejecutivo

El **Agente PP** es un asistente virtual en **WhatsApp** que actúa como **copiloto de certificación**: acompaña al productor desde que se registra en la plataforma **Ciruela Certificada** hasta que mejora su nivel de certificación, conversando en lenguaje natural desde el celular que ya usa a diario.

A diferencia de un chatbot de preguntas frecuentes, el Agente PP **conoce el contexto completo del productor**: la información que cargó en la plataforma, su autodiagnóstico, su Plan de Implementación y su estado de cumplimiento, además del estándar oficial y todo el material de capacitación. Sobre esa base, el agente **resuelve dudas, recomienda, recibe evidencia, notifica y celebra avances**, y todo lo que ocurre en la conversación queda sincronizado con el expediente digital.

El recorrido completo tiene cuatro fases: **(0)** el productor se registra e indica su WhatsApp; **(1)** completa su autodiagnóstico del estándar; **(2)** la plataforma genera su Plan de Implementación y, al entregarlo, le activa el contacto del Agente PP; **(3)** comienza el acompañamiento continuo, donde el agente opera de forma **bidireccional y proactiva**: responde dudas técnicas y de proceso, recomienda capacitación, informa el estado del plan, pide y sube evidencia a la plataforma, **registra las labores que el productor le dicta por mensaje o audio**, entrega notificaciones del auditor y avisa cuando un nuevo avance **cambia el nivel de certificación** (por ejemplo, "con tu puntaje ahora puedes certificar a 2 años").

Una pieza clave de ese acompañamiento es el **registro continuo de labores por mensaje o audio**: para las acciones que exigen una actualización permanente de labores (cuaderno de campo, aplicaciones fitosanitarias, riego, consumos), el productor solo describe en lenguaje natural lo que hizo — *"acabo de aplicar 3 litros de Cuproforte en el cuartel 2"* — y el agente lo estructura, lo guarda en la plataforma y lo usa para alimentar las acciones que necesitan ese dato.

**Valor central:** convertir una conversación cotidiana de WhatsApp en el motor que mantiene vivo el proceso de certificación — sin que el productor tenga que aprender una interfaz web, recordar plazos ni rastrear a qué criterio corresponde cada documento.

---

## 2. Contexto del producto

**Ciruela Certificada** es la plataforma de gestión de certificación del ecosistema de la ciruela deshidratada chilena (Chileprunes / CHOC, con apoyo de FIA, ODEPA, IICA y ASCC). Implementa el **Estándar de Sustentabilidad para la Industria de Ciruelas Deshidratadas**, con dos fases / estándares: **Producción Primaria** (140 preguntas) y **Adecuación Agroindustrial** (130 preguntas).

Conceptos del dominio que el agente maneja:

- **Instalaciones:** una empresa puede tener varias (p. ej. Agrícola San Vicente S.A.: Fundo Romeral, Planta Curicó, Fundo Los Maitenes), cada una con su propio proceso.
- **Niveles de acción:** *Fundamental* y *Básico*.
- **Dimensiones y temáticas:** Ambiente (Agua, Energía, Residuos), Calidad (Gestión de la Calidad, Inocuidad), Gestión, Social.
- **Niveles de certificación por puntaje:** *Certifica a 1 año*, *a 2 años* y *a 3 años*, según el porcentaje de cumplimiento de fundamentales y básicos. La proyección es **referencial y no vinculante**: la certificación final la otorga la entidad certificadora.

> **Dos canales, un mismo expediente.** En la plataforma conviven el chat humano *empresa ↔ auditor* (asíncrono) y el **Agente PP** por WhatsApp (automático, 24/7, que además opera sobre la plataforma). Este documento describe el canal del Agente PP.

---

## 3. Mapa del recorrido (end-to-end)

| Fase                           | Qué hace el productor                                                                           | Rol del Agente PP                                                                                         |
| ------------------------------ | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **0. Registro y onboarding**   | Crea su cuenta y completa sus datos, incluyendo su **número de WhatsApp** (con consentimiento). | Aún inactivo; queda asociado al número del productor.                                                     |
| **1. Autodiagnóstico**         | Responde el cuestionario del estándar (130/140 preguntas; guardado automático).                 | Disponible como ayuda contextual ("Tengo una duda") en cada pregunta.                                     |
| **2. Plan de Implementación**  | La plataforma genera su plan con las acciones necesarias y su proyección de certificación.      | **Se activa:** al entregar el plan, la plataforma le da el contacto del Agente PP y abre la conversación. |
| **3. Acompañamiento continuo** | Ejecuta acciones, sube evidencia, interactúa con el auditor, mejora su puntaje.                 | **Copiloto proactivo:** resuelve dudas, recomienda, sube evidencia, notifica y avisa cambios de nivel.    |

---

## 4. Ficha de caso de uso (formato estructurado / UML)

| Campo                   | Detalle                                                                                                                                                       |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID**                  | CU-WA-INT (caso integral)                                                                                                                                     |
| **Nombre**              | Acompañamiento de certificación de extremo a extremo mediante el Agente PP (WhatsApp)                                                                         |
| **Actor primario**      | Productor / Empresa (Mauricio Hernández — Agrícola San Vicente S.A., Planta Curicó)                                                                           |
| **Actores secundarios** | Agente PP; Plataforma Ciruela Certificada; Auditor (Carla V.); Entidad certificadora                                                                          |
| **Objetivo**            | Que el productor avance y mejore su certificación con acompañamiento conversacional continuo, manteniendo su expediente actualizado sin usar la interfaz web. |
| **Alcance**             | WhatsApp Business + plataforma web (lectura y escritura del expediente, notificaciones).                                                                      |
| **Nivel**               | Resumen / objetivo de negocio (agrupa varios sub-casos de uso).                                                                                               |
| **Disparador**          | La plataforma entrega el Plan de Implementación y activa el contacto del Agente PP.                                                                           |
| **Frecuencia**          | Continua durante toda la temporada de certificación.                                                                                                          |

### Precondiciones

1. El productor está registrado en Ciruela Certificada y **autorizó su número de WhatsApp** para el canal.
2. Completó (o avanza) su autodiagnóstico, lo que generó su **Plan de Implementación** con acciones, plazos y proyección de nivel.
3. El Agente PP tiene acceso de contexto a: datos cargados por el productor, estándar vigente, material de capacitación y estado del plan.

### Postcondiciones (éxito)

1. El expediente del productor refleja las evidencias, respuestas y avances gestionados por WhatsApp.
2. El productor está informado de su estado de cumplimiento, plazos y notificaciones del auditor.
3. Cuando corresponde, su **nivel de certificación proyectado mejora** y queda registrado (p. ej. de 1 a 2 años).

### Flujo principal (camino feliz, end-to-end)

1. **Activación:** entregado el Plan de Implementación, el Agente PP saluda al productor por WhatsApp, se presenta y resume su estado actual (nivel proyectado y avance).
2. **Estado:** a petición (o de forma proactiva), informa el estado de cumplimiento y qué acciones mueven más la aguja para subir de nivel.
3. **Duda técnica:** resuelve una consulta sobre un criterio del estándar, citando la pregunta correspondiente.
4. **Capacitación:** recomienda el material adecuado para esa acción (guía, curso, plantilla, estándar).
5. **Evidencia:** solicita una foto o archivo; el productor la envía y el agente la **sube a la plataforma** vinculada a la acción correcta.
6. **Registro de labores:** el productor describe una labor por mensaje o audio; el agente la estructura, confirma y la **guarda como bitácora**, alimentando las acciones que la requieren.
7. **Hito:** al completarse la acción, recalcula el cumplimiento y **avisa el cambio de nivel** de certificación.
8. **Proceso:** explica los siguientes pasos hacia la certificación oficial.
9. **Notificaciones:** entrega avisos de la plataforma (mensaje del auditor, visita agendada) y ofrece ayuda para prepararlos.

### Flujos alternativos y de excepción

- **0a. Sin consentimiento de WhatsApp:** el canal no se activa; el agente solo opera si el productor autoriza su número.
- **5a. Evidencia que no cumple:** el agente explica qué falta y solicita una nueva; no sube nada hasta que cumpla.
- **5b. Falla la carga:** informa el error, conserva el archivo y reintenta / deja la subida pendiente.
- **6b. Registro de labor incompleto o ambiguo:** el agente pregunta el dato faltante (cuartel, producto o dosis) y solo guarda tras la confirmación del productor; nunca registra datos a medias.
- **3a. Consulta fuera del estándar o ambigua:** pide aclaración o deriva al canal humano (auditor) si excede su alcance.
- **6a. El avance no cambia el nivel:** informa cuánto falta para el siguiente nivel en lugar de un cambio de estado.

### Reglas de negocio

- **RN-1:** Toda evidencia enviada por WhatsApp se vincula a una acción/criterio específico; nunca se almacena suelta.
- **RN-2:** El agente **informa y pre-valida, pero no certifica**. La certificación final la otorga la entidad certificadora; toda proyección es referencial y no vinculante.
- **RN-3:** El agente solo accede a los datos del productor que escribe y opera dentro de su(s) instalación(es).
- **RN-4:** Toda acción del agente sobre el expediente queda trazada como **"Vía Agente WhatsApp"** con marca de tiempo.
- **RN-5:** Las notificaciones push respetan el consentimiento del productor y son reflejo de eventos reales de la plataforma.

### Requisitos no funcionales

- **Disponibilidad:** 24/7. **Lenguaje:** natural (español), tono cercano.
- **Contexto:** el agente mantiene el estado del productor y la conversación a lo largo del tiempo.
- **Bidireccionalidad:** lee y escribe en la plataforma; recibe eventos y emite notificaciones.
- **Trazabilidad y privacidad:** todo queda registrado; el tratamiento de imágenes/datos por WhatsApp requiere consentimiento.

---

## 5. Narrativa paso a paso (conversación demostrativa)

Escenario: Mauricio, responsable de **Planta Curicó** (Adecuación Agroindustrial). Hoy proyecta **Certifica a 1 año** (Fundamentales 72%, Básicos 62%, 8/24 acciones).

**Activación del canal (al entregarse el Plan de Implementación)**

> **Agente PP:** "Hola Mauricio. Soy el Agente PP, tu copiloto de certificación. Ya tengo tu Plan de Implementación de Planta Curicó (Adecuación Agroindustrial). Hoy proyectas *Certifica a 1 año*, con 8 de 24 acciones completadas. ¿Quieres que te muestre qué te falta para subir a 2 años?"

**Estado del plan y del cumplimiento** *(capacidad: estado)*

> **Mauricio:** "Sí, ¿cómo voy?"
> 
> **Agente PP:** "Vas bien. Fundamentales 72% · Básicos 62%. Tu dimensión más baja es *Social* (42%). Las 3 acciones que más suman ahora son: **A001 – Registro mensual de consumo de agua** (vence hoy, 15 jun), *Sistematizar registro energético* (10 jul) y *Capacitar al personal en gestión hídrica* (30 jun). Si cierras A001, tus Fundamentales pasan el umbral de 2 años."

**Duda técnica sobre el estándar** *(capacidad: estándar)*

> **Mauricio:** "Justo tengo dudas con la del agua. ¿Registro el canal y el pozo por separado?"
> 
> **Agente PP:** "**Sí, cada fuente por separado.** La pregunta A001 (Ambiente · Agua) pide registrar mensualmente el consumo distinguiendo canal de riego, pozo profundo y agua potable, con el consumo por fuente en m³ y el tipo de uso."

**Recomendación de material de capacitación** *(capacidad: capacitación)*

> **Mauricio:** "¿Hay algo que me ayude a armarlo?"
> 
> **Agente PP:** "Sí, para esta acción te recomiendo: la **Plantilla de registro de consumo de agua** (Excel, lista para usar), la **Guía para el uso sustentable del agua** (PDF) y, si quieres profundizar, el **Curso de Gestión sustentable del agua** (Chileagrícola, 4 h, con certificado). ¿Te paso la plantilla?"

**Carga de evidencia desde WhatsApp** *(capacidad: subir foto/archivo)*

> **Agente PP:** "Cuando tengas tu registro listo, mándame una foto o el Excel por aquí y lo subo a la acción A001."
> 
> **Mauricio:** *(envía foto)* "Aquí va el registro de marzo."
> 
> *(IMG_2026_03_15.jpg — Canal Romeral 1.250 m³, Pozo profundo 340 m³, Agua potable 85 m³)*
> 
> **Agente PP:** "¡Perfecto! ✅ Tu registro cumple. Lo subí a la plataforma como evidencia de **A001 — Registro mensual de consumo de agua**. Queda *pendiente de verificación* del auditor."

**Registro de labores por mensaje o audio** *(capacidad: bitácora de labores — nueva funcionalidad)*

> **Mauricio:** *(envía un audio de 0:08)* "Acabo de hacer una aplicación de 3 litros de Cuproforte en el cuartel 2."
> 
> **Agente PP:** "Anoté tu labor a partir del audio:
> • **Labor:** Aplicación fitosanitaria
> • **Producto:** Cuproforte · **Dosis:** 3 L
> • **Ubicación:** Cuartel 2 · **Fecha:** hoy 15 jun
> ¿Lo registro en tu cuaderno de campo? (*Sí* / *corregir*)"
> 
> **Mauricio:** "Sí"
> 
> **Agente PP:** "Listo ✅. Lo guardé en tu **Cuaderno de campo** y alimenté la acción *Registro de aplicaciones fitosanitarias*. Quedó trazado *Vía Agente WhatsApp*. Cada aplicación que me dictes se va sumando a ese registro."

**Hito: cambio de nivel de certificación** *(capacidad: avisar cambios de estado)*

> **Agente PP:** "📈 Buenas noticias, Mauricio: con A001 completada, tus Fundamentales suben a **78%**. Tu proyección cambió: **ahora puedes certificar a 2 años.** (Proyección referencial, no vinculante.)"

**Duda sobre el proceso de certificación** *(capacidad: proceso)*

> **Mauricio:** "¿Y qué sigue para la certificación oficial?"
> 
> **Agente PP:** "Te quedan 3 acciones fundamentales por cerrar. Cuando completes los fundamentales, la entidad certificadora agenda la auditoría oficial sobre tu expediente. Yo te aviso de cada paso y de lo que el auditor necesite."

**Notificaciones de la plataforma** *(capacidad: notificaciones)*

> **Agente PP:** "📣 Notificación de la plataforma: tu auditora **Carla V.** dejó un mensaje en la pregunta A001 y agendó una **visita a Planta Curicó el jueves 26 de junio a las 10:00**. ¿Quieres que te prepare un checklist para la visita?"

**Iniciativa del agente** *(capacidad: proactividad)*

> **Agente PP:** "Por cierto, esta semana vencen 2 acciones. ¿Te muestro cuáles y qué evidencia falta en cada una?"

---

## 6. Catálogo de capacidades (sub-casos de uso)

| ID           | Capacidad                                   | Disparador                                           | Qué hace el agente                                              | Efecto en la plataforma                                                        |
| ------------ | ------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **CU-WA-00** | Onboarding y vinculación                    | Se entrega el Plan de Implementación                 | Se presenta y resume el estado del productor                    | Asocia el canal a la cuenta/instalación                                        |
| **CU-WA-01** | Duda técnica del estándar                   | El productor pregunta por un criterio                | Responde citando la pregunta del estándar                       | — (lectura del estándar)                                                       |
| **CU-WA-02** | Duda del proceso de certificación           | Pregunta sobre pasos, plazos o auditoría             | Explica el flujo de certificación y los próximos pasos          | —                                                                              |
| **CU-WA-03** | Recomendar capacitación                     | Pide ayuda o detecta una brecha                      | Sugiere guía / curso / plantilla / estándar pertinente          | Enlaza recursos del criterio                                                   |
| **CU-WA-04** | Estado del plan y cumplimiento              | Pregunta "¿cómo voy?" o el agente lo ofrece          | Informa % de fundamentales/básicos, brechas y prioridades       | Lee el análisis de cumplimiento                                                |
| **CU-WA-05** | Cargar evidencia (foto/archivo)             | El productor envía una imagen o archivo              | Valida y sube la evidencia vinculada a la acción                | Crea evidencia "Vía Agente WhatsApp", deja la acción pendiente de verificación |
| **CU-WA-06** | Notificaciones de la plataforma             | Evento en la plataforma (mensaje/visita del auditor) | Notifica al productor y ofrece ayuda                            | Refleja eventos del expediente                                                 |
| **CU-WA-07** | Aviso de cambio de nivel                    | Una acción completada recalcula el puntaje           | Avisa el nuevo nivel de certificación proyectado                | Lee la proyección actualizada                                                  |
| **CU-WA-08** | **Registro de labores por mensaje o audio** | El productor describe una labor por texto o audio    | Transcribe, estructura los datos, confirma y guarda el registro | Crea un registro de bitácora y alimenta las acciones que lo requieren          |

### Detalle: registro continuo de labores por mensaje o audio (nueva funcionalidad)

Algunas acciones del estándar no se cumplen con una sola evidencia, sino que exigen una **actualización permanente de labores** a lo largo de la temporada: cuaderno de campo, registro de aplicaciones fitosanitarias, registro de riego, registro de consumos, labores culturales, etc. Mantener esos registros al día suele ser la mayor fricción para el productor.

Con esta funcionalidad, el productor **no llena planillas**: simplemente le cuenta al agente lo que hizo, por **mensaje de texto o por audio**, y el agente se encarga del resto.

**Cómo funciona, paso a paso:**

1. **Captura:** el productor envía un mensaje o un audio en lenguaje natural — *"acabo de aplicar 3 litros de Cuproforte en el cuartel 2"*.
2. **Transcripción:** si es audio, el agente lo transcribe automáticamente.
3. **Extracción estructurada:** identifica los campos del registro — *labor, producto, dosis/cantidad, ubicación (cuartel/instalación) y fecha/hora* (la fecha se completa sola).
4. **Confirmación:** el agente devuelve el registro estructurado y pide confirmación antes de guardar (clave para registros permanentes y auditables).
5. **Guardado:** lo escribe en la plataforma como un asiento de bitácora, trazado *"Vía Agente WhatsApp"*.
6. **Alimenta acciones:** ese asiento se asocia a las acciones que necesitan ese dato (p. ej. *Registro de aplicaciones fitosanitarias*), sumando al cumplimiento de forma continua. Un mismo registro puede alimentar más de una acción.

**Ejemplo de registro estructurado**

| Campo            | Valor                                                       |
| ---------------- | ----------------------------------------------------------- |
| Labor            | Aplicación fitosanitaria                                    |
| Producto         | Cuproforte                                                  |
| Dosis / cantidad | 3 L                                                         |
| Ubicación        | Cuartel 2                                                   |
| Fecha / hora     | 15 jun 2026 (automática)                                    |
| Registrado por   | M. Hernández · Vía Agente WhatsApp (audio)                  |
| Alimenta         | Cuaderno de campo · Registro de aplicaciones fitosanitarias |

Esta capacidad complementa a CU-WA-05: mientras la **carga de evidencia** sube un archivo puntual (una foto, un Excel), el **registro de labores** captura datos estructurados y recurrentes a partir de la voz o el texto del productor.

---

## 7. Lo que el agente "sabe" (base de contexto)

El poder del Agente PP está en su **contexto**. Antes de responder, el agente dispone de:

- **Datos del productor cargados en la plataforma:** empresa, instalaciones, responsables, respuestas del autodiagnóstico y evidencias.
- **Estado del Plan de Implementación:** acciones, niveles (fundamental/básico), plazos, responsables, estados y proyección de certificación.
- **El estándar oficial completo:** preguntas, dimensiones, temáticas y criterios de cumplimiento.
- **El material de capacitación:** guías, cursos y plantillas asociados a cada acción.
- **El contexto del proyecto:** el proceso Chileprunes, las fases (Producción Primaria / Adecuación Agroindustrial) y los niveles de certificación.

Esto le permite ser **específico** ("para *tu* acción A001, con *tu* avance de 72%…") en lugar de dar respuestas genéricas.

---

## 8. Arquitectura funcional

- **Capa conversacional (Agente PP):** comprensión de lenguaje natural, memoria del contexto del productor, razonamiento sobre el estándar y validación básica de evidencia.
- **Procesamiento de voz y extracción de datos:** transcribe los audios y extrae campos estructurados de los mensajes (labor, producto, dosis, ubicación, fecha) para los registros de bitácora.
- **Base de conocimiento:** estándar + material de capacitación (recuperación de la respuesta y el recurso correctos).
- **Integración bidireccional WhatsApp ↔ plataforma:**
  - *Lectura:* estado del plan, cumplimiento, recursos, respuestas del autodiagnóstico.
  - *Escritura:* carga de evidencias y **registros de labores (bitácora)** vinculados a una o varias acciones.
  - *Eventos:* recibe notificaciones de la plataforma (auditor, visitas, cambios de nivel) y las empuja al productor.
- **Trazabilidad:** todo lo que el agente escribe queda marcado como "Vía Agente WhatsApp" con fecha.
- **Identidad y privacidad:** identifica al productor por su número autorizado; opera solo dentro de su expediente.

---

## 9. Beneficios e impacto

- **Acompañamiento de extremo a extremo:** del registro al cambio de nivel, sin abandonar WhatsApp.
- **Contexto real, respuestas específicas:** el agente conoce el expediente del productor, no responde en abstracto.
- **Proactividad que evita atrasos:** avisa plazos, notificaciones del auditor y oportunidades de mejora antes de que se conviertan en problema.
- **Captura de evidencia sin fricción:** la foto o el archivo se suben solos al criterio correcto.
- **Registros al día con la voz:** dictar una labor por audio mantiene el cuaderno de campo y los registros recurrentes actualizados sin planillas, ideal para el trabajo en terreno.
- **Motivación por hitos:** celebrar el paso de 1 a 2 años convierte el cumplimiento en progreso visible.
- **Inclusión digital:** baja la barrera tecnológica para productores no familiarizados con plataformas web.
- **Aceleración del ciclo de certificación:** expediente siempre actualizado y auditor con evidencia lista para verificar.

---

## 10. Métricas sugeridas

- % de evidencias y acciones gestionadas por WhatsApp vs. interfaz web.
- Tiempo medio entre generación del medio de verificación y su carga al expediente.
- Consultas (técnicas y de proceso) resueltas por el agente sin escalamiento al auditor.
- N.º de registros de labores ingresados por mensaje/audio y % por voz vs. texto.
- Tasa de acciones que cumplen plazo tras un aviso proactivo del agente.
- N.º de productores que suben de nivel de certificación durante la temporada.
- Tasa de apertura/respuesta de las notificaciones push.

---

## 11. Supuestos y consideraciones

- Documento basado en la **demo interactiva v3** (prototipo); nombres, montos y porcentajes son ilustrativos.
- El agente **no certifica**: informa, pre-valida y acompaña; toda proyección es referencial y la certificación final la otorga la entidad certificadora.
- Requiere **consentimiento explícito** del productor para usar su WhatsApp y tratar imágenes/datos.
- La calidad de las respuestas depende de mantener actualizados el estándar, el material de capacitación y el estado del plan de cada productor.
- Conviene definir reglas de escalamiento al canal humano (auditor) para casos fuera del alcance del agente.
