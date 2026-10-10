# Menú de opciones en WhatsApp (mensajes interactivos)

Fecha: 2026-10-09

## 1. El problema

Muchos productores no interactúan con el agente porque no saben cómo abordarlo:
el saludo actual termina en "¿En qué puedo ayudarte hoy?" y el productor tiene
que inventar la pregunta. Queremos que el agente guíe la conversación como el
bot de una tienda: opciones tocables al inicio y cada vez que ayuden, hasta que
el productor pueda expresar lo que quiere.

Hoy:

- El saludo es un texto fijo en `agents/core/prompts/agent_{aa,pp}/root.md`
  (§2) y cada respuesta cierra con un "¿Hay algo más…?" obligatorio (§4).
- El webhook sólo **envía** texto (`create_text_message`).
- Un mensaje entrante `type: "interactive"` (el toque de un botón o de una fila
  de lista) no se procesa: cae en el acuse "Solo puedo procesar mensajes de
  texto, audio, imágenes y PDF".

## 2. Límites de WhatsApp que fijan el diseño

| Formato | Opciones | Título | Descripción | Cuerpo |
|---|---|---|---|---|
| Botones de respuesta (`interactive.type = "button"`) | 1–3 | ≤ 20 caracteres | — | ≤ 1024 |
| Lista (`interactive.type = "list"`) | 1–10 filas | ≤ 24 caracteres | ≤ 72 caracteres | ≤ 1024; botón ≤ 20 |

Los ids de botón y de fila deben ser únicos dentro del mensaje.

## 3. Decisión: el agente decide, el webhook dibuja

Se descartó un menú fijo en el webhook (predecible, pero estático: no sirve
para "guiar las veces que sea necesario"). El agente decide **cuándo** y
**qué** opciones ofrecer; el webhook sólo las convierte al formato de WhatsApp.

Los sub-agentes (rag, catalog, record) corren como `AgentTool` dentro del raíz:
sus eventos internos no llegan al stream que lee el webhook. Por eso la tool
vive en el agente **raíz**, que es también quien saluda y redacta la respuesta
final.

## 4. Agente (`agents/`)

### 4.1 Tool `ofrecer_opciones`

Módulo nuevo `core/options_tools.py`, registrado en `tools=[...]` del raíz en
`core/agent.py` (AA y PP).

```python
def ofrecer_opciones(opciones: list[dict], boton: str = "Ver opciones") -> dict
```

- `opciones`: lista de `{"titulo": str, "descripcion": str}` (descripción
  opcional).
- Valida: 1–10 opciones; título no vacío y ≤ 24; descripción ≤ 72; títulos sin
  repetir (comparando sin mayúsculas ni espacios extremos); `boton` no vacío y
  ≤ 20.
- Si algo falla devuelve `{"ok": False, "error": "<motivo legible>"}` — el
  contrato que `core/retry_plugin.py` ya reconoce, así el modelo corrige y
  reintenta. Nunca trunca en silencio: un título cortado a la mitad es peor que
  un reintento.
- Si pasa, devuelve `{"ok": True, "data": {"opciones_ofrecidas": n}}`. No envía
  nada: el texto de la respuesta sigue siendo el texto normal del agente.

### 4.2 Prompt raíz (AA y PP)

- **§2 Inicio de conversación:** saludo corto + llamada **obligatoria** a
  `ofrecer_opciones` con el menú principal:

  | Título | Descripción |
  |---|---|
  | Subir un verificador | Foto o documento para una acción de tu plan |
  | Mi avance y puntaje | Cómo vas en tu plan y tu nivel |
  | Qué me falta | Acciones pendientes y próximas fechas |
  | Conocer el estándar | Qué pide, dimensiones y puntajes |
  | Sustentabilidad | Buenas prácticas para producir mejor |
  | Registrar una labor | Algo que hiciste en campo o planta |
  | Hablar con el auditor | Dejar o leer mensajes |

- **§4 Finalización:** reemplaza el cierre fijo "¿Hay algo más…?" por: después
  de responder, ofrece con `ofrecer_opciones` 2–4 siguientes pasos probables
  (o el menú principal si no hay uno claro).
- **Cuándo además:** cuando el productor es vago ("hola", "ayuda", "no sé"),
  y para desambiguar (p. ej. los títulos de sus acciones pendientes que trae
  el EXPEDIENTE).
- **Cuándo no:** cuando el productor está en medio de algo concreto que
  tiene que escribir (el texto de un mensaje al auditor, los datos de una
  labor).
- El texto de la respuesta no repite las opciones: van sólo en la tool.

## 5. Webhook (`webhook-application/`)

### 5.1 Leer las opciones del stream

