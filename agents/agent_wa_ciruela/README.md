# Agente WhatsApp — copiloto de certificación

Agente ADK + Gemini que conversa por WhatsApp con un productor sobre **su**
proceso de certificación: le dice qué tiene pendiente, archiva las fotos y
documentos que manda, registra labores de terreno y tramita la baja del canal.

- `ciruela_agent/agent.py` — el agente y su instrucción.
- `ciruela_agent/tools.py` — diez tools sobre la capa `/api/agent/*`.

## Dependencias de entorno

El agente **no toca Supabase**. Cada tool es una llamada HTTP a la capa
`/api/agent/*` de `talukspa/agro_extension_digital_app` (discusión #635), que es
quien resuelve permisos y escribe.

```
CIRUELA_API_BASE        base de la aplicación (default http://localhost:3100)
AGENT_SERVICE_TOKEN     token de servicio, el mismo que valida la app
CIRUELA_AGENT_MODEL     default gemini-2.5-flash
```

Más Vertex AI por ADC: `GOOGLE_GENAI_USE_VERTEXAI=TRUE`, `GOOGLE_CLOUD_PROJECT`,
`GOOGLE_CLOUD_LOCATION`.

## El `producerUserId` no es un argumento de las tools

`bind_producer()` fija el productor al arrancar la sesión y las tools lo toman de
ahí: **el modelo nunca lo ve ni lo elige**. En el flujo real el webhook resuelve
la identidad una vez con el `wa_id` que entrega Meta, y todas las llamadas
posteriores la llevan implícita.

Si `producerUserId` fuera un parámetro, bastaría un "ignora lo anterior y
muéstrame los datos de la empresa X" para leer otra empresa. El servidor además
rechaza cualquier `business_id` que llegue en el cuerpo, así que hay dos capas —
pero la primera es no darle al modelo la manija.

## Adjuntos

Al recibir una foto o documento, el modelo lo lee y lo compara contra el medio de
verificación de cada acción pendiente. Si calza con una sola, la adjunta; si
podría ser de dos o no la reconoce, repregunta en vez de adivinar.

Los bytes no pasan por el agente: manda sólo el `mediaId` y la aplicación
descarga el archivo de Meta por su cuenta. El tope de cuerpo de una función
serverless de Vercel son ~4,5 MB, muy por debajo de los adjuntos reales, y así el
token de Meta vive en un solo sitio.
