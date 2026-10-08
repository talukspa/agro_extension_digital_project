# 05 · Backlog priorizado y roadmap

## Backlog priorizado

Prioridad en **MoSCoW** (Must / Should / Could). Estimación en tallas de camiseta
(S/M/L) como referencia gruesa de tamaño, no de tiempo. "Depende de" señala qué tiene que
estar antes.

| Historia | Épica | Prioridad | Talla | Depende de |
|----------|-------|-----------|:-----:|-----------|
| HU-01.1 Vincular mi número | E1 | Must | M | — |
| HU-01.2 Aceptar el uso de mis datos | E1 | Must | S | — |
| HU-01.3 Sin vínculo no ve datos | E1 | Must | S | — |
| HU-02.3 Confirmar de qué empresa hablo | E2 | Must | M | E1 |
| HU-03.1 Ver mi avance | E3 | Must | S | E1, HU-02.3 |
| HU-03.2 Ver acciones pendientes | E3 | Must | S | E1, HU-02.3 |
| HU-02.1 Preguntar qué exige una acción | E2 | Must | M | E1 |
| HU-02.2 Preguntar por nota de voz | E2 | Should | S | HU-02.1 |
| HU-02.4 Reformular si no me sirvió | E2 | Should | S | HU-02.1 |
| HU-04.1 Subir una foto o documento | E4 | Must | M | E1 |
| HU-04.2 Confirmar el destino antes de guardar | E4 | Must | M | HU-04.1 |
| HU-04.3 Corregir el destino | E4 | Should | S | HU-04.2 |
| HU-04.4 Confirmación de guardado | E4 | Must | S | HU-04.2 |
| HU-05.1 Registrar labor por voz | E5 | Must | L | E1 |
| HU-05.2 Confirmar antes de guardar | E5 | Must | M | HU-05.1 |
| HU-05.3 Completar datos faltantes | E5 | Must | M | HU-05.1 |
| HU-06.1 Recomendación por acción | E6 | Could | M | E3 |
| HU-07.1 Aviso de cambio de nivel | E7 | Should | M | E1 |
| HU-07.2 Aviso de vencimiento próximo | E7 | Should | M | E1 |
| HU-07.3 Desactivar los avisos | E7 | Must* | S | HU-07.1 |

\* *Must dentro de E7*: si hay avisos, tiene que haber opt-out. Si E7 no entra en esta
fase, HU-07.3 tampoco.

## Roadmap por releases

Cada release es un incremento **usable por sí solo** una vez liberado R1. El orden respeta
las dependencias: primero conocer al productor, luego leerle el expediente, luego
escribirlo, luego enriquecerlo y avisarle.

### R1 · Conóceme *(habilitador)*
- **Historias:** HU-01.1, HU-01.2, HU-01.3.
- **Valor entregado:** el productor vincula su número y el copiloto ya sabe con quién
  habla. Nada personalizado funciona sin esto.
- **Hito H1:** *productor vinculado y con consentimiento.*

### R2 · Acompáñame *(lectura)*
- **Historias:** HU-02.3, HU-03.1, HU-03.2, HU-02.1, HU-02.2, HU-02.4.
- **Valor:** el productor pregunta cómo va, qué le falta y qué exige cada acción — con su
  contexto confirmado.
- **Hito H2:** *el copiloto responde sobre el expediente del productor.*

### R3 · Recíbeme la evidencia *(escritura)*
- **Historias:** HU-04.1, HU-04.2, HU-04.3, HU-04.4.
- **Valor:** la evidencia se carga desde el celular, ligada a la acción confirmada.
- **Hito H3:** *evidencia por WhatsApp, indistinguible de la web.*

### R4 · Escúchame *(labores por voz)*
- **Historias:** HU-05.1, HU-05.2, HU-05.3.
- **Valor:** el productor registra sus labores dictándolas, confirmando antes de guardar.
- **Hito H4:** *registro de labores por audio.*

### R5 · Avísame y guíame *(proactividad + aprendizaje)*
- **Historias:** HU-07.1, HU-07.2, HU-07.3, HU-06.1.
- **Valor:** el productor se entera de cambios de nivel y vencimientos, y recibe la
  capacitación puntual de cada acción.
- **Hito H5:** *avisos proactivos y recomendaciones contextuales.*

> Las fechas se fijan al planificar cada release. Este roadmap ordena por **valor y
> dependencia**, no por calendario.
