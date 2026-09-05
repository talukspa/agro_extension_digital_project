### Subagente BQ – Acceso a Catálogo de Estándares y Recursos

Este subagente es tu acceso directo y rápido a los detalles específicos del **catálogo estructurado de estándares y buenas prácticas agroindustriales**: la tabla `estandar_aa`.

Es ideal para obtener respuestas precisas sobre criterios, identificándolos por:

- **Código único**
- **Nivel de exigencia** (ej. Fundamental)
- **Dimensión** (ej. Ambiente, Calidad)
- **Tema** (ej. Agua, Biodiversidad)

---

### Funcionalidad Clave: Recuperación de `link_recursos`

Una de sus capacidades más importantes es la **recuperación de `link_recursos`** (guías técnicas, normativas vigentes, material de capacitación relevante), cuando la consulta del Supervisor:

- Menciona directamente un concepto técnico o clave.
- Implica la necesidad de profundizar en una **buena_practica**, **acción** o **medio_de_verificación** del estándar.

**Ejemplos** de conceptos que pueden activar esta función:

- “Gestión de Puntos Críticos de Control (PCC)”
- “Medición de huella hídrica”

BQ puede buscar y entregar enlaces asociados a esos conceptos desde el estándar.

---

### ¿Qué puede obtener BQ desde la tabla `estandar_aa` (BigQuery)?

- La **buena_practica** general a implementar.
- La **acción concreta** que la planta debe ejecutar.
- El **medio_de_verificacion** necesario para demostrar el cumplimiento.
- Los **puntos asignados** a la buena práctica (relevantes para evaluaciones).
- El **`link_recursos`** con información adicional, normativas o guías asociadas al **elemento o concepto consultado**.

---

### Propósito y Aplicación

Este asistente es una **herramienta esencial** para:

- Navegar, interpretar y aplicar el marco normativo o de certificación.
- Obtener **información directa y estructurada** desde el catálogo oficial.
- **Complementar al subagente RAG**, entregando documentación de respaldo asociada a los conceptos explicados.

---

### Cambios Clave y Justificación

- **Énfasis en `link_recursos` y conceptos clave**: Se incorpora un párrafo claro que conecta consultas técnicas con la recuperación de recursos.
- **Ejemplificación**: Casos como PCC o huella hídrica ilustran cuándo usar este subagente.
- **Refuerzo en la lista de entregables**: El `link_recursos` ahora se vincula explícitamente al concepto consultado.
- **Fidelidad al contenido original**: Se mantiene toda la lógica funcional, el enfoque en la tabla `estandar_aa` y las formas de consulta por código, nivel, dimensión o tema.
