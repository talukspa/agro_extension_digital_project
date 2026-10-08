# 04 · Historias de usuario

Formato: **Como** [persona] **quiero** [algo] **para** [beneficio], con criterios de
aceptación en *Dado / Cuando / Entonces*. Todo en lenguaje de producto: sin detalles
técnicos. La prioridad y el release están en el [backlog](05-backlog-y-roadmap.md).

> Convención transversal: "el copiloto" = el asistente de WhatsApp. "El expediente" = los
> datos de certificación del productor (avance, acciones, evidencias).

---

## E1 · Vincular mi WhatsApp con mi cuenta

### HU-01.1 · Vincular mi número
**Como** productor **quiero** conectar mi WhatsApp con mi cuenta **para** que el copiloto
conozca mi empresa y mi avance.

- **Dado** que tengo una cuenta en la plataforma, **cuando** pido vincular mi WhatsApp,
  **entonces** recibo un código y, al enviarlo desde mi número, quedo vinculado.
- **Dado** que envié el código, **cuando** la vinculación se completa, **entonces** el
  copiloto me saluda por mi nombre y me dice de qué empresa(s) puede hablar.
- **Dado** un código vencido o equivocado, **cuando** lo envío, **entonces** el copiloto me
  lo dice y me ofrece generar uno nuevo.

### HU-01.2 · Aceptar el uso de mis datos
**Como** productor **quiero** saber y aceptar qué datos se usan **para** vincularme con
confianza.

- **Dado** que estoy por vincularme, **cuando** se me pide consentimiento, **entonces** veo
  en lenguaje simple qué información usará el copiloto y tengo que aceptarlo para continuar.
- **Dado** que ya acepté, **cuando** quiero, **entonces** puedo revocar el consentimiento y
  el copiloto deja de acceder a mi expediente.

### HU-01.3 · Un número sin vincular no ve datos
**Como** productor no vinculado **quiero** que el copiloto no muestre datos de nadie
**para** estar seguro de que mi información está protegida.

- **Dado** un número no vinculado, **cuando** escribe pidiendo su avance o su evidencia,
  **entonces** el copiloto **no** muestra datos del expediente y explica cómo vincularse.

---

## E2 · Resolver mis dudas de certificación

### HU-02.1 · Preguntar qué exige una acción
**Como** productor **quiero** preguntar qué evidencia o requisito pide una acción **para**
saber qué tengo que hacer.

- **Dado** que estoy vinculado, **cuando** pregunto por una acción, **entonces** el copiloto
  responde citando el código de la acción (p. ej. "A001").
- **Dado** que la respuesta depende del estándar, **cuando** respondo, **entonces** la
  respuesta corresponde al estándar de la instalación que confirmé (ver HU-02.3).

### HU-02.2 · Preguntar por nota de voz
**Como** productor con las manos ocupadas **quiero** preguntar por audio **para** no tener
que escribir.

- **Dado** que mando un audio con mi duda, **cuando** el copiloto lo recibe, **entonces**
  responde como si lo hubiera escrito.

### HU-02.3 · Confirmar de qué empresa/instalación hablo
**Como** productor con más de una empresa o instalación **quiero** que el copiloto confirme
de cuál se trata **para** no recibir una respuesta del predio equivocado.

- **Dado** que tengo más de una empresa/instalación/estándar, **cuando** hago una consulta,
  **entonces** el copiloto me pregunta a cuál se refiere **antes** de responder.
- **Dado** que tengo una sola, **cuando** consulto, **entonces** el copiloto la muestra
  pre-seleccionada y me pide un ok rápido.
- **Dado** que aún no confirmé el contexto, **cuando** insisto, **entonces** el copiloto no
  responde con datos de un contexto sin confirmar.

### HU-02.4 · Reformular si no me sirvió
**Como** productor **quiero** decir "no me quedó claro" **para** recibir otra explicación
sin empezar de cero.

- **Dado** que recibí una respuesta, **cuando** digo que no me sirvió, **entonces** el
  copiloto reformula o pide precisar, sin perder el contexto ya confirmado.

---

## E3 · Saber cómo voy

### HU-03.1 · Ver mi avance
**Como** productor **quiero** preguntar cómo voy **para** saber cuánto me falta.

- **Dado** el contexto confirmado, **cuando** pregunto "¿cómo voy?", **entonces** el
  copiloto me da mi avance de esa empresa/instalación, indicado como **referencial**.

### HU-03.2 · Ver mis acciones pendientes
**Como** productor **quiero** saber qué acciones tengo pendientes **para** priorizar.

