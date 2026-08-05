# Agente PP en WhatsApp — Documentación de producto

Copiloto de certificación por WhatsApp para el productor de ciruela. Deja de ser un
asistente de preguntas y respuestas y pasa a **acompañar al productor de extremo a
extremo**: le dice cómo va, le resuelve dudas, le recibe evidencia y le registra sus
labores — todo por WhatsApp, con **confirmación humana antes de cada acción**.

Esta carpeta es la fuente de verdad **de producto** (el *qué* y el *para quién*). El
*cómo* técnico vive aparte, en las vistas de arquitectura.

## Mapa de documentos

| # | Documento | Para qué sirve |
|---|-----------|----------------|
| 01 | [Visión de producto](01-vision-producto.md) | Problema, promesa, métricas de éxito, principios y alcance de esta fase |
| 02 | [Personas](02-personas.md) | Para quién construimos y qué le importa |
| 03 | [Épicas](03-epicas.md) | Las grandes apuestas de valor y qué las compone |
| 04 | [Historias de usuario](04-historias-de-usuario.md) | Historias con criterios de aceptación (el detalle accionable) |
| 05 | [Backlog y roadmap](05-backlog-y-roadmap.md) | Prioridad, releases e hitos |
| 06 | [Listo y Terminado + glosario](06-listo-y-terminado.md) | Definition of Ready / Done y el vocabulario del dominio |

## Cómo leerlo

- **Negocio / stakeholders** → 01 y 03.
- **Equipo de desarrollo** → 04, 05 y 06 (más las vistas de arquitectura).
- **Planificación de sprint** → 05 (backlog) + 06 (Definition of Ready).

## Decisión de alcance de esta fase

El **auditor humano queda fuera** de esta fase: no hay revisión, mensajes ni visitas
del auditor en el flujo del agente. La evidencia y los registros quedan guardados; la
revisión humana se reconecta en una fase posterior. Todo lo demás del ciclo del
productor está dentro.