`external_services/agent_client.send_to_agent` ya recorre todos los eventos.
Además del texto, recoge la **última** parte `function_call` con
`name == "ofrecer_opciones"` y devuelve sus `args.opciones` / `args.boton`
normalizados en `{"response": str, "options": list | None, "button": str | None}`.
Se toma la última porque si el modelo reintentó tras un `ok: False`, la válida
es la final. Se re-validan los límites del §2 en el webhook (defensa ante args
que el modelo emitió y la tool rechazó); si no pasan, `options = None`.

`messages.send_message_to_agent` pasa a devolver ese par (texto + opciones) a
sus tres llamadores: texto, audio y media.

### 5.2 Enviar

Función nueva `send_agent_reply(phone, text, options, button, app_name)` en
`messages.py`, usada por los tres manejadores en lugar del
`send_whatsapp_message(create_text_message(...))` actual:

- Sin opciones → texto, igual que hoy.
- 1–3 opciones y todos los títulos ≤ 20 → botones de respuesta.
- Si no → lista (`boton` como etiqueta).
- Si el texto supera 1024 caracteres → se manda como texto y después el
  interactivo con cuerpo "¿Qué quieres hacer ahora?".
- Si el envío interactivo falla (`send_whatsapp_message` lanza por
  `raise_for_status`) → se reenvía como texto con las opciones numeradas al final. El productor
  nunca se queda sin respuesta.

Builders nuevos en `external_services/whatsapp_client.py`:
`create_button_message(body, titles)` y
`create_list_message(body, button, rows)`. Ids `opt_1…opt_n`.

### 5.3 Recibir el toque

- `models/messages.py`: el mensaje gana `interactive` con `type`
  (`"button_reply"` | `"list_reply"`) y `button_reply` / `list_reply`
  (`id`, `title`, `description` opcional).
- `get_message_content()` para `interactive` devuelve el título, más
  `" — " + descripción` si viene (así "Qué me falta" llega con contexto).
- El despachador trata `type == "interactive"` con contenido como un texto:
  mismo camino que `_process_single_text_message` (sesión, consentimiento y
  tope de longitud intactos). Un `interactive` sin respuesta reconocible sigue
  cayendo en el acuse actual.

## 6. Errores

| Caso | Qué pasa |
|---|---|
| Args inválidos en la tool | `ok: False` → el retry plugin hace que el modelo corrija |
| El modelo no llama la tool | Llega sólo texto, como hoy. Aceptado (es el costo de la opción elegida); un test de prompt fija la regla del saludo |
| Teléfono no vinculado a un productor | El menú se muestra igual; las opciones personales reciben la respuesta "no vinculado" que ya da el EXPEDIENTE. No se ocultan en esta versión |
| Falla el envío interactivo | Fallback a texto con opciones numeradas |
| Toque de un menú viejo (de hace días) | Es texto como cualquier otro: el agente responde con el contexto actual |

## 7. Fuera de alcance

- Ocultar opciones según si el teléfono está vinculado.
- Menús distintos para AA y PP (hoy son el mismo menú).
- Mensajes interactivos con encabezado, pie o imágenes.
- Analítica de qué opciones se tocan (queda en los logs como texto entrante).

## 8. Pruebas

**Agente**
- `ofrecer_opciones`: cada límite (0 y 11 opciones, título 25, descripción 73,
  duplicados, botón 21) devuelve `ok: False`; un caso válido devuelve `ok: True`.
- La tool está registrada en el raíz de AA y PP.
- Prompt raíz: el saludo obliga a `ofrecer_opciones` con los 7 títulos; el
  cierre fijo "¿Hay algo más…?" ya no es obligatorio. Mismo estilo de los tests
  actuales: la regla está y un marcador antónimo no.

**Webhook**
- Builders de botones y lista producen el JSON de la Cloud API.
- `send_to_agent` extrae la última llamada a `ofrecer_opciones`, ignora la de
  args inválidos, y no rompe sin ella.
- `send_agent_reply`: sin opciones → texto; 3 cortas → botones; 3 con un título
  de 21 → lista; 7 → lista; texto de 1100 → texto + interactivo; envío
  interactivo falla → texto numerado.
- Parseo de `button_reply` y `list_reply` y despacho al agente como texto.

## 9. Entrega

Rama `feat/menu-opciones-whatsapp` desde `main`, separada de
`fix/evidence-attach-media-id`. Ambas tocan `agent_client.py` y `root.md`; el
conflicto se resuelve al mergear la segunda. Requiere redeploy de los agentes
(AA y PP) y del webhook; el webhook primero es seguro (sin la tool no hay
opciones y responde texto como hoy).