- **Dado** el contexto confirmado, **cuando** pido mis pendientes, **entonces** el copiloto
  lista las acciones que me faltan, con su código, ordenadas de forma útil.

---

## E4 · Cargar evidencia desde el celular

### HU-04.1 · Subir una foto o documento
**Como** productor **quiero** mandar una foto como evidencia **para** no entrar a la web.

- **Dado** que mando una foto (incluidas las de iPhone) o un documento, **cuando** el
  copiloto la recibe, **entonces** la acepta y avanza a confirmar el destino (HU-04.2).
- **Dado** un archivo no válido (muy pesado o de tipo no permitido), **cuando** lo mando,
  **entonces** el copiloto me explica qué pasó y qué mandar en su lugar.

### HU-04.2 · Confirmar a qué acción va antes de guardar
**Como** productor **quiero** ver a qué empresa/instalación/acción se va a guardar y
confirmarlo **para** no equivocarme.

- **Dado** que mandé una evidencia, **cuando** el copiloto identifica el destino,
  **entonces** me muestra un resumen (empresa · instalación · acción) y me pide confirmar.
- **Dado** que confirmo, **cuando** doy el ok, **entonces** la evidencia queda registrada en
  esa acción y el copiloto me lo avisa.
- **Dado** que el copiloto no logra determinar la acción, **cuando** recibe la evidencia,
  **entonces** me pregunta a cuál va — nunca la guarda suelta.

### HU-04.3 · Corregir el destino
**Como** productor **quiero** corregir la acción si el copiloto eligió mal **para** que
quede en el lugar correcto.

- **Dado** el resumen de destino, **cuando** digo que no es esa acción, **entonces** el
  copiloto me deja indicar la correcta y vuelve a pedir confirmación.

### HU-04.4 · Confirmación de que quedó guardada
**Como** productor **quiero** una confirmación clara **para** saber que ya no tengo que
volver a subirla.

- **Dado** que confirmé, **cuando** la evidencia se guarda, **entonces** recibo un mensaje
  que dice a qué acción quedó ligada.

---

## E5 · Registrar mis labores hablando

### HU-05.1 · Registrar una labor por voz
**Como** productor **quiero** contar por audio qué hice **para** dejar el registro sin
escribir.

- **Dado** que mando un audio describiendo una labor, **cuando** el copiloto lo procesa,
  **entonces** arma un resumen ordenado de la labor (cuartel, producto, dosis, etc.) y me
  lo presenta.

### HU-05.2 · Confirmar el registro antes de guardar
**Como** productor **quiero** revisar el resumen y confirmarlo **para** que no se guarde
algo mal entendido.

- **Dado** un resumen de la labor, **cuando** el copiloto me lo lee, **entonces** solo lo
  guarda si yo confirmo.
- **Dado** que algo está mal, **cuando** lo corrijo, **entonces** el copiloto ajusta el
  resumen y vuelve a pedir confirmación.

### HU-05.3 · Completar datos faltantes
**Como** productor **quiero** que el copiloto me pida lo que falta **para** no dejar un
registro a medias.

- **Dado** que en mi audio falta un dato obligatorio (p. ej. cuártel o dosis), **cuando** el
  copiloto arma el resumen, **entonces** me pregunta ese dato antes de poder guardar; nunca
  registra incompleto.

---

## E6 · Recibir recomendaciones de capacitación

### HU-06.1 · Recomendación por acción
**Como** productor **quiero** que me recomiende el material de la acción específica
**para** aprender a resolverla.

- **Dado** que tengo una acción pendiente o pregunto por ella, **cuando** pido ayuda,
  **entonces** el copiloto me ofrece la guía/curso **de esa acción**, no una lista genérica.

---

## E7 · Enterarme de lo importante

### HU-07.1 · Aviso de cambio de nivel
**Como** productor **quiero** enterarme si mi nivel proyectado cambia **para** reaccionar a
tiempo.

- **Dado** que estoy vinculado y con avisos activos, **cuando** mi nivel proyectado cambia,
  **entonces** recibo un aviso por WhatsApp, indicado como **referencial**.

### HU-07.2 · Aviso de vencimiento próximo
**Como** productor **quiero** que me avisen cuando una acción está por vencer **para** no
dejarla pasar.

- **Dado** que tengo una acción con fecha próxima, **cuando** se acerca el vencimiento,
  **entonces** recibo un aviso a tiempo con la acción concreta.

### HU-07.3 · Desactivar los avisos
**Como** productor **quiero** poder dejar de recibir avisos **para** no sentirme invadido.

- **Dado** que recibo avisos, **cuando** pido no recibir más, **entonces** el copiloto deja
  de enviarlos y me confirma que quedó desactivado.
