# Firestore Database Schema - agro-extension-db

**Proyecto**: agro-extension-digital-npe  
**Base de datos**: agro-extension-db  
**Fecha de extracción**: 2025-08-19

## Resumen de Colecciones

Total de colecciones encontradas: **6**

## Colección: `auditors`

**Documentos analizados**: 5

### Estructura de Campos

| Campo | Tipos de Datos | Descripción |
|-------|----------------|-------------|
| `auditor_name` | str | - |
| `auditor_email` | str | - |
| `auditor_phone` | str | - |
| `assigned_businesses` | array | - |
| `assigned_businesses[]` | str | - |
| `auditor_id` | int | - |

### Documentos de Muestra

#### Documento 1 - ID: `1`

```json
{
  "auditor_name": "James Black",
  "auditor_email": "elizabeth86@example.net",
  "auditor_phone": "001-946-575-7455x47184",
  "assigned_businesses": [
    "966290501",
    "17049695-7",
    "96604260-5",
    "78023030-4",
    "10577592-k"
  ],
  "auditor_id": 1
}
```

#### Documento 2 - ID: `2`

```json
{
  "auditor_name": "Wesley Smith",
  "auditor_email": "andrew26@example.net",
  "auditor_phone": "+1-286-981-3470x535",
  "assigned_businesses": [
    "17708318-6",
    "10590515-7",
    "18276552-k"
  ],
  "auditor_id": 2
}
```

## Colección: `business_profiles`

**Documentos analizados**: 5

### Estructura de Campos

| Campo | Tipos de Datos | Descripción |
|-------|----------------|-------------|
| `commune` | str | - |
| `rut` | str | - |
| `legal_name` | str | - |
| `region` | str | - |
| `owner_email` | str | - |
| `address` | str | - |
| `owner_phone` | str | - |
| `digital_tools_used_at_work` | array | - |
| `digital_tools_used_at_work[]` | str | - |
| `process_type` | str | - |
| `owner_name` | str | - |
| `owner_role` | str | - |
| `business_size` | str | - |
| `digital_tools_experienced` | array | - |
| `digital_tools_experienced[]` | str | - |

### Documentos de Muestra

#### Documento 1 - ID: `1-9`

```json
{
  "commune": "Arica",
  "rut": "1-9",
  "legal_name": "Cerveceria",
  "region": "Arica y Parinacota",
  "owner_email": "rodrigo.vasquez.fernandez@gmail.com",
  "address": "Bartolo Soto 3950, Depto 701",
  "owner_phone": "968767906",
  "digital_tools_used_at_work": [
    "Computador"
  ],
  "process_type": "Secado en horno (obtención de ciruela seca en formato condición natural)",
  "owner_name": "Rodrigo",
  "owner_role": "Ingeniero",
  "business_size": "Micro (ventas anuales entre 0,01 UF a 2.400 UF).",
  "digital_tools_experienced": [
    "Computador"
  ]
}
```

#### Documento 2 - ID: `10521712-9`

```json
{
  "commune": "Arica",
  "rut": "10521712-9",
  "legal_name": "test",
  "region": "Arica y Parinacota",
  "owner_email": "test",
  "address": "test",
  "owner_phone": "test",
  "digital_tools_used_at_work": [
    "Computador"
  ],
  "process_type": "Secado en horno (obtención de ciruela seca en formato condición natural)",
  "owner_name": "test",
  "owner_role": "test",
  "business_size": "Micro (ventas anuales entre 0,01 UF a 2.400 UF).",
  "digital_tools_experienced": [
    "Computador"
  ]
}
```

## Colección: `registers`

**Documentos analizados**: 5

### Estructura de Campos

| Campo | Tipos de Datos | Descripción |
|-------|----------------|-------------|
| `auditor_comments` | str | - |
| `validation_status` | str | - |
| `business_rut` | str | - |
| `validation_timestamp` | str | - |
| `folder` | str | - |
| `id` | int | - |
| `log` | str | - |
| `standard_code` | str | - |
| `upload_timestamp` | str | - |
| `auditor_id` | int | - |

### Documentos de Muestra

#### Documento 1 - ID: `1`

```json
{
  "auditor_comments": "Recent still good carry. Executive since bar claim I. Manage house situation teacher view exactly job.",
  "validation_status": "rejected",
  "business_rut": "78023030-4",
  "validation_timestamp": "1988-10-19T21:09:47",
  "folder": "/path/to/folder/1",
  "id": 1,
  "log": "System range billion with seek. Lose manager door impact. Position message cell future really process PM town.\nIdea instead child PM. See start wind special how. Dream send as ask Republican.",
  "standard_code": "A028",
  "upload_timestamp": "1978-10-22T15:47:24",
  "auditor_id": 3
}
```

#### Documento 2 - ID: `10`

```json
{
  "auditor_comments": "Sea skill chance feeling nothing couple international walk. Manage open less the civil.",
  "validation_status": "validated",
  "business_rut": "16411526-7",
  "validation_timestamp": "2010-08-05T23:31:49",
  "folder": "/path/to/folder/10",
  "id": 10,
  "log": "Season building section think site beyond. A lay agency. Over according exactly.\nMouth strategy year rather detail may. Early money run whom drop television none. Trial end could sort anyone rest.",
  "standard_code": "A045",
  "upload_timestamp": "1972-08-10T22:01:03",
  "auditor_id": 1
}
```

## Colección: `resources`

**Documentos analizados**: 5

### Estructura de Campos

| Campo | Tipos de Datos | Descripción |
|-------|----------------|-------------|
| `standard_code` | str | - |
| `resource_code` | str | - |
| `dimension` | str | - |
| `theme` | str | - |
| `detail` | str | - |
| `type` | str | - |
| `urls` | object | - |
| `urls.pdf` | str | - |
| `urls.web` | str | - |
| `urls.word` | str | - |

### Documentos de Muestra

#### Documento 1 - ID: `0`

```json
{
  "standard_code": "A007",
  "resource_code": "0",
  "dimension": "Ambiente",
  "theme": "Agua",
  "detail": "Evite el desperdicio de agua",
  "type": "Señalética",
  "urls": {
    "pdf": "http://ciruelacertificada.cl/wp-content/uploads/2025/01/P9-A7-.pdf",
    "web": "https://ciruelacertificada.cl/recurso/senaletica-evite-el-desperdicio-de-agua/"
  }
}
```

#### Documento 2 - ID: `1`

```json
{
  "standard_code": "A005",
  "resource_code": "1",
  "dimension": "Ambiente",
  "theme": "Agua",
  "detail": "TDR para la contratación de empresa que realice plan de gestión del recurso hídrico",
  "type": "TDR",
  "urls": {
    "pdf": "https://ciruelacertificada.cl/wp-content/uploads/2024/12/P7-A5-TDR-Plan-gestion-recurso-hidrico.pdf",
    "word": "https://ciruelacertificada.cl/wp-content/uploads/2024/12/P7-A5-TDR-Plan-gestion-recurso-hidrico.docx",
    "web": "https://ciruelacertificada.cl/recurso/tdr-para-la-contratacion-de-empresa-que-realice-plan-de-gestion-del-recurso-hidrico/"
  }
}
```

## Colección: `standard_responses`

**Documentos analizados**: 5

### Estructura de Campos

| Campo | Tipos de Datos | Descripción |
|-------|----------------|-------------|
| `date` | str | - |
| `is_completed` | bool | - |
| `business_rut` | str | - |
| `answers` | array | - |
| `answers[]` | object | - |
| `answers[].standard_code` | str | - |
| `answers[].answer_value` | str | - |

### Documentos de Muestra

#### Documento 1 - ID: `04OVSdslUWPNXLoPJRM2`

```json
{
  "date": "2025-01-13 13:12:17.546991+00:00",
  "is_completed": true,
  "business_rut": "797490709",
  "answers": [
    {
      "standard_code": "A001",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A002",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A003",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A004",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A005",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A006",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A007",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A008",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A009",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A010",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A011",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A012",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A013",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A014",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A015",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A016",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A017",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A018",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A019",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A020",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A021",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A022",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A023",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A024",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A025",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A026",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A027",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A028",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A029",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A030",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A031",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A032",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A033",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A034",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A035",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A036",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A037",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A038",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A039",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A040",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A041",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A042",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A043",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A044",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A045",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A046",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A047",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A048",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A049",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A050",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A051",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A052",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A053",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A054",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A055",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A056",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A057",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A058",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A059",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A060",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A061",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A062",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A063",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A064",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A065",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A066",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A067",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A068",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A069",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A070",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A071",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A072",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A073",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A074",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A075",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A076",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A077",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A078",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A079",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A080",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A081",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A082",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A083",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A084",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A085",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A086",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A087",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A088",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A089",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A090",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A091",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A092",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A093",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A094",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A095",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A096",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A097",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A098",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A099",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A100",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A101",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A102",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A103",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A104",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A105",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A106",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A107",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A108",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A109",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A110",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A111",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A112",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A113",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A114",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A115",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A116",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A117",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A118",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A119",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A120",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A121",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A122",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A123",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A124",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A125",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A126",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A127",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A128",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A129",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A130",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A131",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A132",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A133",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A134",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A135",
      "answer_value": "Si cumplo"
    }
  ]
}
```

#### Documento 2 - ID: `2vmmQEu1m4a7qFZq5Irk`

```json
{
  "date": "2024-12-12 20:01:46.901758+00:00",
  "is_completed": true,
  "business_rut": "76059579-9",
  "answers": [
    {
      "standard_code": "A001",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A002",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A003",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A004",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A005",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A006",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A007",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A008",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A009",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A010",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A011",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A012",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A013",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A014",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A015",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A016",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A017",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A018",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A019",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A020",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A021",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A022",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A023",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A024",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A025",
      "answer_value": "No aplica a mi sistema productivo"
    },
    {
      "standard_code": "A026",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A027",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A028",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A029",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A030",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A031",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A032",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A033",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A034",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A035",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A036",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A037",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A038",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A039",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A040",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A041",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A042",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A043",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A044",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A045",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A046",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A047",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A048",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A049",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A050",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A051",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A052",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A053",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A054",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A055",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A056",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A057",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A058",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A059",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A060",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A061",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A062",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A063",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A064",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A065",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A066",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A067",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A068",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A069",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A070",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A071",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A072",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A073",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A074",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A075",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A076",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A077",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A078",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A079",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A080",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A081",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A082",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A083",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A084",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A085",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A086",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A087",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A088",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A089",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A090",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A091",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A092",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A093",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A094",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A095",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A096",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A097",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A098",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A099",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A100",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A101",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A102",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A103",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A104",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A105",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A106",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A107",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A108",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A109",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A110",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A111",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A112",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A113",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A114",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A115",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A116",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A117",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A118",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A119",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A120",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A121",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A122",
      "answer_value": "No cumplo, pero me es factible"
    },
    {
      "standard_code": "A123",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A124",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A125",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A126",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A127",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A128",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A129",
      "answer_value": "No cumplo"
    },
    {
      "standard_code": "A130",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A131",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A132",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A133",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A134",
      "answer_value": "Si cumplo"
    },
    {
      "standard_code": "A135",
      "answer_value": "No cumplo"
    }
  ]
}
```

## Colección: `standards`

**Documentos analizados**: 2

### Estructura de Campos

| Campo | Tipos de Datos | Descripción |
|-------|----------------|-------------|
| `template_name` | str | - |
| `description` | str | - |
| `questions` | array | - |
| `questions[]` | object | - |
| `questions[].points` | int | - |
| `questions[].level` | str | - |
| `questions[].dimension` | str | - |
| `questions[].verification_detail` | str | - |
| `questions[].action` | str | - |
| `questions[].valid_answers` | array | - |
| `questions[].valid_answers[]` | str | - |
| `questions[].standard_code` | str | - |
| `questions[].link` | str | - |
| `questions[].theme` | str | - |
| `questions[].linked_resources` | array | - |
| `questions[].linked_resources[]` | str | - |
| `questions[].good_practice` | str | - |
| `questions[].verification_type` | str | - |

### Documentos de Muestra

#### Documento 1 - ID: `adecuacion-agroindustrial`

```json
{
  "template_name": "adecuacion-agroindustrial",
  "description": "Estándar de Adecuación Agroindustrial",
  "questions": [
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro de consumo de agua mensual con la siguiente información: - Fuente de abastecimiento disponible (canal, pozo, suministro de agua potable, red aljibe, etc.). - Consumo mensual por de cada fuente (m3). - Tipo de uso dentro de la línea de proceso de cada una de las fuentes.",
      "action": "La planta registra mensualmente el consumo de agua en las plantas, especificando la fuente de abastecimiento y su uso.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A001",
      "link": "https://ciruelacertificada.cl/?s=A001&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "68",
        "203",
        "338",
        "475"
      ],
      "good_practice": "Gestionar los recursos hídricos en la planta",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada) o certificado de participación en instancias de capacitación externa (cursos, seminarios, congresos, etc.). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta capacita a las personas tomadoras de decisiones en el ámbito hídrico, abordando estrategias para la gestión eficiente del recurso.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A002",
      "link": "https://ciruelacertificada.cl/?s=A002&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "42",
        "69",
        "204",
        "339"
      ],
      "good_practice": "Gestionar los recursos hídricos en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Mapa o plano de fuentes de agua e infraestructura hídrica, ya sea digital o en papel.",
      "action": "La planta cuenta con un mapa o plano con la ubicación de las fuentes de aprovisionamiento de agua dentro de la explotación y la estructura hídrica, asociada a las diferentes fases de la producción (secado, tiernizado, despepitado, etc.).",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A003",
      "link": "https://ciruelacertificada.cl/?s=A003&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "70",
        "205",
        "340"
      ],
      "good_practice": "Gestionar los recursos hídricos en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta capacita a las personas que ejecuten acciones asociadas al ámbito hídrico, abordando acciones operativas que permitan la gestión eficiente del recurso.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A004",
      "link": "https://ciruelacertificada.cl/?s=A004&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "43",
        "71",
        "206",
        "341"
      ],
      "good_practice": "Gestionar los recursos hídricos en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Plan de gestión del recurso hídrico que considere los siguientes indicadores: - Un indicador de eficiencia del uso del agua utilizada (litros de agua/kg ciruela seca). - Una meta de eficiencia del uso del agua en base al indicador propuesto en el punto anterior. - Una propuesta de un porcentaje de reducción del uso del agua (en caso de que no se cumpla con la meta de eficiencia).",
      "action": "La planta cuenta con un documento que define un plan de gestión del recurso hídrico.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A005",
      "link": "https://ciruelacertificada.cl/?s=A005&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "1",
        "72",
        "207",
        "342"
      ],
      "good_practice": "Gestionar los recursos hídricos en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Documento que evidencie la medición de huella hídrica en base a la metodología de la norma ISO 14.046.",
      "action": "La planta mide la huella de agua corporativa que usa en actividades propias.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A006",
      "link": "https://ciruelacertificada.cl/?s=A006&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "73",
        "208",
        "343"
      ],
      "good_practice": "Gestionar los recursos hídricos en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de señaléticas de ahorro de agua en servicios higiénicos y de alimentación, zona de lavado de equipos y maquinarias.",
      "action": "La planta cuenta con señalética orientada al ahorro de agua en lugares críticos (servicios higiénicos y de alimentación, zona de lavado de equipos y maquinarias).",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A007",
      "link": "https://ciruelacertificada.cl/?s=A007&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "0",
        "74",
        "209",
        "344"
      ],
      "good_practice": "Minimizar las pérdidas de agua en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Check list o registro de mantención de la infraestructura con los siguientes datos: * Tipo de evento. * Fecha de ejecución. * Equipo o infraestructura. * Detalle de labores. * Empresa y/o responsable. En el caso de que las mantenciones las realice una empresa externa, esta debe entregar un comprobante o informe que certifique las acciones realizadas estén en función de lo solicitado.",
      "action": "La planta realiza revisiones periódicas, mantenciones y reparaciones de la infraestructura hídrica, para controlar las fugas de agua.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A008",
      "link": "https://ciruelacertificada.cl/?s=A008&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "2",
        "75",
        "210",
        "345"
      ],
      "good_practice": "Minimizar las pérdidas de agua en la planta",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Check list o calendarización de monitoreo de comprobación de fugas con la siguiente información. * Tipo de evento. * Fecha de ejecución. * Equipo o infraestructura. * Detalle de labores. * Empresa y/o responsable.",
      "action": "La planta monitorea regularmente las fugas o roturas dentro de su infraestructura hídrica.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A009",
      "link": "https://ciruelacertificada.cl/?s=A009&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "3",
        "76",
        "211",
        "346"
      ],
      "good_practice": "Minimizar las pérdidas de agua en la planta",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de mangueras y lavamanos, observando sistemas de corte automático.",
      "action": "La planta implementa sistemas automáticos de corte de agua en todas las mangueras utilizadas para la limpieza de pisos y en los lavamanos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A010",
      "link": "https://ciruelacertificada.cl/?s=A010&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "77",
        "212",
        "347"
      ],
      "good_practice": "Minimizar las pérdidas de agua en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo o procedimiento de limpieza de materia prima.",
      "action": "La planta promueve el ahorro de agua en los protocolos de lavado o limpieza de materia prima.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A011",
      "link": "https://ciruelacertificada.cl/?s=A011&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "78",
        "213",
        "348"
      ],
      "good_practice": "Minimizar las pérdidas de agua en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo o procedimiento de limpieza de suelos.",
      "action": "La planta privilegia las prácticas como raspado y barrido antes de lavar los suelos, usando mangueras de alta presión o reutilizando aguas de preparación de alimentos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A012",
      "link": "https://ciruelacertificada.cl/?s=A012&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "79",
        "214",
        "349"
      ],
      "good_practice": "Minimizar las pérdidas de agua en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de la zona de tratado y posterior recirculación de aguas dentro de la planta. En el caso de que esta acción la realice una empresa externa, debe existir un comprobante detallado de los procedimientos utilizados y el destino del agua reutilizada.",
      "action": "La planta implementa técnicas de recirculación y reutilización de aguas, ya sea para el uso en planta, para riego (áreas verdes o cultivos asociados) o para reincorporar el recurso a los cursos de agua preexistentes.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A013",
      "link": "https://ciruelacertificada.cl/?s=A013&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "80",
        "215",
        "350"
      ],
      "good_practice": "Reutilizar el agua dentro de la planta",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de fuentes y cursos de agua limpios.",
      "action": "La planta cuenta con fuentes y cursos de agua libres de residuos sólidos domiciliarios y agrícolas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A014",
      "link": "https://ciruelacertificada.cl/?s=A014&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "81",
        "216",
        "351"
      ],
      "good_practice": "Minimizar los riesgos de contaminación de aguas",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de existencia de zona de lavado de equipos que no esté en contacto con el suelo y con vías de evacuación de aguas de lavado.",
      "action": "La planta cuenta con un espacio específico para el lavado de equipos móviles, ej. Bins, alejado de las fuentes o cursos de agua.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A015",
      "link": "https://ciruelacertificada.cl/?s=A015&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "82",
        "217",
        "352"
      ],
      "good_practice": "Minimizar los riesgos de contaminación de aguas",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Informe de análisis físico-químicos y microbiológicos actualizados periódicamente.",
      "action": "La planta realiza análisis periódicos a las aguas residuales provenientes de instalaciones de procesamiento, previo a que estas sean desechadas o reutilizadas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A016",
      "link": "https://ciruelacertificada.cl/?s=A016&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "83",
        "218",
        "353"
      ],
      "good_practice": "Monitorear y asegurar la calidad del agua utilizada en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Informe de análisis físico-químicos y microbiológicos, actualizados periódicamente según NCH409.",
      "action": "La planta realiza análisis periódicos para evaluar la calidad química y biológica de las fuentes de alimentación de agua.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A017",
      "link": "https://ciruelacertificada.cl/?s=A017&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "84",
        "219",
        "354"
      ],
      "good_practice": "Monitorear y asegurar la calidad del agua utilizada en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Diagnóstico de la biodiversidad con los siguientes puntos: - Mapa con identificación de áreas en la explotación con alto valor ecológico (ej. lagos, estanques y cursos de agua, corredores de vida silvestre, humedales, pastizales ricos en especies, etc.). - Catastro de la biodiversidad existente en el lugar, por ejemplo: principales especies presentes en el entorno (aves, mamíferos, árboles, insectos, hongos, arbustos, etc.) - Registro fotográfico con georreferenciación del estado inicial de las zonas de vegetación natural de conectividad, márgenes y límites de los campos, zonas de amortiguamiento ribereño y áreas de conservación con vegetación nativa.",
      "action": "La planta cuenta con un diagnóstico donde se identifica la biodiversidad existente y las áreas de alto valor ecológico, dentro de su propiedad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A018",
      "link": "https://ciruelacertificada.cl/?s=A018&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "11",
        "85",
        "220",
        "355"
      ],
      "good_practice": "Establecer un ordenamiento territorial y línea base",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Plan de gestión con protocolos para la implementación de las siguientes medidas: - Línea base de sitios de interés. - Priorización y definición de objetivos de conservación. - Medidas de conectividad, restauración y rehabilitación. - Medidas de manejo y control de especies exóticas. - Plan de ordenamiento predial. Dicho documento debe tener una fecha de elaboración inferior a 5 años.",
      "action": "La planta cuenta con un plan para la gestión de la biodiversidad que propone medidas de conservación, utilizando información rescatada en el diagnóstico realizado previamente. Este plan es evaluado y actualizado cada 5 años.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A019",
      "link": "https://ciruelacertificada.cl/?s=A019&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "12",
        "86",
        "221",
        "356"
      ],
      "good_practice": "Establecer un ordenamiento territorial y línea base",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta capacita a quienes trabajan permanentemente en la empresa, sobre el plan de gestión de la biodiversidad propuesto, generando un listado de acciones a tomar para potenciar la biodiversidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A020",
      "link": "https://ciruelacertificada.cl/?s=A020&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "44",
        "87",
        "222",
        "357"
      ],
      "good_practice": "Fomentar la participación en acciones para la protección y conservación de ecosistemas, hábitat o especies",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Actas de reuniones de mesas de trabajo con empresas en el territorio.",
      "action": "La planta mantiene un diálogo permanente con las empresas relacionadas al rubro en el territorio, con el objetivo de implementar en conjunto, medidas de conservación y mitigación que les permitan tener un plan de gestión de manera asociativa.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A021",
      "link": "https://ciruelacertificada.cl/?s=A021&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "56",
        "88",
        "223",
        "358"
      ],
      "good_practice": "Fomentar la participación en acciones para la protección y conservación de ecosistemas, hábitat o especies",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de la existencia de vegetación natural de conectividad.",
      "action": "La planta mantiene la conectividad entre la vegetación natural, potenciando su complejidad estructural, a través de cercos vivos, corredores biológicos, franjas ribereñas, entre otras.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A022",
      "link": "https://ciruelacertificada.cl/?s=A022&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "89",
        "224",
        "359"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de los márgenes ribereños o franjas de amortiguación, los que deben ser mayores a 5 m en cursos de agua y mayores a 10 m en manantiales y cuerpos de agua.",
      "action": "La planta protege las zonas de amortiguamiento ribereño (dentro de su propiedad), en el caso de encontrarse a menos de 50 metros de un cuerpo de agua o ecosistema acuático.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A023",
      "link": "https://ciruelacertificada.cl/?s=A023&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "90",
        "225",
        "360"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de monitoreo de especies exóticas invasoras con la siguiente información: - Fecha del hallazgo. - Nombre de la especie. - Ubicación. - N° de individuos visualizados. - Daño provocado. - Medidas de mitigación.",
      "action": "La planta identifica y monitorea las especies exóticas invasoras, en base al listado descrito en el diagnóstico.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A024",
      "link": "https://ciruelacertificada.cl/?s=A024&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "13",
        "91",
        "226",
        "361"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Son válidos los siguientes documentos: * Mapa que identifique zonas con vegetación nativa. * Registro del comparativo de las fotografías de estado inicial con respecto a la situación actual.",
      "action": "La planta mantiene áreas de conservación con vegetación nativa en zonas productivas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A025",
      "link": "https://ciruelacertificada.cl/?s=A025&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "92",
        "227",
        "362"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de señalética con medidas de protección de la fauna silvestre respecto a: - No cazar, matar, pescar o recolectar animales con prohibición según la legislación. - No retener la vida silvestre en cautiverio. - No realizar labores de limpieza de zanjas o poda de corta vientos en época de anidación de aves. - Limitar el libre movimiento de animales domésticos en áreas de producción. - Protocolo de acción en el caso de encontrar una especie nativa herida.",
      "action": "La planta implementa medidas para proteger especies de fauna silvestre.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A026",
      "link": "https://ciruelacertificada.cl/?s=A026&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "7",
        "8",
        "9",
        "10",
        "93",
        "228",
        "363"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo de reforestación que incluya medidas de cuidado de árboles reforestados.",
      "action": "La planta implementa procedimientos de reforestación o replantación, en caso de ser requerida la remoción de árboles dentro de la misma explotación. Esta reforestación debe realizarse con especies nativas de bajo requerimiento hídrico.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A027",
      "link": "https://ciruelacertificada.cl/?s=A027&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "94",
        "229",
        "364"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registros de control de calidad a la ciruela precosecha, durante el secado (en cancha) y al ingreso a la planta, midiendo los siguientes parámetros: - Grados brix, firmeza y porcentaje de color. - Diámetro. - Humedad de la fruta (sólo fruta seca). - Identificación de daños.",
      "action": "La planta implementa procesos de control de calidad a la fruta utilizada en el proceso de elaboración de la ciruela deshidratada.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A028",
      "link": "https://ciruelacertificada.cl/?s=A028&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "95",
        "230",
        "365"
      ],
      "good_practice": "Controlar la calidad de insumos y materias primas",
      "verification_type": "Bitácora"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro de recepción de materias primas verificando el cumplimiento de las especificaciones técnicas: - En el caso de envases y embalajes: medidas, colores, tipo de material, gramaje. - En el caso de ingredientes: condiciones microbiológicas.",
      "action": "La planta implementa procesos de control de calidad a todos los insumos y materias primas utilizadas dentro del proceso.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A029",
      "link": "https://ciruelacertificada.cl/?s=A029&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "96",
        "231",
        "366"
      ],
      "good_practice": "Controlar la calidad de insumos y materias primas",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Documento que dé cuenta de al menos uno de los siguientes registros: - Registro de auditorías a proveedores. - Registro de certificaciones al día de proveedores.",
      "action": "La planta solicita a sus empresas proveedoras de insumos de envase y embalaje, que realice controles de calidad de sus productos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A030",
      "link": "https://ciruelacertificada.cl/?s=A030&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "97",
        "232",
        "367"
      ],
      "good_practice": "Controlar la calidad de insumos y materias primas",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Documento que dé cuenta de al menos uno de los siguientes registros: - Registro de certificaciones al día de proveedores. - Copia de la resolución sanitaria de la empresa proveedora o implementación de HACCP.",
      "action": "La planta solicita a sus empresas proveedoras de ingredientes que son adicionados al producto (sorbato de potasio o aceites), que realicen controles de calidad a sus productos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A031",
      "link": "https://ciruelacertificada.cl/?s=A031&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "98",
        "233",
        "368"
      ],
      "good_practice": "Controlar la calidad de insumos y materias primas",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo de limpieza, revisión y reparación de materiales.",
      "action": "La planta cuenta con protocolo de limpieza y se asegura de que los materiales que son reutilizados (bandejas de madera para secado, bins, carros de metal para bandejas, cajas de cartón y perimetrales), sean limpiados, reparados y revisados para su reingreso a producción.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A032",
      "link": "https://ciruelacertificada.cl/?s=A032&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "99",
        "234",
        "369"
      ],
      "good_practice": "Controlar la calidad de insumos y materias primas",
      "verification_type": ""
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Registro de aplicación de productos en planta (sorbato de potasio y aceites vegetales), identificando los siguientes puntos: - Producto y su trazabilidad (lote). - Fase de la producción. - Fecha de aplicación. - Dosis aplicada.",
      "action": "La planta respeta los niveles máximos de sorbato de potasio u otro insumo utilizado durante el proceso de secado o tiernizado, respetando los límites establecidos y en base a los requerimientos de los mercados de destino.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A033",
      "link": "https://ciruelacertificada.cl/?s=A033&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "100",
        "235",
        "370",
        "511"
      ],
      "good_practice": "Respetar los niveles máximos residuales",
      "verification_type": "Bitácora"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Estudio de pre factibilidad. (La empresa externa que lo realice, debe entregar un informe que certifique las acciones realizadas para desarrollar lo solicitado).",
      "action": "La planta evalúa la factibilidad técnica y económica de utilizar envases reciclables o reutilizables, de acuerdo a una evaluación previa de sus productos o procesos, en busca de la mejora continua en aspectos de sustentabilidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A034",
      "link": "https://ciruelacertificada.cl/?s=A034&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "101",
        "236",
        "371"
      ],
      "good_practice": "Utilizar empaques sustentables",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Ficha técnica del insumo según especificaciones técnicas entregadas por el proveedor (Gramaje, % de insumos reciclables y tipo de material).",
      "action": "La planta utiliza, en los empaques que no están en contacto directo con el producto, materiales reutilizables o reciclables. Dichos empaques poseen, al menos, una de las siguientes características: - Material reciclable. - Material reutilizable. - Material reciclado post consumidor. -Material biodegradable. -Material compostable.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A035",
      "link": "https://ciruelacertificada.cl/?s=A035&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "102",
        "237",
        "372"
      ],
      "good_practice": "Utilizar empaques sustentables",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Ficha técnica del insumo según especificaciones técnicas entregadas por el proveedor (Gramaje, % de insumos reciclables y tipo de material).",
      "action": "La planta utiliza, en los empaques que estén en contacto directo con el producto, materiales reutilizables o reciclables. Dichos empaques poseen, al menos, una de las siguientes características: - Material reciclable. - Material reutilizable. - Material reciclado post consumidor. -Material biodegradable. -Material compostable.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A036",
      "link": "https://ciruelacertificada.cl/?s=A036&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "103",
        "238",
        "373"
      ],
      "good_practice": "Utilizar empaques sustentables",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro actualizado que contiene la siguiente información: - Identificación del tipo de residuo o agente contaminante. - Identificación de la cantidad producida mensualmente. - Identificación de los residuos peligrosos. - Ubicación dentro de la planta. - Destino del residuo (reciclaje, reúso, eliminación, etc.).",
      "action": "La planta identifica los residuos sólidos generados y las posibles fuentes de contaminación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A037",
      "link": "https://ciruelacertificada.cl/?s=A037&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "18",
        "104",
        "239",
        "374"
      ],
      "good_practice": "Contar con un plan de manejo de residuos",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Plan de manejo de residuos que contenga los siguientes contenidos: - Protocolos de almacenamiento de residuos peligrosos. - Manejo de residuos para reciclaje o reutilización. - Medidas de mitigación en caso de contaminación. - Descripción del proceso y los puntos en que se generan residuos. - Procedimientos internos para recoger y almacenar los residuos. - Identificación de alternativas de minimización, valorización y eliminación de residuos.",
      "action": "La planta ha generado y documentado un plan de manejo de residuos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A038",
      "link": "https://ciruelacertificada.cl/?s=A038&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "105",
        "240",
        "375"
      ],
      "good_practice": "Contar con un plan de manejo de residuos",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual del área de almacenamiento, corroborando que los residuos se encuentren dentro de los contenedores correspondientes, evitando el contacto directo con el suelo, con el objetivo de no generar contaminación (ejemplo: radier y techo).",
      "action": "La planta manipula los residuos (sólidos y/o líquidos) de manera tal, que no generen derrames que contaminen el suelo y/o el agua.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A039",
      "link": "https://ciruelacertificada.cl/?s=A039&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "106",
        "241",
        "376"
      ],
      "good_practice": "Minimizar la contaminación derivada de la gestión de los residuos",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo que cuente con las siguientes medidas para minimizar la contaminación: - No se permite la quema ni incineración de los desechos derivados de la producción. - Los caminos son pavimentados o se aplica un suspensor de polvo químico o gravilla para evitar el aumento de la polución. - Se realiza mantención a los equipos que utilizan combustibles fósiles internos, para evitar contaminación debido a fallas mecánicas.",
      "action": "La planta implementa un protocolo para minimizar la contaminación atmosférica por material particulado al interior de sus dependencias.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A040",
      "link": "https://ciruelacertificada.cl/?s=A040&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "4",
        "107",
        "242",
        "377"
      ],
      "good_practice": "Minimizar la contaminación derivada de la gestión de los residuos",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de señaléticas en lugares de riesgo de contaminación, que contemplen los siguientes elementos: - Información sobre acciones de mitigación inmediata. - Información de contacto con servicios de emergencia y autoridades locales.",
      "action": "La planta cuenta con un protocolo establecido para las situaciones de emergencia por contaminación por derrames de residuos líquidos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A041",
      "link": "https://ciruelacertificada.cl/?s=A041&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "14",
        "108",
        "243",
        "378"
      ],
      "good_practice": "Minimizar la contaminación derivada de la gestión de los residuos",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta capacita a su personal en la implementación del protocolo de gestión de emergencias por contaminación por derrames de residuos líquidos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A042",
      "link": "https://ciruelacertificada.cl/?s=A042&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "45",
        "109",
        "244",
        "379"
      ],
      "good_practice": "Minimizar la contaminación derivada de la gestión de los residuos",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Documento con certificado de autocontrol otorgado por el Sistema de Fiscalización de Norma de Emisión de Residuos Industriales Líquidos, de la Superintendencia del Medio Ambiente (SMA). (https://portalvu.mma.gob.cl/).",
      "action": "La planta registra periódicamente la generación y tratamiento de RILES.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A043",
      "link": "https://ciruelacertificada.cl/?s=A043&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "110",
        "245",
        "380"
      ],
      "good_practice": "Gestionar adecuadamente los residuos derivados de la producción",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de zona de almacenamiento de residuos peligrosos.",
      "action": "La planta almacena los residuos peligrosos, (por ejemplo: los aceites lubricantes derivados de vehículos y maquinarias utilizadas en la explotación), en bodegas exclusivas para este tipo de material.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A044",
      "link": "https://ciruelacertificada.cl/?s=A044&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "111",
        "246",
        "381"
      ],
      "good_practice": "Gestionar adecuadamente los residuos derivados de la producción",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro actualizado que contiene la siguiente información: - Identificación del tipo de residuo o agente contaminante. - Identificación de la cantidad producida mensualmente. - Identificación de los residuos peligrosos. - Ubicación dentro de la planta. - Destino del residuo, con autorización sanitaria (reciclaje, reúso, etc.).",
      "action": "La planta lleva registro de los residuos peligrosos generados, siendo manipulados y desechados, por ejemplo: - Aceites lubricantes. - Envases y recipientes con residuos de detergentes, desinfectantes o productos químicos de procesos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A045",
      "link": "https://ciruelacertificada.cl/?s=A045&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "112",
        "247",
        "382"
      ],
      "good_practice": "Gestionar adecuadamente los residuos derivados de la producción",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro actualizado que contiene la siguiente información: - Identificación del tipo de residuo o agente contaminante. - Identificación de la cantidad producida mensualmente. - Identificación de los residuos. - Ubicación dentro de la planta. - Destino del residuo (reciclaje, reúso, etc.).",
      "action": "La planta registra el volumen de biosólidos generados.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A046",
      "link": "https://ciruelacertificada.cl/?s=A046&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "113",
        "248",
        "383"
      ],
      "good_practice": "Gestionar adecuadamente los residuos derivados de la producción",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de áreas de segregación de aguas lluvia.",
      "action": "La planta segrega las aguas lluvias de las aguas derivadas de la producción, con el fin de disminuir el caudal de entrada al sistema de recepción de RILES.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A047",
      "link": "https://ciruelacertificada.cl/?s=A047&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "114",
        "249",
        "384"
      ],
      "good_practice": "Gestionar adecuadamente los residuos derivados de la producción",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Informe que certifique el retiro y la posterior reutilización de los residuos, realizado por la empresa autorizada a cargo de la gestión.",
      "action": "La planta gestiona los residuos de aceites lubricantes derivados de vehículos y maquinarias utilizadas en la empresa, a través de empresas especializadas en su posterior valorización.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A048",
      "link": "https://ciruelacertificada.cl/?s=A048&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "115",
        "250",
        "385"
      ],
      "good_practice": "Gestionar adecuadamente los residuos derivados de la producción",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de la existencia de contenedores y señaléticas informativas con respecto a la gestión de los residuos de reciclaje de: - PET y otros plásticos. - Tetra brik. - Papeles y cartones. - Vidrios. - Latas y otros metales. - Residuos peligrosos. - Residuos no reciclables.",
      "action": "La planta disminuye sus residuos enviados a gestores autorizados a través de la segregación, almacenamiento y entrega para su valorización, basándose en sus características y en las opciones de reciclaje disponibles.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A049",
      "link": "https://ciruelacertificada.cl/?s=A049&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "15",
        "16",
        "17",
        "116",
        "251",
        "386"
      ],
      "good_practice": "Gestionar residuos inorgánicos a través de técnicas de valorización y reciclaje",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Documentación de ejecución de capacitaciones (lista de asistencia identificando sexo del participante, tema expuesto, expositor, material expuesto). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta capacita a su personal sobre la relevancia del reciclaje y los procedimientos apropiados para su implementación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A050",
      "link": "https://ciruelacertificada.cl/?s=A050&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "46",
        "117",
        "252",
        "387"
      ],
      "good_practice": "Gestionar residuos inorgánicos a través de técnicas de valorización y reciclaje",
      "verification_type": "Foto"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro actualizado que contiene la siguiente información: - Identificación del tipo de residuo orgánico. - Identificación de la cantidad producida mensualmente. - Ubicación dentro de la planta. - Destino del residuo (reciclaje, reúso, etc.).",
      "action": "La planta reutiliza la materia orgánica generada en sus procesos, a través de una de las siguientes técnicas: - Compostaje. - Lombricultura. - Biomasa Carozo para la combustión de calderas en el proceso de tiernizado. - Venta o donación a otras explotaciones.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A051",
      "link": "https://ciruelacertificada.cl/?s=A051&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "118",
        "253",
        "388"
      ],
      "good_practice": "Compostar la materia orgánica generada utilizando el compost en su actividad productiva",
      "verification_type": "Bitácora"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro de consumo energético actualizado mensualmente que contenga la siguiente información: - Tipo de fuente de energía. Eléctrica, gas (natural y/o licuado), combustible (diésel, bencina, kerosene), leña, carbón, entre otros. - Consumo energético mensual (kWh). - Gasto en energía ($/mes).",
      "action": "La planta establece un sistema de registro mensual del consumo de energía.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A052",
      "link": "https://ciruelacertificada.cl/?s=A052&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "25",
        "119",
        "254",
        "389"
      ],
      "good_practice": "Implementar un sistema de gestión de la energía",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta implementa un plan de capacitación para los trabajadores, abordando la gestión eficiente de la energía.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A053",
      "link": "https://ciruelacertificada.cl/?s=A053&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "47",
        "120",
        "255",
        "390"
      ],
      "good_practice": "Implementar un sistema de gestión de la energía",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Reporte de diagnóstico energético con levantamiento de información para la identificación de consumo cuenta con: - Registros mensuales de consumo energético. - Identificación de equipos y su consumo energético. (Identificar las áreas críticas en cuanto a consumo). - Identificación de períodos de alto consumo energético por mes (estacional o continuo).. - Registro de mantenimiento de equipos. - Definición del indicador de consumo en base a la producción. - Identificación de capacitaciones en el ámbito de energía. - Identificación de oportunidades de mejora y costos, tiempo de implementación, necesidades adicionales (construcción, capacitación, remodelación, entre otras). En el caso de que lo haga una empresa externa, ésta deberá entregar un informe que certifique las acciones realizadas para entregar el diagnóstico.",
      "action": "La planta cuenta con un diagnóstico energético actualizado.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A054",
      "link": "https://ciruelacertificada.cl/?s=A054&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "23",
        "121",
        "256",
        "391"
      ],
      "good_practice": "Implementar un sistema de gestión de la energía",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Documento con un sistema de gestión de la energía que considere la siguiente información: * Determinación del alcance del sistema de gestión de la energía. * Línea de base energética a través de un indicador de eficiencia energética indicando el año de la línea base (kWh /kilo de fruta seca). * Una meta de intensidad energética.",
      "action": "La planta implementa un sistema de gestión de la energía.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A055",
      "link": "https://ciruelacertificada.cl/?s=A055&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "24",
        "122",
        "257",
        "392"
      ],
      "good_practice": "Implementar un sistema de gestión de la energía",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de señaléticas de uso eficiente de energía en espacios de trabajo con la siguiente información: - Apaga la luz antes de salir. - Cierra la puerta al salir. - Notificar fugas de vapor. - Recordar mantenciones preventivas. - Regular el consumo de agua caliente.",
      "action": "La planta cuenta con señalética que promueve el uso eficiente de la energía.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A056",
      "link": "https://ciruelacertificada.cl/?s=A056&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "20",
        "21",
        "22",
        "123",
        "258",
        "393"
      ],
      "good_practice": "Implementar medidas de eficiencia energética relacionadas al plan de gestión",
      "verification_type": "Foto"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Fichas técnicas de los equipos, maquinarias o piezas que especifiquen el registro de potencia en cada caso.",
      "action": "La planta adquiere equipos industriales o maquinarias o, sustituye sus piezas por otras que presenten un bajo consumo energético o que incorporen el modo ahorro de energía.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A057",
      "link": "https://ciruelacertificada.cl/?s=A057&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "124",
        "259",
        "394"
      ],
      "good_practice": "Implementar medidas de eficiencia energética relacionadas al plan de gestión",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de señaléticas en área de guardado de vehículos que apunten a las siguientes medidas. - Control de la presión de los neumáticos. - Reducción del peso de la carga en los vehículos. - Conducción eficiente a velocidades inferiores a 20 km/h. - Combina viajes y evita los que son innecesarios. - Conduce suavemente, evitando aceleraciones y frenadas bruscas. - Condiciones climáticas: El viento en contra y las temperaturas extremas pueden aumentar el consumo de combustible.",
      "action": "La planta implementa medidas para mejorar la eficiencia de los vehículos dentro de la explotación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A058",
      "link": "https://ciruelacertificada.cl/?s=A058&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "19",
        "125",
        "260",
        "395"
      ],
      "good_practice": "Implementar medidas de eficiencia energética relacionadas al plan de gestión",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Son válidos los siguientes documentos: * Check list de mantenimiento de equipos. * Registro de mantenimiento de equipos. * Bitácora de mantención. * Plan de mantenimiento de equipos, maquinarias y vehículos. En el caso de que esta labor la realice una empresa externa, debe existir un contrato e informe que acredite la realización de las actividades mencionadas.",
      "action": "La planta realiza mantención de equipos, maquinarias y vehículos, una vez durante la temporada o más frecuentemente si las indicaciones del fabricante lo estipulan, asegurando un adecuado funcionamiento y uso eficiente de la energía.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A059",
      "link": "https://ciruelacertificada.cl/?s=A059&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "5",
        "126",
        "261",
        "396"
      ],
      "good_practice": "Implementar medidas de eficiencia energética relacionadas al plan de gestión",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Plan de mantenimiento elaborado que incorpore al menos las siguientes medidas: - Utiliza luminaria de bajo consumo energético. - Limpia las luminarias y ampolletas periódicamente. - Tipos de luminarias a adquirir en caso de reemplazo.",
      "action": "La planta implementa un plan de mantenimiento de luminarias, para gestionar eficientemente la iluminación dentro del recinto.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A060",
      "link": "https://ciruelacertificada.cl/?s=A060&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "127",
        "262",
        "397"
      ],
      "good_practice": "Implementar medidas de eficiencia energética relacionadas al plan de gestión",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Documento con estudio de prefactibilidad técnico económica. En el caso de que lo haga una empresa externa, esta debe entregar un informe que certifique que las acciones realizadas estén en función de lo solicitado.",
      "action": "La planta evalúa la prefactibilidad técnica y económica de incorporar energías renovables dentro de su sistema productivo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A061",
      "link": "https://ciruelacertificada.cl/?s=A061&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "128",
        "263",
        "398"
      ],
      "good_practice": "Implementar sistemas de energías renovables",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de alguno de los siguientes tipos de energía: - Energía solar. - Eólica. - Mini hidroeléctrica. - Biomasa o biogás.",
      "action": "La planta utiliza sistemas de energía renovable para autoconsumo energético",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A062",
      "link": "https://ciruelacertificada.cl/?s=A062&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "129",
        "264",
        "399"
      ],
      "good_practice": "Implementar sistemas de energías renovables",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de emisiones y capturas que incluya, fecha, monitoreo, periodo, balance de los siguientes aspectos: Emisiones directas de GEI • Combustión estacionaria • Combustión Móvil • Uso suelo, cambios en el uso de suelo y Silvicultura • Procesos industriales • Emisiones fugitivas Emisiones indirectas de GEI causadas por energía importada • Electricidad importada • Otra energía importada y/o pérdidas T&D Otras emisiones indirectas de GEI • Transporte • Bienes y servicios utilizados • Uso de productos de la organización *Se recomienda el uso de la plataforma de Huella Chile para cuantificar emisiones. En el caso de que lo haga una empresa externa, esta debe entregar un informe que certifique que las acciones realizadas estén en función de lo solicitado.",
      "action": "La planta cuantifica sus emisiones directas e indirectas de GEI de la unidad y define una línea base en las principales etapas de su producción.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A063",
      "link": "https://ciruelacertificada.cl/?s=A063&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "26",
        "29",
        "130",
        "265",
        "400"
      ],
      "good_practice": "Cuantificar emisiones de GEI en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Reporte anual de emisiones y capturas, con indicación de la metodología empleada y los resultados obtenidos. En el caso de que lo haga una empresa externa, esta debe entregar un informe que certifique que las acciones realizadas estén en función de lo solicitado.",
      "action": "La planta monitorea periódicamente los GEI de la unidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A064",
      "link": "https://ciruelacertificada.cl/?s=A064&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "27",
        "30",
        "131",
        "266",
        "401"
      ],
      "good_practice": "Cuantificar emisiones de GEI en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta implementa un plan de capacitación para las personas que trabajan en ella, abordando la problemática asociada al cambio climático y conceptos sobre cuantificación y mitigación de emisión de GEI.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A065",
      "link": "https://ciruelacertificada.cl/?s=A065&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "48",
        "132",
        "267",
        "402"
      ],
      "good_practice": "Reducir las emisiones y promover las capturas de GEI en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo para reducir las emisiones de GEI.",
      "action": "La planta cuenta con un protocolo para reducir sus emisiones de GEI que contempla, por ejemplo, alguna de las siguientes medidas: • Cambiar el sistema de calefacción de caldera de petróleo por gas natural o biogás. • Instalar paneles solares térmicos para el precalentamiento del agua utilizada en el procesamiento de ciruelas. • Implementar luminarias LED de bajo consumo con automatización. • Mejorar el aislamiento térmico en paredes y techos para reducir pérdidas de calor. • Establecer un plan de mantención preventiva de maquinaria y equipos. • Reemplazar montacargas y vehículos de transporte por modelos eléctricos de bajas emisiones.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A066",
      "link": "https://ciruelacertificada.cl/?s=A066&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "28",
        "133",
        "268",
        "403"
      ],
      "good_practice": "Reducir las emisiones y promover las capturas de GEI en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Plan de reducción, control y respuesta frente a riesgos de desastres, vinculados al Cambio Climático que contenga al menos la siguiente información: * Listado de las amenazas o peligros (internas y externas) según su origen, y evaluación de recursos y vulnerabilidades para enfrentar cada una de ellas * Programas de trabajo en sus fases de prevención, respuesta y recuperación. * Definición de responsables y de mecanismos para asignación de recursos que financien los programas de trabajo que surjan del plan. * Realización de simulaciones y simulacros. El plan debe ser evaluado posterior a la ocurrencia de cada evento de emergencia o desastre.",
      "action": "La planta elabora e implementa un plan de reducción, control y respuesta frente a riesgo de desastres, vinculados al Cambio Climático. La elaboración del plan contempla determinar las amenazas históricas y proyectadas, identificar los recursos mínimos y capacidades para abordar las amenazas, y determinar las debilidades respecto de los recursos y capacidades requeridas. Las medidas del plan se elaboran en función de las debilidades detectadas y su respectiva priorización.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A067",
      "link": "https://ciruelacertificada.cl/?s=A067&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "134",
        "269",
        "404"
      ],
      "good_practice": "Elaborar un plan de reducción de riesgos de desastres",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de eventos meteorológicos significativos, indicando la fuente de obtención de la información (estación meteorológica propia o datos de portales como http://agroclima.cl/ o https://agrometeorologia.cl/ , de los siguientes puntos: * Altas temperaturas (más de 30°C). * Bajas temperaturas (menos de 4°C). * Lluvias. * Fuente de obtención de la información. Este registro debe ser actualizado de manera mensual.",
      "action": "La planta incorpora monitoreo de parámetros de la situación meteorológica propia o cercana, para visualizar episodios extremos de sequías extremas, altas y bajas temperaturas, y episodios de alta pluviometría.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A068",
      "link": "https://ciruelacertificada.cl/?s=A068&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "135",
        "270",
        "405"
      ],
      "good_practice": "Elaborar un plan de reducción de riesgos de desastres",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta capacita al personal sobre el un plan de reducción, control y respuesta frente a riesgo de desastres, vinculados al Cambio Climático, para evitar que sean susceptibles a sufrir daños o pérdidas por efecto de las amenazas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A069",
      "link": "https://ciruelacertificada.cl/?s=A069&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "136",
        "271",
        "406"
      ],
      "good_practice": "Elaborar un plan de reducción de riesgos de desastres",
      "verification_type": "Foto"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Calidad",
      "verification_detail": "Protocolo de acciones de control de calidad realizadas en la planta.",
      "action": "La planta identifica y gestiona de manera eficiente, los principales Puntos Críticos de Control (PCC) asociados a la producción de ciruelas deshidratadas. Se deben considerar, al menos, los siguientes puntos: - Identificar el producto. - Describir el producto y el uso previsto, incluidas instrucciones de procesamiento validadas. - Listar materias primas/ingredientes. - Incluir un diagrama de flujo del proceso (con los PCC identificados). - Incluir un análisis de peligros de materias primas, productos y procesos. - Describir el objetivo y los límites críticos del PCC. - Describir el seguimiento y la frecuencia de los PCC. - Detallar acciones correctivas para cada PCC.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A070",
      "link": "https://ciruelacertificada.cl/?s=A070&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "137",
        "272",
        "407"
      ],
      "good_practice": "Poseer una política de calidad y de mejora continua en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Protocolo de gestión de calidad que detalle los procesos realizados para cumplir los requisitos de seguridad, legalidad y calidad del producto",
      "action": "La planta establece un procedimiento de gestión de la calidad en la recepción de la materia prima y en las etapas del proceso productivo y el producto final.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A071",
      "link": "https://ciruelacertificada.cl/?s=A071&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "138",
        "273",
        "408"
      ],
      "good_practice": "Poseer una política de calidad y de mejora continua en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta posee un procedimiento de gestión de la calidad conocida por las personas que trabajan en ella.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A072",
      "link": "https://ciruelacertificada.cl/?s=A072&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "49",
        "139",
        "274",
        "409"
      ],
      "good_practice": "Poseer una política de calidad y de mejora continua en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Registro que evidencie las vías de comunicación con clientes y consumidores, ya sea de manera física (empaques) o digital (página web), para el envío de sugerencias y reclamos.",
      "action": "La planta establece canales de comunicación directos, para recibir y responder de manera oportuna los reclamos de clientes y consumidores.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A073",
      "link": "https://ciruelacertificada.cl/?s=A073&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "140",
        "275",
        "410"
      ],
      "good_practice": "Poseer una política de calidad y de mejora continua en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Comprobante de auditoría interna, que permita verificar que se cumple con los requisitos de las certificaciones aplicables (con su respectiva periodicidad).",
      "action": "La planta gestiona sus auditorías internas en base a los riesgos asociados, para evaluar el nivel de cumplimiento de su política de gestión de calidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A074",
      "link": "https://ciruelacertificada.cl/?s=A074&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "141",
        "276",
        "411"
      ],
      "good_practice": "Poseer una política de calidad y de mejora continua en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Documento de registro con la siguiente información: - Fecha. - Total de producto seco recolectado al día. - Tipo de secado. - Tiempo de almacenamiento máximo de producto seco. - Total de producto tiernizado elaborado al día. - Total de producto empacado al día. - Tipo de empaque. - Mercado de destino.",
      "action": "La planta mantiene registros de todo el producto seco y tiernizado elaborado.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A075",
      "link": "https://ciruelacertificada.cl/?s=A075&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "142",
        "277",
        "412"
      ],
      "good_practice": "Documentar los procesos productivos realizados en la planta",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Registro con la siguiente información: - Labor. - Fase de la línea de proceso. - Fecha y hora de ejecución. - Persona responsable de su ejecución.",
      "action": "La planta registra todas las labores productivas realizadas y la persona responsable de su ejecución.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A076",
      "link": "https://ciruelacertificada.cl/?s=A076&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "31",
        "143",
        "278",
        "413"
      ],
      "good_practice": "Documentar los procesos productivos realizados en la planta",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Registro diario con la siguiente información: - Volumen y procedencia de la fruta de la fase de producción primaria. - Tipo y cantidad de conservantes utilizados (sorbato de potasio). - Tipo y cantidad de material de embalaje utilizado.",
      "action": "La planta registra el consumo de materias primas, ingredientes e insumos utilizados para el procesamiento.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A077",
      "link": "https://ciruelacertificada.cl/?s=A077&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "144",
        "279",
        "414"
      ],
      "good_practice": "Documentar los procesos productivos realizados en la planta",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Protocolo del proceso de trazabilidad en la empresa que cuente con los siguientes aspectos: - Identificación de predio o proveedor de materia prima. - Identificación del tipo de secado. - Calibre. - % de humedad. - Despepitado. - Dosis de conservante adicionado. - Mercado de destino.",
      "action": "La planta establece políticas y procedimientos documentados para garantizar que todos los ingredientes, auxiliares tecnológicos, productos acabados y envases de los productos (interiores y exteriores) puedan rastrearse desde la producción hasta la distribución, a través de un protocolo de trazabilidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A078",
      "link": "https://ciruelacertificada.cl/?s=A078&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "145",
        "280",
        "415"
      ],
      "good_practice": "Poseer un sistema de trazabilidad del producto a lo largo de todas sus etapas de producción",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Registro que evidencie la presencia del N° de lote en el producto terminado, ya sea en el paquete o en la etiqueta del producto.",
      "action": "La planta asegura que sus productos elaborados posean un código (N° de lote), que le permita rastrear la cantidad producida, enviada y desperdiciada; ubicación del material; y fechas de producción y envío.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A079",
      "link": "https://ciruelacertificada.cl/?s=A079&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "146",
        "281",
        "416"
      ],
      "good_practice": "Poseer un sistema de trazabilidad del producto a lo largo de todas sus etapas de producción",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Registro del diagrama de flujo disponible ya sea en formato físico o digital.",
      "action": "La planta posee un diagrama de flujo del proceso productivo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A080",
      "link": "https://ciruelacertificada.cl/?s=A080&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "147",
        "282",
        "417"
      ],
      "good_practice": "Poseer protocolos logísticos que faciliten la gestión del proceso productivo",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Registro con el N° de la guía de despacho que contenga la siguiente información: - Fecha despacho. - Tipo de producto (condición natural o tiernizado). - Calibre. - Tipo de empaque. - Documentación legal del mercado de destino. - Autorización de la autoridad fitosanitaria (SAG), al momento de cargar el contenedor.",
      "action": "La planta implementa un procedimiento que asegure el adecuado despacho del producto final.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A081",
      "link": "https://ciruelacertificada.cl/?s=A081&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "148",
        "283",
        "418"
      ],
      "good_practice": "Poseer protocolos logísticos que faciliten la gestión del proceso productivo",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Son válidos los siguientes documentos: * Check listo o registro de labores de mantención ejecutadas en planta. * Inventario actualizado mensualmente.",
      "action": "La planta optimiza el proceso de elaboración del producto final, a través de las siguientes medidas: - Realiza mantención y calibración de los equipos de las líneas de proceso anualmente o según las indicaciones del fabricante, en el caso de que requiera mantención con mayor frecuencia. - Maneja adecuadamente los inventarios de insumos, materias primas y producto terminado.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A082",
      "link": "https://ciruelacertificada.cl/?s=A082&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "6",
        "149",
        "284",
        "419"
      ],
      "good_practice": "Poseer protocolos logísticos que faciliten la gestión del proceso productivo",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Calidad",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta capacita a las personas que trabajan en ella sobre seguridad e higiene de los alimentos basada en el Codex y las regulaciones nacionales aplicables.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A083",
      "link": "https://ciruelacertificada.cl/?s=A083&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "50",
        "150",
        "285",
        "420"
      ],
      "good_practice": "Poseer una política de inocuidad para la producción",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Inspección visual de las señaléticas con las siguientes temáticas: - Procedimientos de limpieza. - Manipulación de alimentos (lavado de manos, contaminación por agentes externos). - Uso de ropa de trabajo adecuada (cofia, calzado protector, delantal, etc.) y libre de accesorios.",
      "action": "La planta utiliza señaléticas para promover sus prácticas sobre higiene e inocuidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A084",
      "link": "https://ciruelacertificada.cl/?s=A084&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "32",
        "60",
        "61",
        "151",
        "286",
        "421"
      ],
      "good_practice": "Poseer una política de inocuidad para la producción",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Plan de análisis de riesgos, documentado para las materias primas, ingredientes, auxiliares tecnológicos y materiales de envasado que contenga, al menos la siguiente información: - Determinar puntos críticos de control. - Establecer límites críticos. - Establecer procedimientos de monitoreo. - Establecer medidas correctivas. - Establecer procedimientos de comprobación auditables. El plan debe ser revisado, al menos, una vez al año si se producen cambios en el producto o en el proceso.",
      "action": "La planta establece, implementa, documenta y mantiene un sistema de seguridad y calidad alimentaria, para proteger el suministro de alimentos de los peligros biológicos, químicos y físicos, con el fin de evitar la contaminación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A085",
      "link": "https://ciruelacertificada.cl/?s=A085&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "152",
        "287",
        "422"
      ],
      "good_practice": "Poseer una política de inocuidad para la producción",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Calidad",
      "verification_detail": "Comprobante de auditoría interna que permita verificar que se cumple con los requisitos de inocuidad, demostrando su capacidad para cumplir con los mismos mediante procesos documentados, medidas de control y resultados de sus auditorías realizadas, al menos, una vez por año.",
      "action": "La planta realiza auditorías internas anuales para evaluar el nivel de cumplimiento de su política de inocuidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A086",
      "link": "https://ciruelacertificada.cl/?s=A086&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "153",
        "288",
        "423"
      ],
      "good_practice": "Poseer una política de inocuidad para la producción",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Registro que acredite la utilización del servicio básico de agua potable en la planta.",
      "action": "La planta utiliza agua potable cuando esta es un ingrediente del producto final.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A087",
      "link": "https://ciruelacertificada.cl/?s=A087&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "154",
        "289",
        "424"
      ],
      "good_practice": "Utilizar agua con condiciones microbiológicas adecuadas para la producción",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Calidad",
      "verification_detail": "Informe periódicos de análisis con requisitos físicos, químicos, bacteriológicos y de desinfección establecidos en la Norma NCH 409/1.",
      "action": "La planta realiza análisis microbiológicos al agua que se encuentra en contacto con el producto, durante su procesamiento.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A088",
      "link": "https://ciruelacertificada.cl/?s=A088&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "155",
        "290",
        "425"
      ],
      "good_practice": "Utilizar agua con condiciones microbiológicas adecuadas para la producción",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Inspección visual del N° de la Resolución Sanitaria con fecha de otorgamiento, entregado por el servicio de salud del ambiente.",
      "action": "La planta se asegura de que sus instalaciones, interiores y exteriores posean una adecuada construcción y limpieza acorde con los requerimientos de seguridad e higiene de los alimentos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A089",
      "link": "https://ciruelacertificada.cl/?s=A089&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "156",
        "291",
        "426"
      ],
      "good_practice": "Asegurar la adecuada limpieza de espacios, equipos e indumentarias requeridas para la producción",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Se consideran válidos alguno siguientes documentos. - Registro de lavado de indumentaria de trabajo en la planta, que evidencie su lavado semanal. - Check list de higiene del personal, donde diariamente se va evaluando la limpieza de la indumentaria entregada. - Convenio o contrato con empresa que se encargue del lavado de los uniformes. - Documento con el procedimiento de lavado entregado a las personas que trabajan en la planta.",
      "action": "La planta mantiene limpia y en buen estado, la indumentaria utilizada por el personal en contacto directo con el producto.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A090",
      "link": "https://ciruelacertificada.cl/?s=A090&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "157",
        "292",
        "427"
      ],
      "good_practice": "Asegurar la adecuada limpieza de espacios, equipos e indumentarias requeridas para la producción",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Protocolo de limpieza de superficies.",
      "action": "La planta asegura adecuados protocolos de limpieza de superficies en contacto directo con el producto elaborado, a través de las siguientes medidas: - Los utensilios destinados a la limpieza de superficies que estén en contacto directo con el producto, son utilizados únicamente con este fin y existe una diferenciación por color con utensilios similares utilizados en otros espacios. - Los productos químicos de limpieza son adecuados para el entorno de producción y no se utilizan productos de limpieza fenólicos o perfumados. - Se utiliza agua potable para la limpieza de equipos en contacto directo con el producto.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A091",
      "link": "https://ciruelacertificada.cl/?s=A091&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "158",
        "293",
        "428"
      ],
      "good_practice": "Asegurar la adecuada limpieza de espacios, equipos e indumentarias requeridas para la producción",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Registro de los insumos que dé cuenta de la siguiente información: - Nombre del producto. - Fecha de compra. - Número de lote y proveedor. - Unidades adquiridas. - Fecha de vencimiento y vida útil.",
      "action": "La planta se asegura de que los insumos, materias primas e ingredientes utilizados en el proceso productivo, no representen un riesgo para la inocuidad alimentaria.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A092",
      "link": "https://ciruelacertificada.cl/?s=A092&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "159",
        "294",
        "429"
      ],
      "good_practice": "Asegurar la inocuidad de los insumos utilizados",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Inspección visual de señaléticas de prohibición de las siguientes acciones: - Prohíbe fumar, comer y beber en áreas designadas para la producción. - Prohíbe la presencia de animales dentro de sus instalaciones.",
      "action": "La planta previene la contaminación de agentes externos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A093",
      "link": "https://ciruelacertificada.cl/?s=A093&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "59",
        "160",
        "295",
        "430"
      ],
      "good_practice": "Prevenir la contaminación durante el proceso productivo",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Procedimiento para gestionar los problemas de salud de quienes trabajan en la empresa, que incluya: - Registro de quienes se han presentado con alguna enfermedad transmisible. - Prohibición de labores ante sospecha de enfermedades contagiosas. - Procedimientos para la protección de las heridas.",
      "action": "La planta desarrolla procedimientos para gestionar las dificultades asociadas a enfermedades transmisibles, y quienes trabajan en ella, informan al personal encargado cuando presentan una enfermedad que pueda significar la contaminación del producto final.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A094",
      "link": "https://ciruelacertificada.cl/?s=A094&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "161",
        "296",
        "431"
      ],
      "good_practice": "Prevenir la contaminación durante el proceso productivo",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Inspección visual de instalaciones del personal.",
      "action": "La planta provee al personal de instalaciones adecuadas para evitar todo agente contaminante antes de ingresar a sus espacios de trabajo, mediante las siguientes medidas: - Vestuarios y baños separados del área de producción. - Estaciones de lavado de manos en todos los puntos de entrada al área de producción. - Áreas segregadas para comer fuera del área de producción. - Zonas para almacenar artículos personales que puedan suponer un riesgo de contaminación para el producto final (ej. relojes, teléfonos, joyería, monedas, medicamentos, entre otros).",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A095",
      "link": "https://ciruelacertificada.cl/?s=A095&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "162",
        "297",
        "432"
      ],
      "good_practice": "Prevenir la contaminación durante el proceso productivo",
      "verification_type": "Foto"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Gestión",
      "verification_detail": "Son válidos alguno de los siguientes documentos: - Contrato de servicios de una persona que realiza asesorías financieras. - Descripción de cargos y CV de la persona encargada del área financiera.",
      "action": "La planta cuenta con una persona encargada o una persona que realiza asesorías financieras.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A096",
      "link": "https://ciruelacertificada.cl/?s=A096&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "163",
        "298",
        "433"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad de la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Gestión",
      "verification_detail": "Documento de identificación de puntos críticos dentro de la planta.",
      "action": "La planta identifica los principales puntos críticos de su producción y busca mejoras para aumentar su productividad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A097",
      "link": "https://ciruelacertificada.cl/?s=A097&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "164",
        "299",
        "434"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad de la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Gestión",
      "verification_detail": "Son válidos alguno de los dos documentos enunciados a continuación: * Documento de evaluación del proyecto que posea al menos propuesta de TIR y VAN y decisión sobre la adopción de la nueva práctica o tecnología. * Registro de procedimiento, diseño y desarrollo del plan de implementación de la nueva tecnología. Adicionalmente, se requiere un listado con las inversiones implementadas, indicando la temática a la que corresponde (agua, energía, residuos, etc.).",
      "action": "La planta evalúa la adopción de nuevas prácticas o tecnologías, considerando su contribución a la productividad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A098",
      "link": "https://ciruelacertificada.cl/?s=A098&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "165",
        "300",
        "435"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad de la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Gestión",
      "verification_detail": "Documento de planificación que contenga los siguientes puntos: - Presupuesto. - Proyecciones de ventas. - Organigrama y descripción de cargos dentro de la empresa.",
      "action": "La planta cuenta con un plan de gestión para su productividad y rentabilidad, que le permite definir indicadores de gestión y asegurar su viabilidad a largo plazo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A099",
      "link": "https://ciruelacertificada.cl/?s=A099&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "166",
        "301",
        "436"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad de la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Gestión",
      "verification_detail": "Documentos de registro de los siguientes aspectos: - Inventario de productos entrantes y salientes. - Registro contable de la empresa.",
      "action": "La planta cuenta con un sistema de gestión contable que considera registros de inventario, control de gastos, ingresos y utilidades derivadas del proceso productivo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A100",
      "link": "https://ciruelacertificada.cl/?s=A100&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "167",
        "302",
        "437"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad de la planta",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Gestión",
      "verification_detail": "Registro de licencia o suscripción a plataforma digital específica para la gestión agrícola o industrial.",
      "action": "La planta cuenta con una herramienta de gestión digital que facilita la implementación de medidas y registros.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A101",
      "link": "https://ciruelacertificada.cl/?s=A101&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "168",
        "303",
        "438"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad de la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Gestión",
      "verification_detail": "Acta de reuniones realizadas con la “comunidad de práctica”.",
      "action": "La planta forma parte de una \"comunidad de práctica\" que le permite realizar una evaluación de cambio tecnológico, en conjunto con otras empresas de la industria a nivel territorial.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A102",
      "link": "https://ciruelacertificada.cl/?s=A102&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "57",
        "169",
        "304",
        "439"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad de la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Gestión",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada) o certificado de participación en instancias de capacitación externa (cursos, seminarios, congresos, etc.). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "Quienes trabajan como directivos o son tomadores de decisiones, participan en instancias de capacitación que les permiten entender de mejor manera, el comportamiento del mercado de ciruelas deshidratadas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A103",
      "link": "https://ciruelacertificada.cl/?s=A103&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "51",
        "170",
        "305",
        "440"
      ],
      "good_practice": "Gestionar la empresa para garantizar su viabilidad económica y financiera",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Gestión",
      "verification_detail": "Registro de planificación estratégica con una vigencia de máximo 5 años que contenga la siguiente información: - Diagnóstico que incorpore un FODA. - Plan de implementación en base a los resultados del FODA, (ventajas competitivas para potenciar fortalezas, evitar debilidades y enfrentar amenazas).",
      "action": "La planta desarrolla una visión empresarial y planifica y decide, en base a información robusta de índole económica y financiera.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A104",
      "link": "https://ciruelacertificada.cl/?s=A104&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "171",
        "306",
        "441"
      ],
      "good_practice": "Gestionar la empresa para garantizar su viabilidad económica y financiera",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Gestión",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta capacita a las personas que trabajan en ella sobre estrategias de aumento de la productividad, para que puedan identificar los puntos críticos del proceso y conozcan las herramientas de optimización de la producción.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A105",
      "link": "https://ciruelacertificada.cl/?s=A105&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "52",
        "172",
        "307",
        "442"
      ],
      "good_practice": "Fomentar que las personas tengan acceso a la información de productividad y mercado",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Gestión",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada) o certificado de participación en instancias de capacitación externa (cursos, seminarios, congresos, etc.). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta capacita sus directivos y tomadores de decisiones en finanzas, costos de producción y gestión del negocio agrícola.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A106",
      "link": "https://ciruelacertificada.cl/?s=A106&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "53",
        "173",
        "308",
        "443"
      ],
      "good_practice": "Fomentar que las personas tengan acceso a la información de productividad y mercado",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Matriz de mapeo de actores con la identificación de los impactos generados. • Nombre de la organización/institución, actor • Representante o contraparte • Cargo • Contacto • Categoría de actor (empresa, comercio, residentes, servicios locales, etc.). • Ubicación geográfica en el territorio • Relaciones predominantes con la empresa • Nivel de afectación (positiva y negativa) de las operaciones la empresa",
      "action": "La planta identifica los potenciales impactos, positivos o negativos, generados en las comunidades vecinas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A107",
      "link": "https://ciruelacertificada.cl/?s=A107&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "35",
        "187",
        "322",
        "444"
      ],
      "good_practice": "Evaluar el impacto generado en las comunidades locales",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Social",
      "verification_detail": "Matriz con las medidas de mitigación de impactos generados que dé cuenta de: • Efecto. • Acción. • Objetivo (fortalecer, prevenir, mitigar). • Resultado esperado.",
      "action": "La planta aplica medidas de mitigación para los impactos generados.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A108",
      "link": "https://ciruelacertificada.cl/?s=A108&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "36",
        "188",
        "323",
        "445"
      ],
      "good_practice": "Evaluar el impacto generado en las comunidades locales",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Social",
      "verification_detail": "Son válidos cualquiera de los documentos que se proponen a continuación. * Portafolio de evidencia de las actividades realizadas, ej. proyectos realizados, imágenes, registros de convenios, canales de comunicación, minutas. * Documentos que evidencien el tipo de iniciativa, la fecha, la ubicación, los montos y/o las horas profesionales invertidas.",
      "action": "La planta apoya con aportes pecuniarios y no pecuniarios, proyectos o iniciativas que abordan las necesidades y prioridades de la comunidad, con el fin de mejorar la calidad de vida de sus habitantes en temas como: educación, salud, capacitación, saneamiento, problemas ambientales, deporte, infraestructura comunitaria o pública, con acciones de RES u otras.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A109",
      "link": "https://ciruelacertificada.cl/?s=A109&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "38",
        "189",
        "324",
        "446"
      ],
      "good_practice": "Contribuir al desarrollo local",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Son válidos algunos de los siguientes documentos: - Registro de documento tributario que acredite compras a empresas locales. - Existencia de contratos de compra con proveedores locales.",
      "action": "La planta contribuye a la economía local, comprando los bienes y servicios, que no son claves para la producción (materia prima, ingredientes, envases o embalajes), a personas o empresas locales a nivel provincial. Por ejemplo: materiales de oficina, productos de aseo, alimentación, vestimenta, etc.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A110",
      "link": "https://ciruelacertificada.cl/?s=A110&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "190",
        "325",
        "447"
      ],
      "good_practice": "Contribuir a la economía local",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Social",
      "verification_detail": "Son válidos algunos de los siguientes documentos: * Registro de contratos laborales. * Registro de ofertas laborales en la OMIL local.",
      "action": "La planta promueve la contratación de personas mediante la difusión de ofertas laborales a los habitantes de la misma provincia, ya sea de trabajo temporal o permanente.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A111",
      "link": "https://ciruelacertificada.cl/?s=A111&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "39",
        "191",
        "326",
        "448"
      ],
      "good_practice": "Contribuir a la economía local",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Registro de contratos identificando a personas de la provincia.",
      "action": "La planta cuenta con, al menos, un 90% del personal contratado (de manera permanente) de la misma provincia.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A112",
      "link": "https://ciruelacertificada.cl/?s=A112&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "192",
        "327",
        "449"
      ],
      "good_practice": "Contribuir a la economía local",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Portafolio que registre los canales de comunicación con la comunidad, por ejemplo: acta de reuniones con la JJVV, anuncios en radios locales, publicaciones en el diario mural de la junta de vecinos, mensajes de WhatsApp, etc.",
      "action": "La planta cuenta con canales de comunicación efectivos, para informar a las comunidades locales sobre la faena que podría impactar positiva o negativamente en el entorno o territorio, y otras actividades que se quieran comunicar.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A113",
      "link": "https://ciruelacertificada.cl/?s=A113&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "40",
        "193",
        "328",
        "450"
      ],
      "good_practice": "Mantener un sistema de comunicación efectivo con la comunidad",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Registros del libro de reclamos y sugerencias, además de las soluciones implementadas con: - Nombre - Fecha - Correo electrónico - Teléfono - Reclamo o sugerencia - Encargado de gestionar - Resolución. - Fecha resolución",
      "action": "La planta dispone de un mecanismo de gestión de reclamos y sugerencias, a disposición de las comunidades locales, y además, mantiene un registro de las mismas y de cómo se han abordado.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A114",
      "link": "https://ciruelacertificada.cl/?s=A114&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "37",
        "194",
        "329",
        "451"
      ],
      "good_practice": "Mantener un sistema de comunicación efectivo con la comunidad",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Social",
      "verification_detail": "Son válidos alguno de los siguientes documentos: * Identificación la persona encargada o responsable a través del organigrama o la descripción de cargos. * Convenio con la institución que realiza los trabajos comunitarios.",
      "action": "La planta cuenta con una persona responsable de coordinar, planificar y ejecutar proyectos de relacionamiento comunitario.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A115",
      "link": "https://ciruelacertificada.cl/?s=A115&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "195",
        "330",
        "452"
      ],
      "good_practice": "Mantener un sistema de comunicación efectivo con la comunidad",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Inspección visual de las instalaciones o dispositivos dispensadores de agua potable.",
      "action": "La planta provee a las personas que trabajan en ella, acceso a agua potable suficiente y segura, destinada al consumo humano.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A116",
      "link": "https://ciruelacertificada.cl/?s=A116&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "174",
        "309",
        "453"
      ],
      "good_practice": "Disponer de instalaciones adecuadas y seguras de las personas que trabajan en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Inspección visual de servicios higiénicos, espacios de protección para el sol (predio), camarines, comedor o casino y áreas de descanso.",
      "action": "La planta proporciona a quienes trabajan en ella, instalaciones que cuenten con las siguientes características. - Servicios higiénicos de uso individual o colectivo. - Espacios de protección del sol y la lluvia. - Instalaciones para cambiarse de ropa y las prendas exteriores de protección. - Comedor o casino. - Áreas designadas para el descanso y las pausas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A117",
      "link": "https://ciruelacertificada.cl/?s=A117&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "175",
        "310",
        "454"
      ],
      "good_practice": "Disponer de instalaciones adecuadas y seguras de las personas que trabajan en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Registro actualizado de manera mensual con la siguiente información. - Número mensual diferenciado por sexo. - Número mensual de incidentes y accidentes. - Número mensual de casos con enfermedades profesionales. - Total mensual de días perdidos. - Tasa de accidentabilidad. - Licencias médicas.",
      "action": "La planta mantiene un registro mensual de la gestión de la seguridad de las personas que trabajan en ella.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A118",
      "link": "https://ciruelacertificada.cl/?s=A118&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "34",
        "176",
        "311",
        "455"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en la planta",
      "verification_type": "Bitácora"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Señalética con protocolo de emergencias o accidentes que contiene la siguiente información. - Teléfonos y contactos de emergencia. - Medidas básicas de primeros auxilios. - Zonas de seguridad dentro de la planta. - Mapas de ubicación de extintores y botiquines. - Vías de evacuación.",
      "action": "La planta cuenta con un protocolo en caso de emergencia (sismos, incendios, fuga de gases, otros) o accidentes laborales. Los detalles del protocolo están claramente exhibidos en lugares accesibles y visibles.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A119",
      "link": "https://ciruelacertificada.cl/?s=A119&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "62",
        "63",
        "64",
        "65",
        "66",
        "67",
        "177",
        "312",
        "456"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Social",
      "verification_detail": "Contrato con profesional prevencionista o convenio con la Mutual de seguridad.",
      "action": "La planta cuenta con una persona encargada del programa de prevención de riesgos (prevencionista de riesgos) o un convenio con una mutual que desarrolle esta labor.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A120",
      "link": "https://ciruelacertificada.cl/?s=A120&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "178",
        "313",
        "457"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Documento con el programa de prevención de riesgos que contemple los siguientes aspectos: * Identificación y evaluación de riesgos. * Medidas preventivas y de protección. * Vigilancia de la salud. * Investigación de accidentes e incidentes.",
      "action": "La planta implementa un programa de gestión de riesgos para quienes trabajan en ella.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A121",
      "link": "https://ciruelacertificada.cl/?s=A121&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "33",
        "179",
        "314",
        "458"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Social",
      "verification_detail": "Registro de que las personas que manejan productos agroquímicos, cuentan con exámenes médicos vigentes (al menos de un año). Por ejemplo: ruido, oído medio, control de sangre preventivo, examen general, examen de colinesterasa, etc. (mutual).",
      "action": "La planta somete a exámenes médicos, al menos una vez al año, a quienes trabajan en ella y que normalmente estén expuestos a labores que puedan generar un riesgo para su salud (ruido, sustancias tóxicas, entre otros) y entrega los resultados a cada uno.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A122",
      "link": "https://ciruelacertificada.cl/?s=A122&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "180",
        "315",
        "459"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Documento con el reglamento interno de la planta.",
      "action": "La planta no discrimina por raza, color, religión, género, nacionalidad, tendencia política, etc.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A123",
      "link": "https://ciruelacertificada.cl/?s=A123&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "181",
        "316",
        "460"
      ],
      "good_practice": "Velar por el bienestar social y laboral de las personas que trabajan en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "La planta capacita a quienes trabajan en ella sobre cómo desempeñar las labores asociadas a su trabajo, buscando la eficiencia en su desempeño.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A124",
      "link": "https://ciruelacertificada.cl/?s=A124&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "54",
        "182",
        "317",
        "461"
      ],
      "good_practice": "Velar por el bienestar social y laboral de las personas que trabajan en la planta",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Social",
      "verification_detail": "Portafolio de evidencia que respalde la existencia del programa con listado de potenciales instituciones u organizaciones de apoyo, públicas o privadas.",
      "action": "La planta cuenta con un programa para promover estilos de vida saludables y prevenir dependencias a drogas y alcohol.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A125",
      "link": "https://ciruelacertificada.cl/?s=A125&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "183",
        "318",
        "462"
      ],
      "good_practice": "Velar por el bienestar social y laboral de las personas que trabajan en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Social",
      "verification_detail": "Son válidos alguno de los siguientes documentos: * Registro de información entregada a través de correos electrónicos, folletos, publicaciones en diarios murales y/o registros de capacitaciones asociadas al tema. * Registro de entrega del Reglamento interno. * Registro de inducciones o documento con instrucciones respecto al puesto de trabajo.",
      "action": "La planta se asegura de que las personas que trabajan en ella, conozcan sus derechos y obligaciones, relacionados con la situación contractual con la empresa y las leyes laborales vigentes.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A126",
      "link": "https://ciruelacertificada.cl/?s=A126&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "184",
        "319",
        "463"
      ],
      "good_practice": "Respetar los derechos laborales de las personas que trabajan en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Social",
      "verification_detail": "Documentación con contratos de trabajo, finiquitos, registro de asistencia y pago de leyes sociales que indiquen lo siguiente. - No supera el máximo de horas diarias y semanales permitidas. - No supera el máximo de horas extras permitidas. - Provee de pausas diarias para el almuerzo y el descanso. - Otorga tiempo libre pagado por vacaciones y licencia por enfermedad. - Posibilita la desvinculación voluntaria en casos específicos. - Emplea prácticas de pago transparentes y justas.",
      "action": "La planta respeta y adhiere a las leyes aplicables a los derechos laborales de las personas que trabajan en ella.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A127",
      "link": "https://ciruelacertificada.cl/?s=A127&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "185",
        "320",
        "464"
      ],
      "good_practice": "Respetar los derechos laborales de las personas que trabajan en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Son válidos alguno de los siguientes documentos: * Política o procedimientos de contratación de la planta. * Registro de ofertas laborales del último año en las que se evidencie que no se solicita que la persona pertenezca a un género en específico.",
      "action": "La planta promueve la equidad de género en su política de contrataciones, evidenciando que no existe solicitud específica de género en sus ofertas laborales.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A128",
      "link": "https://ciruelacertificada.cl/?s=A128&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "186",
        "321",
        "465"
      ],
      "good_practice": "Respetar los derechos laborales de las personas que trabajan en la planta",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ética",
      "verification_detail": "Se requiere matriz con listado de normativas aplicables para la planta que incluya la siguiente información: * Tipo de documento (ley, resolución, decreto, norma, etc.) y entidad o Ministerio. * Identificación de normativas prioritarias. * Acciones requeridas para verificar y asegurar su cumplimiento. Adicionalmente, se debe mantener al menos una copia de las normativas prioritarias, ya sea como documento impreso y/o registro digital.",
      "action": "La planta identifica las legislaciones relacionadas con las obligaciones prioritarias para la empresa, a través de una matriz de riesgos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A129",
      "link": "https://ciruelacertificada.cl/?s=A129&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida diligencia de la Legislación",
      "linked_resources": [
        "41",
        "196",
        "331",
        "466"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ética",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "Los personas que trabajan en la planta han sido capacitadas y conocen la legislación aplicable a sus labores.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A130",
      "link": "https://ciruelacertificada.cl/?s=A130&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida diligencia de la Legislación",
      "linked_resources": [
        "55",
        "197",
        "332",
        "467"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ética",
      "verification_detail": "Inspección visual de documentos de registro archivados o documentos digitales almacenados.",
      "action": "La planta guarda los registros que acrediten el cumplimiento de las diferentes legislaciones o certificaciones durante un plazo de al menos 5 años.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A131",
      "link": "https://ciruelacertificada.cl/?s=A131&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida diligencia de la Legislación",
      "linked_resources": [
        "198",
        "333",
        "468"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ética",
      "verification_detail": "Son válidos los siguientes documentos de validación. * Escritura de propiedad que verifique el uso de suelo. * Copia de instrumentos de ordenamiento territorial que verifiquen uso de suelo.",
      "action": "La planta demuestra un título o contrato de uso de tierra claro en conformidad con las prácticas, uso de suelo y legislaciones nacionales.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A132",
      "link": "https://ciruelacertificada.cl/?s=A132&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida diligencia de la Legislación",
      "linked_resources": [
        "199",
        "334",
        "469"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ética",
      "verification_detail": "Son válidos los siguientes documentos de validación. * Registro en el Conservador de Bienes Raíces (CBR). * Catastro Público de Aguas de la DGA.",
      "action": "La planta posee Derechos de Aprovechamiento de Aguas inscritos en conformidad con las legislaciones nacionales.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A133",
      "link": "https://ciruelacertificada.cl/?s=A133&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida diligencia de la Legislación",
      "linked_resources": [
        "200",
        "335",
        "470"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ética",
      "verification_detail": "Son válidos los siguientes documentos: * Actas de reuniones realizadas a través de la Ley de Lobby. * Actas de reuniones con entidades legisladoras a la empresa.",
      "action": "La planta mantiene un diálogo permanente con las instituciones asociadas a las entidades legisladoras a nivel territorial o regional.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A134",
      "link": "https://ciruelacertificada.cl/?s=A134&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida diligencia de la Legislación",
      "linked_resources": [
        "58",
        "201",
        "336",
        "471"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ética",
      "verification_detail": "Autodiagnóstico con alguna de las herramientas de autoevaluación de debida diligencia de derechos humanos.",
      "action": "Las empresas realizan un autodiagnóstico de conducta empresarial responsable y debida diligencia en derechos humanos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "A135",
      "link": "https://ciruelacertificada.cl/?s=A135&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-adecuacion-agroindustrial%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida diligencia de la Legislación",
      "linked_resources": [
        "202",
        "337",
        "472"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    }
  ]
}
```

#### Documento 2 - ID: `produccion-primaria`

```json
{
  "template_name": "produccion-primaria",
  "description": "Estándar de Producción Primaria",
  "questions": [
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro de consumo de agua de riego mensual con especificaciones de la siguiente información:  - Fecha.  - Cultivo.  - Sector o cuartel.  - Fuente de abastecimiento disponible (canal, pozo, suministro de agua potable, red aljibe, etc.).  - Superficie.  - Tiempo de riego.  - Días de riego en la semana.  - Volumen de agua aplicado en el día (litros).  - Volumen de agua acumulado (litros).",
      "action": "El predio registra mensualmente el consumo de agua de riego especificando la fuente de abastecimiento y su uso.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P001",
      "link": "https://ciruelacertificada.cl/?s=P001&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "476",
        "572",
        "717",
        "862"
      ],
      "good_practice": "Gestionar los recursos hídricos en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada) o certificado de participación en instancias de capacitación externa (cursos, seminarios, congresos, etc.). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "El predio capacita a quienes trabajan como tomadores de decisiones en el ámbito hídrico, abordando estrategias para la gestión eficiente del recurso.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P002",
      "link": "https://ciruelacertificada.cl/?s=P002&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "547",
        "573",
        "718",
        "863"
      ],
      "good_practice": "Gestionar los recursos hídricos en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Mapa o plano de las fuentes de agua, ya sea en digital o en papel.",
      "action": "El predio cuenta con un mapa con la ubicación de las fuentes de aprovisionamiento de agua dentro de la explotación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P003",
      "link": "https://ciruelacertificada.cl/?s=P003&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "574",
        "719",
        "864"
      ],
      "good_practice": "Gestionar los recursos hídricos en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada).",
      "action": "El predio capacita a las personas que trabajan en la ejecución de acciones asociadas al riego, abordando acciones operativas que permitan la gestión eficiente del recurso.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P004",
      "link": "https://ciruelacertificada.cl/?s=P004&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "548",
        "575",
        "720",
        "865"
      ],
      "good_practice": "Gestionar los recursos hídricos en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Plano de equipamiento de riego, ya sea en formato digital o en papel.",
      "action": "El predio cuenta con planos de la infraestructura de riego asociada a su producción.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P005",
      "link": "https://ciruelacertificada.cl/?s=P005&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "576",
        "721",
        "866"
      ],
      "good_practice": "Gestionar los recursos hídricos en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro del monitoreo de extracciones DGA que cuenta con:  - Datos del titular: Nombre, RUT y dirección del titular de la autorización de extracción.  - Datos de la fuente: Nombre, código y ubicación de la fuente de agua de la que se extrae.  - Datos de la extracción:  * Fecha y hora de inicio y término de la extracción.  * Caudal y/o volumen extraído.  * Nombre y firma de quién realizó la extracción.  - Datos del medidor (Número de serie, fecha de calibración y factor de corrección del medidor de flujo utilizado para medir la extracción).",
      "action": "El predio que posee pozo profundo, utiliza instrumentos de medición para registrar su caudal, cumpliendo con el monitoreo de extracciones exigido por la DGA.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P006",
      "link": "https://ciruelacertificada.cl/?s=P006&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "577",
        "722",
        "867"
      ],
      "good_practice": "Gestionar los recursos hídricos en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Plan de gestión del recurso hídrico que considere la siguiente información:  - Indicador de eficiencia del uso del agua utilizada (litros de agua/kg ciruela fresca).  - Meta de eficiencia del uso del agua en base al indicador propuesto en el punto anterior.  - Propuesta de un porcentaje de reducción del uso del agua, en el caso de que no se cumpla con la meta de eficiencia.",
      "action": "El predio cuenta con un documento que define un plan de gestión del recurso hídrico.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P007",
      "link": "https://ciruelacertificada.cl/?s=P007&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "474",
        "578",
        "723",
        "868"
      ],
      "good_practice": "Gestionar los recursos hídricos en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Check list o calendarización de monitoreo de comprobación de fugas con la siguiente información.  - Tipo de evento.  - Fecha de ejecución.  - Equipo o infraestructura.  - Detalle de labores.  - Responsable.",
      "action": "El predio monitorea regularmente las fugas o roturas dentro de su infraestructura hídrica.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P008",
      "link": "https://ciruelacertificada.cl/?s=P008&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "480",
        "579",
        "724",
        "869"
      ],
      "good_practice": "Minimizar las pérdidas de agua en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de señaléticas de ahorro de agua en servicios higiénicos y de alimentación, zona de lavado de equipos y maquinarias.",
      "action": "El predio cuenta con señalética orientada al ahorro de agua en lugares críticos (servicios higiénicos y de alimentación, zona de lavado de equipos y maquinarias).",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P009",
      "link": "https://ciruelacertificada.cl/?s=P009&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "473",
        "580",
        "725",
        "870"
      ],
      "good_practice": "Minimizar las pérdidas de agua en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de fuentes y cursos de agua limpios.",
      "action": "El predio cuenta con fuentes y cursos de agua libres de residuos sólidos domiciliarios y agrícolas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P010",
      "link": "https://ciruelacertificada.cl/?s=P010&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "581",
        "726",
        "871"
      ],
      "good_practice": "Minimizar los riesgos de contaminación de aguas",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de existencia de zona de lavado de equipos que no esté en contacto con el suelo y con vías de evacuación de aguas de lavado.",
      "action": "El predio cuenta con un espacio específico para el lavado de equipos y maquinarias, alejado de las fuentes o cursos de agua.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P011",
      "link": "https://ciruelacertificada.cl/?s=P011&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "582",
        "727",
        "872"
      ],
      "good_practice": "Minimizar los riesgos de contaminación de aguas",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Informe de análisis físico-químicos y microbiológicos, actualizados periódicamente según NCH409.",
      "action": "El predio realiza análisis periódicos para evaluar la calidad química y biológica de las fuentes de alimentación de agua.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P012",
      "link": "https://ciruelacertificada.cl/?s=P012&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "583",
        "728",
        "873"
      ],
      "good_practice": "Monitorear y asegurar la calidad del agua utilizada en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro que demuestre la ejecución de las calicatas con la siguiente información:  * Número o código.  * Fecha de ejecución.  * Sector, cuartel o georreferenciación.  * Profundidad.  * Textura (ej.: arcillosa, arenosa, etc.).  * Resultados obtenidos (nivel de humedad).",
      "action": "El predio realiza mediciones de humedad de suelo mediante la observación de calicatas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P013",
      "link": "https://ciruelacertificada.cl/?s=P013&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "495",
        "584",
        "729",
        "874"
      ],
      "good_practice": "Gestionar eficientemente el riego en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de los equipos de riego utilizados en el predio.",
      "action": "El predio utiliza riego tecnificado para el cultivo, como por ejemplo: riego por goteo o microaspersión.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P014",
      "link": "https://ciruelacertificada.cl/?s=P014&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "585",
        "730",
        "875"
      ],
      "good_practice": "Gestionar eficientemente el riego en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Check list o registro de mantención de la infraestructura con los siguientes datos:  • Fecha  • Tipo de evento  • Equipo o infraestructura  • Detalle labores  • Responsable  En el caso de que las mantenciones las realice una empresa externa, esta debe entregar un comprobante o informe que certifique que las acciones realizadas estén en función de lo solicitado.",
      "action": "El predio realiza mantención a los equipos de riego y fertirriego de manera periódica, al menos una vez en la temporada o con mayor frecuencia si el fabricante lo recomienda.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P015",
      "link": "https://ciruelacertificada.cl/?s=P015&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "586",
        "731",
        "876"
      ],
      "good_practice": "Gestionar eficientemente el riego en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro del balance hídrico indicando la siguiente información:  - Fecha de evaluación.  - Coeficiente de cultivo (Kc).  - Sector, cuartel o zona homogénea de cultivo.  - Evapotranspiración de referencia (ETo) indicando la fuente de obtención de la información (estación meteorológica propia o datos de portales como http://agroclima.cl/ o https://agrometeorologia.cl/ ).  - Volumen de agua aplicada en el último riego.  - Precipitación efectiva en el periodo.  - Evapotranspiración de cultivo (ETc)  - Balance hídrico (diferencia entre aportes y pérdidas de agua).",
      "action": "El predio programa el riego en función del balance hídrico, con el fin de reponer el déficit de humedad el suelo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P016",
      "link": "https://ciruelacertificada.cl/?s=P016&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "477",
        "587",
        "732",
        "877"
      ],
      "good_practice": "Gestionar eficientemente el riego en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de la uniformidad de distribución del sistema de riego tecnificado que contemple los siguientes puntos:  * Fecha de evaluación.  * Equipo de riego.  * Sector o cuartel.  * Caudal del equipo (litros/horas).  * Porcentaje de uniformidad.  * Desempeño (excelente, bueno, crítico, inaceptable).  * Medidas correctivas implementadas de ser necesarias.  * Responsable.  En el caso de que esta labor la realice una empresa externa, debe existir un contrato e informe que acredite la realización de las actividades ejecutadas.",
      "action": "El predio evalúa la uniformidad de la distribución del sistema de riego tecnificado, al menos una vez por temporada e implementa medidas de corrección cuando el coeficiente de uniformidad es menor a 85%.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P017",
      "link": "https://ciruelacertificada.cl/?s=P017&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "478",
        "588",
        "733",
        "878"
      ],
      "good_practice": "Gestionar eficientemente el riego en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de los equipos de riego utilizados en el predio.",
      "action": "El predio implementa tecnologías de riego tecnificado subterráneo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P018",
      "link": "https://ciruelacertificada.cl/?s=P018&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "589",
        "734",
        "879"
      ],
      "good_practice": "Gestionar eficientemente el riego en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de datos de humedad de suelo, obtenidos con los instrumentos utilizados indicando la siguiente información:  * Fecha.  * Equipo de riego.  * Humedad de suelo o potencial hídrico de la planta, según datos arrojados por el instrumento.  * Observaciones.  * Responsable.  En el caso de que esta labor la realice una empresa externa, debe existir un contrato e informe que acredite la realización de las actividades ejecutadas.",
      "action": "El predio realiza mediciones de humedad al suelo o al potencial hídrico de la planta, mediante la utilización de sondas o tecnologías de detección de humedad como por ejemplo: tensiómetros o bombas de presión.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P019",
      "link": "https://ciruelacertificada.cl/?s=P019&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Agua",
      "linked_resources": [
        "479",
        "590",
        "735",
        "880"
      ],
      "good_practice": "Gestionar eficientemente el riego en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro que demuestre la ejecución de las calicatas con la siguiente información:  * Número o código.  * Fecha de ejecución.  * Sector, cuartel o georreferenciación.  * Profundidad.  * Textura (ej.: arcillosa, arenosa, etc.).  * Resultados obtenidos con respecto a las características del suelo.",
      "action": "El predio realiza calicatas para analizar las características del suelo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P020",
      "link": "https://ciruelacertificada.cl/?s=P020&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "496",
        "591",
        "736",
        "881"
      ],
      "good_practice": "Planificar el huerto y gestionar el suelo de manera sustentable en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Documento diagnóstico que contemple la siguiente información:  - Mapa o diagrama del predio diferenciando entre distintos tipos de suelo.  - Identificación de los perfiles de suelo y su riesgo de erosión.  - Identificación de las áreas particularmente susceptibles a erosión.",
      "action": "El predio realiza un diagnóstico predial para identificar las características del suelo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P021",
      "link": "https://ciruelacertificada.cl/?s=P021&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "488",
        "592",
        "737",
        "882"
      ],
      "good_practice": "Planificar el huerto y gestionar el suelo de manera sustentable en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Check list o registro de mantención de la infraestructura con los siguientes datos:  • Fecha  • Tipo de evento  • Equipo o infraestructura  • Detalle labores  • Responsable  En el caso de que las mantenciones las realice una empresa externa, esta debe entregar un comprobante o informe que certifique las acciones realizadas estén en función de lo solicitado.",
      "action": "El predio minimiza los riesgos de contaminación del suelo realizando mantenciones a sus equipos de aplicación de agroquímicos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P022",
      "link": "https://ciruelacertificada.cl/?s=P022&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "482",
        "593",
        "738",
        "883"
      ],
      "good_practice": "Prevenir y mitigar la degradación de los suelos en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "- Inspección visual de cuarteles, verificando signos de la existencia de cobertura vegetal natural o sembrada.",
      "action": "El predio mantiene o mejora las coberturas vegetales en los suelos, para evitar que queden descubiertos, contemplando al menos un 50% de cobertura en la entre hilera.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P023",
      "link": "https://ciruelacertificada.cl/?s=P023&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "594",
        "739",
        "884"
      ],
      "good_practice": "Prevenir y mitigar la degradación de los suelos en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de la señalética que indique que no se realizan quemas en el campo.",
      "action": "El predio no quema la vegetación del lugar para despejar las zonas productivas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P024",
      "link": "https://ciruelacertificada.cl/?s=P024&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "487",
        "595",
        "740",
        "885"
      ],
      "good_practice": "Prevenir y mitigar la degradación de los suelos en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de labores de campo que contenga la siguiente información:  • Fecha y hora.  • Sector o cuartel.  • Labor ejecutada.  • Objetivo de la labor.  • Responsable.  • Hallazgos (opcional).",
      "action": "El predio implementa medidas para mejorar la estructura del suelo y evitar su compactación con medidas como por ejemplo:  - Incrementar el porcentaje de materia orgánica en el suelo, a través de enmiendas orgánicas.  - Incorporar restos de poda.  - Incorporar rastrojos.  - Utilizar rotura vertical (subsolado).  - Realizar enmiendas cálcicas (yeso).",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P025",
      "link": "https://ciruelacertificada.cl/?s=P025&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "493",
        "596",
        "741",
        "886"
      ],
      "good_practice": "Prevenir y mitigar la degradación de los suelos en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Mapa o plano que indique las zonas compactadas, indicadas a través de:  * Penetrómetro.  * Perfil de suelo a través de calicatas.  * Medición de densidad aparente o velocidad de infiltración.",
      "action": "El predio identifica las zonas compactadas dentro de su explotación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P026",
      "link": "https://ciruelacertificada.cl/?s=P026&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "597",
        "742",
        "887"
      ],
      "good_practice": "Prevenir y mitigar la degradación de los suelos en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada).",
      "action": "El predio capacita al personal de la empresa sobre la degradación de suelos y da a conocer técnicas de cultivo que evitan la erosión.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P027",
      "link": "https://ciruelacertificada.cl/?s=P027&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "549",
        "598",
        "743",
        "888"
      ],
      "good_practice": "Prevenir y mitigar la degradación de los suelos en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual verificando que exista alguna de las siguientes medidas.  - Usar sistemas de riego localizado.  - Plantar árboles en el borde de las zonas de pendiente.  - Utilizar zanjas de infiltración.  - Plantar en curvas de nivel.",
      "action": "El predio aplica medidas para evitar la erosión por escurrimiento tanto antes, durante y después de plantación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P028",
      "link": "https://ciruelacertificada.cl/?s=P028&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "599",
        "744",
        "889"
      ],
      "good_practice": "Prevenir y mitigar la degradación de los suelos en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de cuarteles, verificando que exista alguna de las siguientes medidas.  - Se plantan especies vegetales que sirven como corta vientos.  - Se usa la vegetación nativa y/o natural, en taludes y bordes de canales.",
      "action": "El predio no deja expuesto el suelo y protege el área de cultivo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P029",
      "link": "https://ciruelacertificada.cl/?s=P029&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "600",
        "745",
        "890"
      ],
      "good_practice": "Prevenir y mitigar la degradación de los suelos en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo de labores de campo que manifieste que se realizan medidas de mínima labranza.",
      "action": "El predio cuenta con un protocolo que menciona estrategias de mínima labranza para no alterar la condición del suelo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P030",
      "link": "https://ciruelacertificada.cl/?s=P030&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "486",
        "601",
        "746",
        "891"
      ],
      "good_practice": "Prevenir y mitigar la degradación de los suelos en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Informe con resultados de análisis de suelo por cuartel o zona homogénea de manejo, realizado cada 3 años, que contenga al menos la siguiente información:  - Análisis químico.  - Conductividad eléctrica y CIC.  - Bases de intercambio.  - Materia orgánica.",
      "action": "El predio realiza periódicamente, un análisis del suelo por cuartel o zona homogénea de manejo, para controlar los cambios en su estado.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P031",
      "link": "https://ciruelacertificada.cl/?s=P031&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "602",
        "747",
        "892"
      ],
      "good_practice": "Gestionar la fertilización del predio de manera sustentable",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro de aplicaciones de fertilizantes durante la temporada que cuente con los siguientes datos:  * Fecha y hora de la aplicación.  * Sector o cuartel.  * Nombre del producto.  * Composición (P2O5, K2O o N y otros nutrientes).  * Identificación de fertilizantes nitrogenados.  * Dosis.  * Método de aplicación.  * Responsable",
      "action": "El predio aplica los fertilizantes de forma parcializada durante la temporada y teniendo en cuenta el estado fenológico del cultivo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P032",
      "link": "https://ciruelacertificada.cl/?s=P032&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "490",
        "603",
        "748",
        "893"
      ],
      "good_practice": "Gestionar la fertilización del predio de manera sustentable",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Plan de fertilización actualizado que contenga la siguiente información:  - Registro de los manejos históricos en términos de rendimientos.  - Muestreo de suelos.  - Evaluación del nivel nutricional de las plantas y del suelo post fertilización.  - Definición de un programa de fertilización para la temporada.  - Medidas de monitoreo y estrategias de corrección para las siguientes temporadas.",
      "action": "El predio cuenta con un plan de fertilización actualizado, basado en las características del suelo y la demanda del cultivo. Dicho plan debe ser actualizado cada temporada.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P033",
      "link": "https://ciruelacertificada.cl/?s=P033&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "489",
        "604",
        "749",
        "894"
      ],
      "good_practice": "Gestionar la fertilización del predio de manera sustentable",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de aplicaciones de fertilizantes a través de fertirriego durante la temporada con la siguiente información:  * Fecha y hora de aplicación.  * Sector o cuartel.  * Nombre del producto.  * Composición (P2O5, K2O o N y otros nutrientes).  * Identificación de fertilizantes nitrogenados.  * Dosis.  * Método de aplicación.  * Responsable",
      "action": "El predio prioriza el uso de fertilizantes que se aplican en pequeñas proporciones a través de sistemas de fertirriego, según los periodos de demanda correspondientes.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P034",
      "link": "https://ciruelacertificada.cl/?s=P034&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "491",
        "605",
        "750",
        "895"
      ],
      "good_practice": "Gestionar la fertilización del predio de manera sustentable",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de aplicaciones de fertilizantes durante la temporada, identificando fertilizantes orgánicos con la siguiente información:  * Fecha y hora de aplicación.  * Sector o cuartel.  * Nombre del producto.  * Composición (P2O5, K2O o N y otros nutrientes).  * Composición orgánica.  * Identificación de fertilizantes nitrogenados.  * Dosis.  * Método de aplicación.  * Responsable.",
      "action": "El predio prioriza el uso de métodos de fertilización orgánica como abono, por ejemplo: compost, ácidos húmicos, entre otros.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P035",
      "link": "https://ciruelacertificada.cl/?s=P035&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Suelo",
      "linked_resources": [
        "492",
        "606",
        "751",
        "896"
      ],
      "good_practice": "Gestionar la fertilización del predio de manera sustentable",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Diagnóstico de la biodiversidad con los siguientes puntos:  - Mapa con identificación de áreas en la explotación con alto valor ecológico (ej.: lagos, estanques y cursos de agua, corredores de vida silvestre, humedales, pastizales ricos en especies, etc.).  - Catastro de la biodiversidad existente en el lugar, por ejemplo: principales especies presentes en el entorno (aves, mamíferos, árboles, insectos, hongos, arbustos, etc.).  - Registro fotográfico con georreferenciación del estado inicial de las zonas de vegetación natural de conectividad, márgenes y límites de los campos, zonas de amortiguamiento ribereño y áreas de conservación con vegetación nativa.",
      "action": "El predio cuenta con un diagnóstico donde se identifica la biodiversidad existente y las áreas de alto valor ecológico, dentro de su propiedad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P036",
      "link": "https://ciruelacertificada.cl/?s=P036&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "501",
        "607",
        "752",
        "897"
      ],
      "good_practice": "Establecer un ordenamiento territorial y línea base",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Plan de gestión con protocolos para la implementación de las siguientes medidas:  - Línea base de sitios de interés.  - Priorización y definición de objetivos de conservación.  - Medidas de conectividad, restauración y rehabilitación.  - Medidas de manejo y control de especies exóticas.  - Plan de ordenamiento predial.  Dicho documento debe tener una fecha de elaboración inferior a 5 años.",
      "action": "El predio cuenta con un plan para la gestión de la biodiversidad que propone medidas de conservación, utilizando información rescatada en el diagnóstico realizado previamente. Este plan es evaluado y actualizado cada 5 años.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P037",
      "link": "https://ciruelacertificada.cl/?s=P037&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "502",
        "608",
        "753",
        "898"
      ],
      "good_practice": "Establecer un ordenamiento territorial y línea base",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada).",
      "action": "El predio capacita a quienes trabajan permanentemente en la empresa, sobre el plan de gestión de la biodiversidad propuesto, generando un listado de acciones a tomar para potenciar la biodiversidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P038",
      "link": "https://ciruelacertificada.cl/?s=P038&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "550",
        "609",
        "754",
        "899"
      ],
      "good_practice": "Fomentar la participación en acciones para la protección y conservación de ecosistemas, hábitats o especies",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Actas de reuniones de mesas de trabajo con empresas en el territorio.",
      "action": "El predio mantiene un diálogo permanente con las empresas relacionadas al rubro en el territorio, con el objetivo de implementar en conjunto, medidas de conservación y mitigación que les permitan tener un plan de gestión de manera asociativa.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P039",
      "link": "https://ciruelacertificada.cl/?s=P039&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "561",
        "610",
        "755",
        "900"
      ],
      "good_practice": "Fomentar la participación en acciones para la protección y conservación de ecosistemas, hábitats o especies",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo de gestión y conservación de márgenes y límites de los campos, definiendo medidas preventivas.",
      "action": "El predio cuenta con márgenes y límites de los campos que se gestionan, de manera de asegurar su conservación, minimizando su intervención.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P040",
      "link": "https://ciruelacertificada.cl/?s=P040&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "611",
        "756",
        "901"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de la existencia de vegetación natural de conectividad.",
      "action": "El predio mantiene la conectividad entre la vegetación natural, potenciando su complejidad estructural, a través de cercos vivos, corredores biológicos, franjas ribereñas, entre otras.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P041",
      "link": "https://ciruelacertificada.cl/?s=P041&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "612",
        "757",
        "902"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de los márgenes ribereños o franjas de amortiguación, los que deben ser mayores a 5 m en cursos de agua y mayores a 10 m en manantiales y cuerpos de agua.",
      "action": "El predio protege las zonas de amortiguamiento ribereño (dentro de su propiedad), en el caso de encontrarse a menos de 50 metros de un cuerpo de agua o ecosistema acuático.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P042",
      "link": "https://ciruelacertificada.cl/?s=P042&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "613",
        "758",
        "903"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de monitoreo de especies exóticas invasoras con la siguiente información:  * Fecha del hallazgo.  * Nombre de la especie.  * Ubicación.  * N° de individuos visualizados.  * Daño provocado.  * Medidas de mitigación.",
      "action": "El predio identifica y monitorea las especies exóticas invasoras, en base al listado descrito en el diagnóstico.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P043",
      "link": "https://ciruelacertificada.cl/?s=P043&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "503",
        "614",
        "759",
        "904"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Son válidos los siguientes documentos:  - Mapa que identifique zonas con vegetación nativa.  - Registro del comparativo de las fotografías de estado inicial con respecto a la situación actual.",
      "action": "El predio mantiene áreas de conservación con vegetación nativa.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P044",
      "link": "https://ciruelacertificada.cl/?s=P044&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "615",
        "760",
        "905"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de señaléticas de medidas de protección de fauna silvestre con respecto a:  - No cazar, matar, pescar o recolectar animales con prohibición según la legislación.  - No retener la vida silvestre en cautiverio.  - No realizar labores de limpieza de zanjas o poda de corta vientos en época de anidación de aves.  - Limitar el libre movimiento de animales domésticos en áreas de producción.  - Protocolo de acción en el caso de encontrar una especie nativa herida.",
      "action": "El predio implementa medidas para proteger especies de fauna silvestre.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P045",
      "link": "https://ciruelacertificada.cl/?s=P045&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "497",
        "498",
        "499",
        "500",
        "616",
        "761",
        "906"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo de reforestación que incluya medidas de cuidado de árboles reforestados.",
      "action": "El predio implementa procedimientos de reforestación o replantación, en caso de ser requerida la remoción de árboles dentro de la misma explotación. Esta reforestación debe realizarse con especies nativas de bajo requerimiento hídrico.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P046",
      "link": "https://ciruelacertificada.cl/?s=P046&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Biodiversidad",
      "linked_resources": [
        "617",
        "762",
        "907"
      ],
      "good_practice": "Implementar sistemas, programas o acciones para el manejo, protección y mantención de ecosistemas, especies y hábitats",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro actualizado de aplicaciones con la siguiente información:  * Fecha y hora.  * Sector o cuartel.  * Nombre del producto.  * Color de la etiqueta.  * Ingrediente activo.  * Dosis.  * Método de aplicación.  * Objetivo de la aplicación.  * Período de carencia y de reingreso.  * Responsable.",
      "action": "El predio registra las aplicaciones de agroquímicos realizadas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P047",
      "link": "https://ciruelacertificada.cl/?s=P047&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "506",
        "618",
        "763",
        "908"
      ],
      "good_practice": "Registrar las aplicaciones de productos agroquímicos",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de monitoreo de plagas, enfermedades y malezas actualizado mensualmente con la siguiente información:  * Fecha del hallazgo.  * Nombre de la especie.  * Ubicación.  * N° de individuos visualizados.  * Daño provocado.  * Umbral de daño máximo.  * Medidas de control.",
      "action": "El predio monitorea plagas, enfermedades y malezas, para determinar el tipo de intervención a realizar.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P048",
      "link": "https://ciruelacertificada.cl/?s=P048&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "512",
        "619",
        "764",
        "909"
      ],
      "good_practice": "Disminuir el impacto ambiental de los agroquímicos",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo de manejo de plagas que especifique el umbral de daño máximo para las plagas, enfermedades y malezas más comunes, y las aplicaciones a efectuar una vez superado el umbral de daño definido.",
      "action": "El predio realiza un plan de manejo de plagas, enfermedades y malezas, en base a un umbral de daño definido, el cual debe estar asociado al monitoreo realizado.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P049",
      "link": "https://ciruelacertificada.cl/?s=P049&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "620",
        "765",
        "910"
      ],
      "good_practice": "Disminuir el impacto ambiental de los agroquímicos",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro actualizado de aplicaciones con la siguiente información:  * Fecha y hora.  * Sector o cuartel.  * Nombre del producto.  * Color de la etiqueta.  * Ingrediente activo.  * Dosis.  * Método de aplicación.  * Objetivo de la aplicación.  * Período de carencia y de reingreso.  * Responsable.",
      "action": "El predio selecciona los productos agroquímicos en base a su impacto ambiental, prefiriendo aquellos que generen menor impacto (etiqueta verde o azul).",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P050",
      "link": "https://ciruelacertificada.cl/?s=P050&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "507",
        "621",
        "766",
        "911"
      ],
      "good_practice": "Disminuir el impacto ambiental de los agroquímicos",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de pesticidas utilizados durante la temporada, incluyendo el Score del EIQ de cada uno de ellos. Se debe verificar que se haya utilizado el producto con menor Score para el tipo de aplicación, en base a la lista de agroquímicos con autorización vigente SAG para ciruelo.  *El cálculo del EIQ se puede realizar a través de la plataforma elaborada por la universidad de Cornell https://cals.cornell.edu/new-york-state-integrated-pest-management/risk-assessment/eiq/eiq-calculator  ** Se dejará disponible el cálculo de los EIQ de los productos agroquímicos actualmente autorizados por el SAG para ciruelo europeo.",
      "action": "El predio registra el índice de impacto ambiental generado por los productos agroquímicos utilizados en la producción, prefiriendo los que tienen menor impacto para la aplicación correspondiente.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P051",
      "link": "https://ciruelacertificada.cl/?s=P051&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "508",
        "622",
        "767",
        "912"
      ],
      "good_practice": "Disminuir el impacto ambiental de los agroquímicos",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de que exista una zona de almacenamiento de agroquímicos y combustibles identificada, que posea piso, indicación de almacenamiento de productos separado según tipo y señalética con indicaciones en caso de emergencia de derrames.",
      "action": "El predio cuenta con una zona de almacenamiento para productos agroquímicos y combustibles, para no poner en riesgo a las personas y garantizar la inocuidad alimentaria.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P052",
      "link": "https://ciruelacertificada.cl/?s=P052&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "623",
        "768",
        "913"
      ],
      "good_practice": "Almacenar adecuadamente productos agroquímicos",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inventario actualizado, al menos una vez por temporada, de los productos almacenados con su etiqueta y que contenga la siguiente información:  - Nombre del producto.  - Fecha de compra.  - Número de lote y proveedor.  - Unidades adquiridas.  - Volumen utilizado.  - Fecha de caducidad o vencimiento.  - Ingrediente activo.  - Color de la etiqueta.",
      "action": "El predio mantiene un inventario actualizado de la existencia de agroquímicos en la zona de almacenamiento.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P053",
      "link": "https://ciruelacertificada.cl/?s=P053&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "513",
        "624",
        "769",
        "914"
      ],
      "good_practice": "Almacenar adecuadamente productos agroquímicos",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de:  - Señalética con indicaciones en el caso de emergencia por derrames.  - Kit de emergencia en la zona de lavado y almacenamiento, verificando que cuente con:  * Señalética con protocolo de limpieza y números de emergencia.  * Sector de lavado para manos y ojos (lavatorio).  * Material de absorción para evitar propagación del derrame, por ejemplo: arena.  * Sistema manual de extinción de incendios, a base de extintores compatibles con los productos almacenados.",
      "action": "El predio cuenta con un kit de emergencia con señalética informativa para casos de derrames de productos agroquímicos, en el sector de lavado y zonas de almacenamiento.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P054",
      "link": "https://ciruelacertificada.cl/?s=P054&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "504",
        "505",
        "625",
        "770",
        "915"
      ],
      "good_practice": "Almacenar adecuadamente productos agroquímicos",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Check list o registro de mantención de equipos de aplicación, que cuente con la siguiente información:  * • Fecha  * • Tipo de evento  * • Equipo o infraestructura  * • Detalle labores  * • Responsable  En el caso de que esta labor la realice una empresa externa, debe existir un contrato e informe que acredite la realización de las actividades ejecutadas.",
      "action": "El predio realiza mantenciones y monitorea fugas de sus equipos con el objetivo de asegurar una adecuada calidad en la aplicación de agroquímicos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P055",
      "link": "https://ciruelacertificada.cl/?s=P055&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "483",
        "626",
        "771",
        "916"
      ],
      "good_practice": "Realizar limpieza y mantención adecuada de productos y equipos de aplicación de agroquímicos",
      "verification_type": "Bitácora"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro actualizado de aplicaciones con la siguiente información:  * Fecha y hora.  * Sector o cuartel.  * Nombre del producto.  * Ingrediente activo.  * Dosis.  * Dosis recomendada por fabricante.  * Método de aplicación.  * Objetivo de la aplicación.  * Período de carencia y de reingreso.  * Responsable.",
      "action": "El predio se rige por las dosis indicadas en la etiqueta del fabricante para la aplicación de agroquímicos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P056",
      "link": "https://ciruelacertificada.cl/?s=P056&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "509",
        "627",
        "772",
        "917"
      ],
      "good_practice": "Emplear de manera segura los productos agroquímicos en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro actualizado de aplicaciones con la siguiente información:  * Fecha y hora.  * Factores meteorológicos (temperatura, velocidad del viento y evento de lluvia).  * Sector o cuartel.  * Nombre del producto.  * Ingrediente activo.  * Dosis.  * Dosis recomendada por fabricante.  * Método de aplicación.  * Objetivo de la aplicación.  * Período de carencia y de reingreso.  * Responsable.  Se sugiere utilizar estación meteorológica propia o datos de portales como http://agroclima.cl o https://agrometeorologia.cl/",
      "action": "El predio considera las condiciones climáticas para las aplicaciones de agroquímicos, realizándolas bajo las siguientes condiciones:  - Temperaturas entre 10° y 30°C.  - Velocidad del viento entre 3 y 15 km/h.  - Ausencia de lluvia entre 2 a 8 horas después de la aplicación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P057",
      "link": "https://ciruelacertificada.cl/?s=P057&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Insumos",
      "linked_resources": [
        "510",
        "628",
        "773",
        "918"
      ],
      "good_practice": "Emplear de manera segura los productos agroquímicos en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro actualizado que contiene la siguiente información:  - Identificación del tipo de residuo o agente contaminante.  - Identificación de la cantidad producida mensualmente.  - Identificación de los residuos peligrosos.  - Ubicación dentro de la planta.  - Destino del residuo (reciclaje, reúso, eliminación, etc.).",
      "action": "El predio identifica los residuos sólidos generados y las posibles fuentes de contaminación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P058",
      "link": "https://ciruelacertificada.cl/?s=P058&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "518",
        "629",
        "774",
        "919"
      ],
      "good_practice": "Contar con un plan de manejo de residuos",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Plan de manejo de residuos que contenga los siguientes contenidos:  * Protocolos de almacenamiento de residuos peligrosos.  * Manejo de residuos para reciclaje o reutilización.  * Medidas de mitigación en caso de contaminación.  * Descripción del proceso y los puntos en que se generan residuos.  * Procedimientos internos para recoger y almacenar los residuos.  •Identificación de alternativas de minimización, valorización y eliminación de residuos.",
      "action": "El predio ha generado y documentado un plan de manejo de residuos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P059",
      "link": "https://ciruelacertificada.cl/?s=P059&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "630",
        "775",
        "920"
      ],
      "good_practice": "Contar con un plan de manejo de residuos",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual del área de almacenamiento, corroborando que los residuos se encuentren dentro de los contenedores correspondientes, evitando el contacto directo con el suelo, con el objetivo de no generar contaminación (ejemplo: radier y techo).",
      "action": "El predio manipula los residuos (sólidos y/o líquidos) de manera tal, que no generen derrames que contaminen el suelo y/o el agua.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P060",
      "link": "https://ciruelacertificada.cl/?s=P060&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "631",
        "776",
        "921"
      ],
      "good_practice": "Minimizar la contaminación derivada de la gestión de los residuos",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo que cuente con las siguientes medidas para minimizar la contaminación:  * No se permite la quema ni incineración de los desechos derivados de la producción.  * Los caminos son pavimentados o se aplica un suspensor de polvo químico o gravilla para evitar el aumento de la polución.  * Se realiza mantención a los equipos que utilizan combustibles fósiles internos, para evitar contaminación debido a fallas mecánicas.",
      "action": "El predio implementa un protocolo para minimizar la contaminación atmosférica por material particulado al interior de sus dependencias.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P061",
      "link": "https://ciruelacertificada.cl/?s=P061&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "484",
        "632",
        "777",
        "922"
      ],
      "good_practice": "Minimizar la contaminación derivada de la gestión de los residuos",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de señaléticas en lugares de riesgo de contaminación, que contemple los siguientes elementos:  - Información sobre acciones de mitigación inmediata.  - Información de contacto con servicios de emergencia y autoridades locales.",
      "action": "El predio cuenta con señaléticas para las situaciones de emergencia por contaminación por derrame de residuos líquidos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P062",
      "link": "https://ciruelacertificada.cl/?s=P062&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "514",
        "633",
        "778",
        "923"
      ],
      "good_practice": "Minimizar la contaminación derivada de la gestión de los residuos",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada).",
      "action": "El predio capacita a su personal en la implementación del protocolo de gestión de emergencias por contaminación por derrame de residuos líquidos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P063",
      "link": "https://ciruelacertificada.cl/?s=P063&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "551",
        "634",
        "779",
        "924"
      ],
      "good_practice": "Minimizar la contaminación derivada de la gestión de los residuos",
      "verification_type": "Foto"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Certificados de recepción de envases.  Más información respecto a la técnica de triple lavado y de lugares de recepción de",
      "action": "El predio somete a un triple lavado los envases derivados de la aplicación de agroquímicos, en conformidad con lo descrito en el programa “Campo limpio”. Posteriormente, son entregados o retirados por empresas u organizaciones encargadas de su revalorización.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P064",
      "link": "https://ciruelacertificada.cl/?s=P064&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "635",
        "780",
        "925"
      ],
      "good_practice": "Gestionar adecuadamente los residuos derivados de la producción",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de zona de almacenamiento de residuos peligrosos.",
      "action": "El predio almacena los residuos peligrosos, (por ejemplo: los aceites lubricantes derivados de vehículos y maquinarias utilizadas en la explotación), en bodegas exclusivas para este tipo de material.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P065",
      "link": "https://ciruelacertificada.cl/?s=P065&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "636",
        "781",
        "926"
      ],
      "good_practice": "Gestionar adecuadamente los residuos derivados de la producción",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Informe que certifique el retiro y la posterior reutilización de los residuos, realizado por la empresa autorizada a cargo de la gestión.",
      "action": "El predio gestiona los residuos de aceites lubricantes derivados de vehículos y maquinarias utilizadas en la explotación, a través de empresas especializadas en su posterior valorización.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P066",
      "link": "https://ciruelacertificada.cl/?s=P066&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "637",
        "782",
        "927"
      ],
      "good_practice": "Gestionar adecuadamente los residuos derivados de la producción",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de la existencia de contenedores y señaléticas informativas con respecto a la gestión de residuos para reciclaje de:  - PET y otros plásticos.  - Tetra brick.  - Papeles y cartones.  - Vidrios.  - Latas y otros metales.  - Residuos peligrosos.  - Residuos no reciclables.",
      "action": "La planta disminuye sus residuos enviados a gestores autorizados a través de la segregación, almacenamiento y entrega para su valorización, basándose en sus características y en las opciones de reciclaje disponibles.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P067",
      "link": "https://ciruelacertificada.cl/?s=P067&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "515",
        "516",
        "517",
        "638",
        "783",
        "928"
      ],
      "good_practice": "Gestionar residuos inorgánicos a través de técnicas de valorización y reciclaje",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada).",
      "action": "El predio capacita al personal sobre la relevancia del reciclaje y los procedimientos apropiados para su implementación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P068",
      "link": "https://ciruelacertificada.cl/?s=P068&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "552",
        "639",
        "784",
        "929"
      ],
      "good_practice": "Gestionar residuos inorgánicos a través de técnicas de valorización y reciclaje",
      "verification_type": "Foto"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro actualizado que contiene la siguiente información:  - Identificación del tipo de residuo orgánico.  - Identificación de la cantidad producida mensualmente.  - Ubicación dentro de la planta.  - Destino del residuo (reciclaje, reúso, etc.).",
      "action": "El predio reutiliza la materia orgánica generada en sus procesos, a través de al menos, una de las siguientes técnicas:  - Compostaje.  - Lombricultura.  - Reincorporación (picado o rastraje).  - Venta o donación a otras explotaciones.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P069",
      "link": "https://ciruelacertificada.cl/?s=P069&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Residuos",
      "linked_resources": [
        "640",
        "785",
        "930"
      ],
      "good_practice": "Compostar la materia orgánica generada utilizando el compost en su actividad productiva",
      "verification_type": "Bitácora"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Registro de consumo energético actualizado mensualmente que contenga la siguiente información:  - Tipo de fuente de energía (diésel, gas, gasolina y/o energía eléctrica).  - Consumo energético mensual (kWhe).  - Gasto en energía ($/mes).",
      "action": "El predio establece un sistema de registro mensual del consumo de energía.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P070",
      "link": "https://ciruelacertificada.cl/?s=P070&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "525",
        "641",
        "786",
        "931"
      ],
      "good_practice": "Implementar un sistema de gestión de la energía",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Reporte de diagnóstico energético con levantamiento de información para la identificación de consumo cuenta con:  * Registros mensuales de consumo energético.  * Identificación de equipos y su consumo energético. (Identificar las áreas críticas en cuanto a consumo).  * Identificación de períodos de alto consumo energético por mes (estacional o continuo)..  * Registro de mantenimiento de equipos.  * Definición del indicador de consumo en base a la producción.  * Identificación de capacitaciones en el ámbito de energía.  * Identificación de oportunidades de mejora y costos, tiempo de implementación, necesidades adicionales (construcción, capacitación, remodelación, entre otras).  En el caso de que lo haga una empresa externa, ésta deberá entregar un informe que certifique las acciones realizadas para entregar el diagnóstico.",
      "action": "El predio cuenta con un diagnóstico energético actualizado.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P071",
      "link": "https://ciruelacertificada.cl/?s=P071&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "523",
        "642",
        "787",
        "932"
      ],
      "good_practice": "Implementar un sistema de gestión de la energía",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada).",
      "action": "El predio implementa un plan de capacitación para su personal, abordando la gestión eficiente de la energía.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P072",
      "link": "https://ciruelacertificada.cl/?s=P072&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "553",
        "643",
        "788",
        "933"
      ],
      "good_practice": "Implementar un sistema de gestión de la energía",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Documento con un sistema de gestión de la energía que considere la siguiente información:  * Determinación del alcance del sistema de gestión de la energía.  * Línea de base energética a través de un indicador de eficiencia energética indicando el año de la línea base (kWh /kilo de fruta seca).  * Una meta de intensidad energética.",
      "action": "El predio implementa un sistema de gestión de la energía.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P073",
      "link": "https://ciruelacertificada.cl/?s=P073&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "524",
        "644",
        "789",
        "934"
      ],
      "good_practice": "Implementar un sistema de gestión de la energía",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de señaléticas de uso eficiente de energía en espacios de trabajo con la siguiente información:  * Apaga la luz antes de salir.  * Cierra la puerta al salir.  * Recordar mantenciones preventivas.  * Regular el consumo de agua caliente.",
      "action": "El predio cuenta con señalética que promueve el uso eficiente de la energía.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P074",
      "link": "https://ciruelacertificada.cl/?s=P074&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "520",
        "521",
        "522",
        "645",
        "790",
        "935"
      ],
      "good_practice": "Implementar medidas de eficiencia energética relacionadas al plan de gestión",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de señaléticas en área de guardado de vehículos que apunten a las siguientes medidas.  - Control de la presión de los neumáticos.  - Reducción del peso de la carga en los vehículos.  - Conducción eficiente a velocidades inferiores a 20 km/h.  - Combina viajes y evita los que son innecesarios.  - Conduce suavemente, evitando aceleraciones y frenadas bruscas.  - Condiciones climáticas: El viento en contra y las temperaturas extremas pueden aumentar el consumo de combustible.",
      "action": "El predio implementa medidas para mejorar la eficiencia de los vehículos dentro de la explotación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P075",
      "link": "https://ciruelacertificada.cl/?s=P075&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "519",
        "646",
        "791",
        "936"
      ],
      "good_practice": "Implementar medidas de eficiencia energética relacionadas al plan de gestión",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ambiente",
      "verification_detail": "Check list o registro de mantención de equipos, maquinarias y vehículos, con los siguientes datos:  • Fecha  • Tipo de evento  • Equipo o infraestructura  • Detalle labores  • Responsable  En el caso de que las mantenciones las realice una empresa externa, esta debe entregar un comprobante o informe que certifique que las acciones realizadas estén en función de lo solicitado.",
      "action": "El predio realiza mantención de equipos, maquinarias y vehículos, una vez durante la temporada o más frecuentemente si las indicaciones del fabricante lo estipulan, asegurando un adecuado funcionamiento y uso eficiente de la energía.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P076",
      "link": "https://ciruelacertificada.cl/?s=P076&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "485",
        "647",
        "792",
        "937"
      ],
      "good_practice": "Implementar medidas de eficiencia energética relacionadas al plan de gestión",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Documento con estudio de prefactibilidad técnico económica.  En el caso de que lo haga una empresa externa, esta debe entregar un informe que certifique que las acciones realizadas estén en función de lo solicitado.",
      "action": "El predio evalúa la prefactibilidad técnica y económica de incorporar energías renovables dentro de su sistema productivo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P077",
      "link": "https://ciruelacertificada.cl/?s=P077&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "648",
        "793",
        "938"
      ],
      "good_practice": "Implementar sistemas de energías renovables",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Inspección visual de alguno de los siguientes tipos de energía.  - Energía solar.  - Eólica.  - Mini hidroeléctrica.  - Biomasa o biogás.",
      "action": "La planta utiliza sistemas de energía renovable para autoconsumo energético.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P078",
      "link": "https://ciruelacertificada.cl/?s=P078&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Energía",
      "linked_resources": [
        "649",
        "794",
        "939"
      ],
      "good_practice": "Implementar sistemas de energías renovables",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de emisiones y capturas que incluya, fecha, monitoreo, periodo, balance de los siguientes aspectos:  Emisiones directas de GEI  • Combustión estacionaria  • Combustión móvil  • Uso suelo, cambios en el uso de suelo y silvicultura  • Procesos industriales  • Emisiones fugitivas  Emisiones indirectas de GEI causadas por energía importada  • Electricidad importada  • Otra energía importada y/o pérdidas T&D  Otras emisiones indirectas de GEI  • Transporte  • Bienes y servicios utilizados  • Uso de productos de la organización  *Se recomienda el uso de la plataforma de Huella Chile para cuantificar emisiones.  En el caso de que lo haga una empresa externa, esta debe entregar un informe que certifique que las acciones realizadas estén en función de lo solicitado.",
      "action": "El predio cuantifica sus emisiones directas e indirectas de GEI de la unidad y define una línea base en las principales etapas de su producción.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P079",
      "link": "https://ciruelacertificada.cl/?s=P079&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "526",
        "529",
        "650",
        "795",
        "940"
      ],
      "good_practice": "Cuantificar emisiones de GEI en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Reporte anual de emisiones y capturas, con indicación de la metodología empleada y los resultados obtenidos.  En el caso de que lo haga una empresa externa, esta debe entregar un informe que certifique que las acciones realizadas estén en función de lo solicitado.",
      "action": "El predio monitorea periódicamente los GEI de la unidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P080",
      "link": "https://ciruelacertificada.cl/?s=P080&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "527",
        "530",
        "651",
        "796",
        "941"
      ],
      "good_practice": "Cuantificar emisiones de GEI en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Ambiente",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada).",
      "action": "El predio implementa un plan de capacitación para el personal, que aborda la problemática asociada al cambio climático y conceptos sobre cuantificación y mitigación de emisión de GEI.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P081",
      "link": "https://ciruelacertificada.cl/?s=P081&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "554",
        "652",
        "797",
        "942"
      ],
      "good_practice": "Reducir las emisiones y promover las capturas de GEI en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Protocolo para reducir las emisiones de GEI.",
      "action": "El predio cuenta con un protocolo para reducir sus emisiones de GEI que contempla, por ejemplo, alguna de las siguientes medidas:  • Usar maquinaria agrícola eficiente energéticamente.  • Optimiza las distancias de transporte en el campo para lograr reducciones en el uso de combustible.  • Utiliza luminarias LED en bodegas, salas de empaque y oficinas para disminuir consumo eléctrico.  • Cambia de combustibles fósiles a electricidad de la red o paneles solares en el sistema de bombeo para riego.  • Emplea métodos de labranza de conservación que promueven la captura de carbono en el suelo, como mínima labranza y los cultivos de cobertura.  • Usa fertilizantes de formulación avanzada para reducir emisiones.  • Recicla, composta y valoriza los residuos orgánicos generados en el huerto y sus procesos.  • No utiliza fuego para la preparación de tierra o la eliminación en el campo de los residuos derivados de la producción.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P082",
      "link": "https://ciruelacertificada.cl/?s=P082&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "528",
        "653",
        "798",
        "943"
      ],
      "good_practice": "Reducir las emisiones y promover las capturas de GEI en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Plan de reducción, control y respuesta frente a riesgos de desastres, vinculados al Cambio Climático que contenga al menos la siguiente información:  *Listado de las amenazas o peligros (internas y externas) según su origen, y evaluación de recursos y vulnerabilidades para enfrentar cada una de ellas  * Programas de trabajo en sus fases de prevención, respuesta y recuperación.  *Definición de responsables y de mecanismos para asignación de recursos que financien los programas de trabajo que surjan del plan.  * Realización de simulaciones y simulacros.  El plan debe ser evaluado posterior a la ocurrencia de cada evento de emergencia o desastre.",
      "action": "La planta elabora e implementa un plan de reducción, control y respuesta frente a riesgo de desastres, vinculados al Cambio Climático. La elaboración del plan contempla determinar las amenazas históricas y proyectadas, identificar los recursos mínimos y capacidades para abordar las amenazas, y determinar las debilidades respecto de los recursos y capacidades requeridas. Las medidas del plan se elaboran en función de las debilidades detectadas y su respectiva priorización.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P083",
      "link": "https://ciruelacertificada.cl/?s=P083&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "654",
        "799",
        "944"
      ],
      "good_practice": "Elaborar un plan de reducción de riesgo de desastres",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de eventos meteorológicos significativos, indicando la fuente de obtención de la información (estación meteorológica propia o datos de portales como http://agroclima.cl/ o https://agrometeorologia.cl/ , de los siguientes puntos:  * Altas temperaturas (más de 30°C).  * Bajas temperaturas (menos de 4°C).  * Lluvias.  * Fuente de obtención de la información.  Este registro debe ser actualizado de manera mensual.",
      "action": "El predio incorpora monitoreo de parámetros de la situación meteorológica propia o cercana, para visualizar periodos de sequías extremas, altas y bajas temperaturas, y episodios de alta pluviometría.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P084",
      "link": "https://ciruelacertificada.cl/?s=P084&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "655",
        "800",
        "945"
      ],
      "good_practice": "Elaborar un plan de reducción de riesgo de desastres",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de ejecución de capacitaciones (lista de asistencia identificando sexo de quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada).",
      "action": "La planta capacita al personal sobre el un plan de reducción, control y respuesta frente a riesgo de desastres, vinculados al Cambio Climático, para evitar que sean susceptibles a sufrir daños o pérdidas por efecto de las amenazas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P085",
      "link": "https://ciruelacertificada.cl/?s=P085&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "656",
        "801",
        "946"
      ],
      "good_practice": "Elaborar un plan de reducción de riesgo de desastres",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ambiente",
      "verification_detail": "Registro de monitoreo de erosión de suelo que considere los siguientes aspectos:  * Presencia de zanjas o corrugado en laderas con más de 10%.  * Presencia de cubiertas vegetales vivas.  * Presencia de cubierta vegetales inertes.  * Presencia/ausencia de infraestructura de protección contra aluviones (zanjas, muros de contención y de derivación de caudales).",
      "action": "El predio evalúa las condiciones de degradación del suelo, monitoreando la presencia de signos de erosión.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P086",
      "link": "https://ciruelacertificada.cl/?s=P086&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gases de Efecto Invernadero (GEI)",
      "linked_resources": [
        "657",
        "802",
        "947"
      ],
      "good_practice": "Elaborar un plan de reducción de riesgo de desastres",
      "verification_type": "Foto"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Calidad",
      "verification_detail": "Protocolo para la gestión eficiente de los PCC con las siguientes medidas.  - Grado de maduración de la fruta en base a acuerdos con clientes (brix, color, tamaño).  - Aplicación de agroquímicos cumpliendo con los límites máximos de residuos.  - Humedad de secado (cancha u horno).  - Otros identificados por la empresa.",
      "action": "El predio identifica y gestiona de manera eficiente los principales puntos críticos de control (PCC) para la obtención de ciruelas para deshidratado.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P087",
      "link": "https://ciruelacertificada.cl/?s=P087&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "658",
        "803",
        "948"
      ],
      "good_practice": "Poseer una política de calidad y de mejora continua en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Registro de acciones de control de calidad realizadas en el predio:  - Medición de niveles de grados brix en la fruta.  - Medición de firmeza en la fruta.  - Registro de identificación de defectos en la fruta.",
      "action": "El predio establece un procedimiento de control de calidad de la fruta cosechada.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P088",
      "link": "https://ciruelacertificada.cl/?s=P088&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "531",
        "659",
        "804",
        "949"
      ],
      "good_practice": "Poseer una política de calidad y de mejora continua en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Documentación de la ejecución de capacitaciones (lista de asistencia identificando sexo del participante, tema expuesto, expositor, material expuesto y certificación entregada).",
      "action": "El predio posee procedimiento de control de calidad de la fruta conocida por las personas que trabajan en él.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P089",
      "link": "https://ciruelacertificada.cl/?s=P089&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "555",
        "660",
        "805",
        "950"
      ],
      "good_practice": "Poseer una política de calidad y de mejora continua en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Informes de los controles de calidad desde planta, que justifiquen la no conformidad del producto.",
      "action": "El predio establece canales de comunicación con sus contrapartes directas en planta, para gestionar de manera oportuna los reclamos y no conformidades del proceso agroindustrial.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P090",
      "link": "https://ciruelacertificada.cl/?s=P090&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "661",
        "806",
        "951"
      ],
      "good_practice": "Poseer una política de calidad y de mejora continua en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Comprobante de auditoría interna, que permita verificar que se cumple con los requisitos de las certificaciones aplicables (con su respectiva periodicidad).",
      "action": "El predio gestiona sus auditorías internas, en base los riesgos asociados, para evaluar el nivel de cumplimiento de su política de gestión de calidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P091",
      "link": "https://ciruelacertificada.cl/?s=P091&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "662",
        "807",
        "952"
      ],
      "good_practice": "Poseer una política de calidad y de mejora continua en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Documento de registro del producto cosechado con la siguiente información:  - Fecha de cosecha.  - Total de producción cosechada al día (kg).  - Sector o cuartel cosechado.  - Tipo de secado posterior (horno o cancha).  - Empresa agroindustrial de destino.",
      "action": "El predio mantiene registros de todo su producto cosechado dentro de la explotación.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P092",
      "link": "https://ciruelacertificada.cl/?s=P092&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "532",
        "663",
        "808",
        "953"
      ],
      "good_practice": "Documentar los procesos productivos realizados en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Cuaderno de campo con labores productivas indicando:  - Fecha y hora.  - Sector o cuartel.  - Labor realizada.  - Objetivo.  - Responsable.",
      "action": "El predio registra todas las labores productivas realizadas y las personas responsables de su ejecución.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P093",
      "link": "https://ciruelacertificada.cl/?s=P093&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "494",
        "533",
        "664",
        "809",
        "954"
      ],
      "good_practice": "Documentar los procesos productivos realizados en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Inventario de los insumos que dé cuenta de la siguiente información:  - Nombre del producto.  - Fecha de compra.  - Número de lote y proveedor.  - Unidades adquiridas.  - Volumen utilizado.  - Fecha de caducidad o vencimiento.",
      "action": "El predio lleva un inventario de sus insumos para llevar una adecuada gestión de la calidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P094",
      "link": "https://ciruelacertificada.cl/?s=P094&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "665",
        "810",
        "955"
      ],
      "good_practice": "Documentar los procesos productivos realizados en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Registro de ventas con documentos tributarios asociados:  * Facturas.  * Guías de despacho.",
      "action": "El predio maneja un registro de sus ventas para llevar una adecuada gestión de la calidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P095",
      "link": "https://ciruelacertificada.cl/?s=P095&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "666",
        "811",
        "956"
      ],
      "good_practice": "Documentar los procesos productivos realizados en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Registro de trazabilidad en el predio que permita rastrear los siguientes aspectos:  - Identificación del campo o cuarteles.  - Variedad o especie.  - Superficie.  - Año de plantación.  Además, debe contar con los registros de labores actualizados en el cuaderno de campo.",
      "action": "El predio posee un protocolo de trazabilidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P096",
      "link": "https://ciruelacertificada.cl/?s=P096&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "534",
        "667",
        "812",
        "957"
      ],
      "good_practice": "Poseer un sistema de trazabilidad del producto a lo largo de todas sus etapas de producción",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Registro con el N° de guía de despacho o lote interno en la tarja del producto.",
      "action": "El predio asegura que sus productos posean un código que le permite rastrear la información sobre todos sus procesos productivos, al momento de llegar a la planta.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P097",
      "link": "https://ciruelacertificada.cl/?s=P097&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Calidad",
      "linked_resources": [
        "668",
        "813",
        "958"
      ],
      "good_practice": "Poseer un sistema de trazabilidad del producto a lo largo de todas sus etapas de producción",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Calidad",
      "verification_detail": "Inspección visual de las señaléticas con las siguientes temáticas:  - Procedimientos de limpieza.  - Prohibición de labores ante sospecha de enfermedades contagiosas.  - Manipulación de alimentos (lavado de manos, contaminación por agentes externos).",
      "action": "El predio utiliza señaléticas para promover prácticas sobre inocuidad e higiene.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P098",
      "link": "https://ciruelacertificada.cl/?s=P098&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "564",
        "565",
        "669",
        "814",
        "959"
      ],
      "good_practice": "Poseer una política de inocuidad para la producción",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Protocolo que contenga la siguiente información:  - Realizar análisis de riesgos.  - Determinar Puntos Críticos de Control (PCC).  - Establecer límites críticos.  - Establecer procedimientos de monitoreo.  - Establecer medidas correctivas.  - Establecer procedimientos de comprobación auditables.",
      "action": "El predio posee un plan de gestión de la inocuidad, que garantiza que los productos cumplan con los requerimientos de calidad y seguridad requeridos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P099",
      "link": "https://ciruelacertificada.cl/?s=P099&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "670",
        "815",
        "960"
      ],
      "good_practice": "Poseer una política de inocuidad para la producción",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Calidad",
      "verification_detail": "Comprobante de auditoría interna, que permita verificar que se cumple con los requisitos de inocuidad, al menos una vez por año.",
      "action": "El predio realiza auditorías internas anuales, para evaluar el nivel de cumplimiento de su política de inocuidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P100",
      "link": "https://ciruelacertificada.cl/?s=P100&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "671",
        "816",
        "961"
      ],
      "good_practice": "Poseer una política de inocuidad para la producción",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Calidad",
      "verification_detail": "Inspección visual de los espacios de disposición temporal de la fruta, asegurando que estos posean sombras y no se ubiquen cerca de agentes contaminantes.",
      "action": "El predio cuenta con un lugar adecuado para la disposición temporal de la fruta cosechada (antes de ser enviada a secado), impidiendo el contacto con contaminantes o vectores.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P101",
      "link": "https://ciruelacertificada.cl/?s=P101&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "672",
        "817",
        "962"
      ],
      "good_practice": "Asegurar la inocuidad de los insumos, espacios, equipos e indumentarias requeridas para la producción",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Calidad",
      "verification_detail": "Registro actualizado de aplicaciones con la siguiente información:  * Fecha y hora.  * Sector o cuartel.  * Nombre del producto.  * Ingrediente activo.  * Dosis.  * Dosis recomendada por fabricante.  * Método de aplicación.  * Objetivo de la aplicación.  * Período de carencia y de reingreso.  * Responsable.",
      "action": "El predio se asegura de que los insumos aplicados en las labores productivas, no representen un riesgo para la inocuidad alimentaria, utilizando productos autorizados para las ciruelas y respetando los periodos de carencia.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P102",
      "link": "https://ciruelacertificada.cl/?s=P102&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Gestión de la Inocuidad",
      "linked_resources": [
        "673",
        "818",
        "963"
      ],
      "good_practice": "Asegurar la inocuidad de los insumos, espacios, equipos e indumentarias requeridas para la producción",
      "verification_type": "Bitácora"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Gestión",
      "verification_detail": "Documento de identificación de puntos críticos dentro de la producción.",
      "action": "El predio identifica los principales puntos críticos de su producción y busca mejoras para aumentar su productividad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P103",
      "link": "https://ciruelacertificada.cl/?s=P103&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "674",
        "819",
        "964"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad del predio",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Gestión",
      "verification_detail": "Documento de planificación que contenga los siguientes puntos:  - Presupuesto.  - Proyecciones de ventas.  - Organigrama y descripción de cargos dentro de la empresa.",
      "action": "El predio cuenta con un plan de gestión de productividad y rentabilidad, que le permite definir indicadores de gestión y asegurar su viabilidad a largo plazo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P104",
      "link": "https://ciruelacertificada.cl/?s=P104&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "675",
        "820",
        "965"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad del predio",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Gestión",
      "verification_detail": "Registro de visitas de asesores/as o registro de visitas a ferias tecnológicas o cotizaciones de tecnologías o servicios. El registro deberá tener como máximo 1 año de antigüedad.  Adicionalmente, se requiere un listado con las inversiones implementadas, indicando la temática a la que corresponde (agua, energía, residuos, etc.).",
      "action": "En el predio se evalúa la adopción de nuevas prácticas y tecnologías considerando su contribución a la productividad y/o rentabilidad.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P105",
      "link": "https://ciruelacertificada.cl/?s=P105&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "481",
        "535",
        "676",
        "821",
        "966"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad del predio",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Gestión",
      "verification_detail": "Documentos de registro de los siguientes aspectos:  - Inventario de productos entrantes y salientes.  - Registro contable de la empresa.",
      "action": "El predio cuenta con un sistema de gestión contable, que considera registros de inventario, control de gastos, ingresos y utilidades derivadas del proceso productivo.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P106",
      "link": "https://ciruelacertificada.cl/?s=P106&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "536",
        "677",
        "822",
        "967"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad del predio",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Gestión",
      "verification_detail": "Registro de licencia o suscripción a plataforma digital específica para la gestión agrícola.",
      "action": "El predio cuenta con una herramienta de gestión digital, que facilita la implementación de medidas y registros.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P107",
      "link": "https://ciruelacertificada.cl/?s=P107&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "678",
        "823",
        "968"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad del predio",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Gestión",
      "verification_detail": "Son válidos alguno de los siguientes documentos:  * Contrato de servicios de una persona que realiza asesorías financieras.  * Descripción de cargos y CV de la persona encargada del área financiera.",
      "action": "El predio cuenta con una persona encargada o una persona que realiza asesoría financiera.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P108",
      "link": "https://ciruelacertificada.cl/?s=P108&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "679",
        "824",
        "969"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad del predio",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Gestión",
      "verification_detail": "Actas de reuniones realizadas con la “comunidad de práctica”.",
      "action": "El predio forma parte de una \"comunidad de práctica\", que le permite realizar una evaluación de cambio tecnológico, en conjunto con otras empresas de la industria a nivel territorial.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P109",
      "link": "https://ciruelacertificada.cl/?s=P109&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "562",
        "680",
        "825",
        "970"
      ],
      "good_practice": "Mejorar la productividad y rentabilidad del predio",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Gestión",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada) o certificado de participación en instancias de capacitación externa (cursos, seminarios, congresos, etc.). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "Quienes trabajan como directivos o son tomadores de decisiones, participan en instancias de capacitación que les permite entender de mejor manera, el comportamiento del mercado de ciruelas deshidratadas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P110",
      "link": "https://ciruelacertificada.cl/?s=P110&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "556",
        "681",
        "826",
        "971"
      ],
      "good_practice": "Gestionar el predio para garantizar su viabilidad económica y financiera",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Gestión",
      "verification_detail": "Registro de planificación estratégica con una vigencia de máximo 5 años, que contenga la siguiente información:  - Diagnóstico que incorpore un FODA.  - Plan de implementación en base a los resultados del FODA, (ventajas competitivas para potenciar fortalezas, evitar debilidades y enfrentar amenazas).",
      "action": "El predio desarrolla una visión empresarial y planifica y decide, en base a información robusta de índole económica y financiera.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P111",
      "link": "https://ciruelacertificada.cl/?s=P111&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "682",
        "827",
        "972"
      ],
      "good_practice": "Gestionar el predio para garantizar su viabilidad económica y financiera",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Gestión",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada).",
      "action": "El predio capacita a su personal sobre estrategias de aumento de la productividad, para que puedan identificar los puntos críticos del proceso y conozcan las herramientas de optimización de la producción.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P112",
      "link": "https://ciruelacertificada.cl/?s=P112&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "557",
        "683",
        "828",
        "973"
      ],
      "good_practice": "Fomentar que las personas que trabajan en el predio, tengan acceso a la información de productividad y mercado",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Gestión",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada) o certificado de participación en instancias de capacitación externa (cursos, seminarios, congresos, etc.). Se verifica que al menos una persona atingente al área, haya recibido esta capacitación.",
      "action": "El predio capacita sus directivos y tomadores de decisiones en finanzas, costos de producción y gestión del negocio agrícola.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P113",
      "link": "https://ciruelacertificada.cl/?s=P113&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Viabilidad Económica",
      "linked_resources": [
        "558",
        "684",
        "829",
        "974"
      ],
      "good_practice": "Fomentar que las personas que trabajan en el predio, tengan acceso a la información de productividad y mercado",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Matriz de mapeo de actores con la identificación de los impactos generados con la siguiente información:  • Nombre de la organización/institución, actor  • Representante o contraparte  • Cargo  • Contacto  • Categoría de actor (empresa, comercio, residentes, servicios locales, etc.).  • Ubicación geográfica en el territorio  • Relaciones predominantes con la empresa  • Nivel de afectación (positiva y negativa) de las operaciones de la empresa.",
      "action": "El predio identifica los potenciales impactos, positivos o negativos, generados en las comunidades vecinas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P114",
      "link": "https://ciruelacertificada.cl/?s=P114&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "540",
        "701",
        "846",
        "975"
      ],
      "good_practice": "Evaluar el impacto generado en las comunidades locales",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Social",
      "verification_detail": "Matriz con las medidas de mitigación de los impactos generados que dé cuenta de la siguiente información:  • Efecto  • Acción  • Objetivo (fortalecer, prevenir, mitigar)  • Resultado esperado",
      "action": "El predio aplica medidas de mitigación para los impactos generados.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P115",
      "link": "https://ciruelacertificada.cl/?s=P115&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "541",
        "702",
        "847",
        "976"
      ],
      "good_practice": "Evaluar el impacto generado en las comunidades locales",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Social",
      "verification_detail": "Son válidos cualquiera de los documentos que se proponen a continuación.  - Portafolio de evidencia de las actividades realizadas, ej. proyectos realizados, imágenes, registros de convenios, canales de comunicación, minutas.  - Documentos que evidencien el tipo de iniciativa, la fecha, la ubicación, los montos y/o las horas profesionales invertidas.",
      "action": "El predio apoya con aportes pecuniarios y no pecuniarios, proyectos o iniciativas que abordan las necesidades y prioridades de la comunidad, con el fin de mejorar la calidad de vida de sus habitantes en temas como: educación, salud, capacitación, saneamiento, problemas ambientales, deporte, infraestructura comunitaria o pública, con acciones de RES u otras.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P116",
      "link": "https://ciruelacertificada.cl/?s=P116&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "543",
        "703",
        "848",
        "977"
      ],
      "good_practice": "Contribuir al desarrollo local",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Son válidos algunos de los siguientes documentos:  - Registro de documento tributario que acredite compras a empresas locales.  - Existencia de contratos de compra con proveedores locales.",
      "action": "El predio contribuye a la economía local, comprando los bienes y servicios, que no son claves para la producción, a personas o empresas locales a nivel provincial. Por ejemplo: materiales de oficina, productos de aseo, alimentación, vestimenta, etc.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P117",
      "link": "https://ciruelacertificada.cl/?s=P117&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "704",
        "849",
        "978"
      ],
      "good_practice": "Contribuir a la economía local",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Social",
      "verification_detail": "Son válidos algunos de los siguientes documentos:  - Registro de contratos laborales.  - Registro de ofertas laborales en la OMIL local.",
      "action": "El predio promueve la contratación de personas, mediante la difusión de ofertas laborales a los habitantes de la misma provincia, ya sea trabajo temporal o permanente.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P118",
      "link": "https://ciruelacertificada.cl/?s=P118&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "544",
        "705",
        "850",
        "979"
      ],
      "good_practice": "Contribuir a la economía local",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Social",
      "verification_detail": "Registro de contratos identificando a personas de la provincia.",
      "action": "El predio cuenta con, al menos, un 90% del personal contratado (de manera permanente) de la misma provincia.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P119",
      "link": "https://ciruelacertificada.cl/?s=P119&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "706",
        "851",
        "980"
      ],
      "good_practice": "Contribuir a la economía local",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Portafolio que registre los canales de comunicación con la comunidad, por ejemplo: acta de reuniones con la JJVV, anuncios en radios locales, publicaciones en el diario mural de la junta de vecinos, mensajes de WhatsApp, etc.",
      "action": "El predio cuenta con canales de comunicación efectivos para informar a las comunidades locales, sobre la faena que podría impactar positiva o negativamente en el entorno o territorio, y otras actividades que se quieran comunicar.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P120",
      "link": "https://ciruelacertificada.cl/?s=P120&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "545",
        "707",
        "852",
        "981"
      ],
      "good_practice": "Mantener un sistema de comunicación efectivo con la comunidad",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Registros del libro de reclamos y sugerencias, además de las soluciones implementadas:  * Nombre  * Fecha  * Correo electrónico  * Teléfono  * Reclamo o sugerencia  * Encargado de gestionar  * Resolución.  * Fecha resolución",
      "action": "El predio dispone de un mecanismo de gestión de reclamos y sugerencias, a disposición de las comunidades locales, y además, mantiene un registro de las mismas y de cómo se han abordado.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P121",
      "link": "https://ciruelacertificada.cl/?s=P121&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "542",
        "708",
        "853",
        "982"
      ],
      "good_practice": "Mantener un sistema de comunicación efectivo con la comunidad",
      "verification_type": "Bitácora"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Social",
      "verification_detail": "Son válidos alguno de los siguientes documentos:  - Identificación de la persona encargada o responsable, a través del organigrama o la descripción de cargos.  - Convenio con la institución que realiza los trabajos comunitarios.",
      "action": "El predio cuenta con una persona responsable de coordinar, planificar y ejecutar proyectos de relacionamiento comunitario.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P122",
      "link": "https://ciruelacertificada.cl/?s=P122&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Comunidades Locales",
      "linked_resources": [
        "709",
        "854",
        "983"
      ],
      "good_practice": "Mantener un sistema de comunicación efectivo con la comunidad",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Inspección visual de las instalaciones o dispositivos dispensadores de agua potable.",
      "action": "El predio provee a quienes trabajan en él, acceso a agua potable suficiente y segura, destinada al consumo humano.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P123",
      "link": "https://ciruelacertificada.cl/?s=P123&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "685",
        "830",
        "984"
      ],
      "good_practice": "Disponer de instalaciones adecuadas y seguras para las personas que trabajan en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Inspección visual de los servicios higiénicos, espacios de protección para el sol, camarines, comedor o casino y áreas de descanso.  En el caso de empresas de menor tamaño (AFC) que subcontraten los servicios durante la temporada, estas deben entregar todos los registros antes mencionados.",
      "action": "El predio proporciona a quienes trabajan en él, instalaciones que cuenten con las siguientes características.  - Servicios higiénicos de uso individual o colectivo.  - Espacios de protección del sol y la lluvia.  - Instalaciones para cambiarse de ropa y las prendas exteriores de protección.  - Comedor o casino.  - Áreas designadas para el descanso y las pausas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P124",
      "link": "https://ciruelacertificada.cl/?s=P124&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "686",
        "831",
        "985"
      ],
      "good_practice": "Disponer de instalaciones adecuadas y seguras para las personas que trabajan en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Inspección visual de alojamientos que cuenten como mínimo, con agua, electricidad, instalaciones sanitarias, ventilación, pisos secos y lavables, temperaturas adecuadas y control de plagas.",
      "action": "El predio se asegura de que las personas y familias que viven de manera permanente o temporal en sus dependencias, cuenten con alojamiento seguro y limpio.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P125",
      "link": "https://ciruelacertificada.cl/?s=P125&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "687",
        "832",
        "986"
      ],
      "good_practice": "Disponer de instalaciones adecuadas y seguras para las personas que trabajan en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Registro actualizado de manera mensual con al menos, la siguiente información.  * Número mensual diferenciado por sexo.  * Número mensual de incidentes y accidentes.  * Número mensual de casos con enfermedades profesionales.  * Total mensual de días perdidos.  * Tasa de accidentabilidad.  * Licencias médicas.  En el caso de empresas de menor tamaño (AFC) que subcontraten los servicios durante la temporada, estas deben entregar todos los registros antes mencionados.",
      "action": "El predio mantiene un registro mensual de la gestión de la seguridad de las personas que trabajan en él.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P126",
      "link": "https://ciruelacertificada.cl/?s=P126&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "538",
        "688",
        "833",
        "987"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Inspección visual de señalética con protocolo de emergencias o accidentes que contiene la siguiente información.  - Teléfonos y contactos de emergencia.  - Medidas básicas de primeros auxilios.  - Mapas de ubicaciones de extintores y botiquines.  - Vías de evacuación.  - Zonas de seguridad dentro del predio.",
      "action": "El predio cuenta con un protocolo en caso de emergencia (sismos, incendios, fuga de gases, otros) o accidentes laborales. Los detalles del protocolo están claramente exhibidos en lugares accesibles y visibles.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P127",
      "link": "https://ciruelacertificada.cl/?s=P127&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "566",
        "567",
        "568",
        "569",
        "570",
        "571",
        "689",
        "834",
        "988"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Social",
      "verification_detail": "Contrato con profesional prevencionista o convenio con la Mutual de seguridad.",
      "action": "El predio cuenta con una persona a cargo del programa de prevención de riesgos (prevencionista de riesgos) o un convenio con una mutual que desarrolle esta labor.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P128",
      "link": "https://ciruelacertificada.cl/?s=P128&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "690",
        "835",
        "989"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Social",
      "verification_detail": "Credencial de aplicadores de plaguicidas capacitados, entregado por el SAG  En el caso de que esta labor la realice una empresa externa, debe existir un respaldo (copia) del certificado del aplicador/a.",
      "action": "En el predio, las tareas peligrosas, incluida la aplicación o manipulación de agroquímicos de alta toxicidad, se llevan a cabo únicamente por personal calificado y personas debidamente capacitadas.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P129",
      "link": "https://ciruelacertificada.cl/?s=P129&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "691",
        "836",
        "990"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Social",
      "verification_detail": "Registro de entrega de EPP firmados y actualizados con la siguiente información:  * Fecha.  * Nombre",
      "action": "El predio proporciona a quienes manipulan sustancias tóxicas, realizan tareas peligrosas o aplican pesticidas, los equipos de protección personal (EPP) correspondientes.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P130",
      "link": "https://ciruelacertificada.cl/?s=P130&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "539",
        "692",
        "837",
        "991"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en el predio",
      "verification_type": "Bitácora"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Documento con el programa de prevención de riesgos que contemple los siguientes aspectos:  o Identificación y evaluación de riesgos.  o Medidas preventivas y de protección.  o Vigilancia de la salud.  o Investigación de accidentes e incidentes.  En el caso de empresas de menor tamaño (AFC) que subcontraten los servicios durante la temporada, estas deben entregar todos los registros antes mencionados.",
      "action": "El predio implementa un programa de gestión de riesgos para quienes trabajan en él.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P131",
      "link": "https://ciruelacertificada.cl/?s=P131&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "537",
        "693",
        "838",
        "992"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Social",
      "verification_detail": "Registro de que las personas que manejan productos agroquímicos, cuentan con exámenes médicos vigentes (al menos un año). Por ejemplo: control de sangre preventivo, examen de colinesterasa, examen general (mutual).  En el caso de empresas de menor tamaño (AFC) que subcontraten los servicios durante la temporada, estas deben entregar todos los registros antes mencionados.",
      "action": "El predio somete a exámenes médicos, al menos una vez al año, a quienes normalmente estén expuestos a labores que puedan generar un riesgo para su salud (ruido, sustancias tóxicas, entre otros) y entrega los resultados a cada uno.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P132",
      "link": "https://ciruelacertificada.cl/?s=P132&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "694",
        "839",
        "993"
      ],
      "good_practice": "Velar y garantizar la salud y seguridad de las personas que trabajan en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Social",
      "verification_detail": "Documento con el Reglamento interno de la planta.  Lista de trabajadores/as identificados por sexo.",
      "action": "El predio no discrimina por raza, color, religión, género, nacionalidad, tendencia política, etc.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P133",
      "link": "https://ciruelacertificada.cl/?s=P133&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "695",
        "840",
        "994"
      ],
      "good_practice": "Velar por el bienestar social y laboral de las personas que trabajan en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada).",
      "action": "El predio capacita a su personal sobre cómo desempeñar las labores asociadas a su trabajo, buscando la eficiencia en su desempeño.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P134",
      "link": "https://ciruelacertificada.cl/?s=P134&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "559",
        "696",
        "841",
        "995"
      ],
      "good_practice": "Velar por el bienestar social y laboral de las personas que trabajan en el predio",
      "verification_type": "Foto"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Social",
      "verification_detail": "Portafolio de evidencia que respalde la existencia del programa con listado de potenciales instituciones u organizaciones de apoyo, públicas o privadas.",
      "action": "El predio cuenta con un programa para promover estilos de vida saludables y prevenir dependencias a drogas y alcohol.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P135",
      "link": "https://ciruelacertificada.cl/?s=P135&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "697",
        "842",
        "996"
      ],
      "good_practice": "Velar por el bienestar social y laboral de las personas que trabajan en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Social",
      "verification_detail": "Son válidos los siguientes documentos.  - Registro de información entregada al personal a través de correos electrónicos, folletos, publicaciones en diarios murales y/o registros de capacitaciones asociadas al tema.  - Registro de entrega del Reglamento interno.  - Registro de inducciones o documento con instrucciones respecto al puesto de trabajo.  En el caso de empresas de menor tamaño (AFC) que subcontraten los servicios durante la temporada, estas deben entregar todos los registros antes mencionados.",
      "action": "El predio se asegura de que su personal conozca sus derechos y obligaciones relacionados con la situación contractual con la empresa y las leyes laborales vigentes.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P136",
      "link": "https://ciruelacertificada.cl/?s=P136&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "698",
        "843",
        "997"
      ],
      "good_practice": "Respetar los derechos laborales de las personas que trabajan en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Social",
      "verification_detail": "Política o procedimiento de contratación del predio que indique lo siguiente:  - No supera el máximo de horas diarias y semanales permitidas.  - No supera el máximo de horas extras permitidas.  - Provee de pausas diarias para el almuerzo y el descanso.  - Otorga tiempo libre pagado por vacaciones y licencia por enfermedad.  - Posibilita la desvinculación voluntaria en casos específicos.  - Emplea prácticas de pago transparentes y justas.  En el caso de empresas de menor tamaño (AFC) que subcontraten los servicios durante la temporada, estas deben entregar todos los registros antes mencionados.",
      "action": "El predio respeta y adhiere a las leyes aplicables a los derechos laborales de su personal.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P137",
      "link": "https://ciruelacertificada.cl/?s=P137&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "699",
        "844",
        "998"
      ],
      "good_practice": "Respetar los derechos laborales de las personas que trabajan en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 3,
      "level": "Intermedio",
      "dimension": "Social",
      "verification_detail": "Son válidos los siguientes documentos de validación.  - Política o procedimientos de contratación.  - Registro de ofertas laborales del último año en las que se evidencie que no se solicita que la persona a contratar, pertenezca a un género específico.",
      "action": "El predio promueve la equidad de género en su política de contrataciones, evidenciando que no existe solicitud específica de género en sus ofertas laborales.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P138",
      "link": "https://ciruelacertificada.cl/?s=P138&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Condiciones de Trabajo y Protección Social",
      "linked_resources": [
        "700",
        "845",
        "999"
      ],
      "good_practice": "Respetar los derechos laborales de las personas que trabajan en el predio",
      "verification_type": "Archivo"
    },
    {
      "points": 5,
      "level": "Fundamental",
      "dimension": "Ética",
      "verification_detail": "Registro de la ejecución de capacitaciones (lista de asistencia identificando sexo quien participa, tema expuesto, persona que expone, material expuesto, registro fotográfico y certificación entregada).",
      "action": "Las personas que trabajan en el predio han sido capacitadas y conocen la legislación aplicable a sus labores.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P139",
      "link": "https://ciruelacertificada.cl/?s=P139&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida Diligencia de la Legislación",
      "linked_resources": [
        "560",
        "710",
        "855",
        "1000"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Foto"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ética",
      "verification_detail": "Inspección visual de documentos de registro archivados o documentos digitales almacenados.",
      "action": "El predio guarda los registros que acrediten el cumplimiento de las diferentes legislaciones o certificaciones, durante un plazo de al menos 5 años.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P140",
      "link": "https://ciruelacertificada.cl/?s=P140&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida Diligencia de la Legislación",
      "linked_resources": [
        "711",
        "856",
        "1001"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ética",
      "verification_detail": "Son válidos los siguientes documentos de validación.  - Escritura de propiedad que verifique el uso de suelo.  - Copia de instrumentos de ordenamiento territorial que verifiquen uso de suelo.",
      "action": "El predio demuestra un título o contrato de uso de tierra claro en conformidad con las prácticas, uso de suelo y legislaciones nacionales.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P141",
      "link": "https://ciruelacertificada.cl/?s=P141&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida Diligencia de la Legislación",
      "linked_resources": [
        "712",
        "857",
        "1002"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    },
    {
      "points": 2,
      "level": "Básico",
      "dimension": "Ética",
      "verification_detail": "Son válidos los siguientes documentos de validación.  - Registro en el Conservador de Bienes Raíces (CBR).  - Catastro Público de Aguas de la DGA.  - Comprobante de acciones de aguas.",
      "action": "El predio posee Derechos de Aprovechamiento de Aguas inscritos en conformidad con las legislaciones nacionales.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P142",
      "link": "https://ciruelacertificada.cl/?s=P142&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida Diligencia de la Legislación",
      "linked_resources": [
        "713",
        "858",
        "1003"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ética",
      "verification_detail": "Matriz con listado de normativas aplicables para la planta que incluya la siguiente información:  * Tipo de documento (ley, resolución, decreto, norma, etc.) y entidad o Ministerio.  * Identificación de normativas prioritarias.  * Acciones requeridas para verificar y asegurar su cumplimiento.  Adicionalmente, se debe mantener al menos una copia de las normativas prioritarias, ya sea como documento impreso y/o registro digital.",
      "action": "El predio identifica las legislaciones relacionadas con las obligaciones prioritarias para la empresa, a través de una matriz de riesgos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P143",
      "link": "https://ciruelacertificada.cl/?s=P143&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida Diligencia de la Legislación",
      "linked_resources": [
        "546",
        "714",
        "859",
        "1004"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ética",
      "verification_detail": "Son válidos los siguientes documentos:  - Actas de reuniones realizadas a través de la Ley de Lobby.  - Actas de reuniones con entidades legisladoras.",
      "action": "El predio mantiene un diálogo permanente con las instituciones asociadas a las entidades legisladoras a nivel territorial o regional.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P144",
      "link": "https://ciruelacertificada.cl/?s=P144&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida Diligencia de la Legislación",
      "linked_resources": [
        "563",
        "715",
        "860",
        "1005"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    },
    {
      "points": 4,
      "level": "Avanzado",
      "dimension": "Ética",
      "verification_detail": "Autodiagnóstico ejecutado con alguna de las herramientas de autoevaluación de debida diligencia de derechos humanos.",
      "action": "La empresa realiza un autodiagnóstico de conducta empresarial responsable y debida diligencia en derechos humanos.",
      "valid_answers": [
        "Si cumplo",
        "No cumplo",
        "No cumplo, pero me es factible",
        "No aplica a mi sistema productivo"
      ],
      "standard_code": "P145",
      "link": "https://ciruelacertificada.cl/?s=P145&jet_ajax_search_settings=%7B%22current_query%22%3A%7B%22taxonomy%22%3A%22estandares-recursos%22%2C%22term%22%3A%22recurso-produccion-primaria%22%7D%2C%22sentence%22%3Atrue%2C%22search_in_taxonomy%22%3Atrue%2C%22search_in_taxonomy_source%22%3A%5B%22elementor_library_category%22%2C%22acciones-relacionadas%22%5D%7D",
      "theme": "Debida Diligencia de la Legislación",
      "linked_resources": [
        "716",
        "861",
        "1006"
      ],
      "good_practice": "Asegurar la debida diligencia de todas las leyes, reglamentaciones, certificaciones aplicables para la industria, tanto a nivel nacional como de los mercados de destino a nivel internacional",
      "verification_type": "Archivo"
    }
  ]
}
```

## Consideraciones para Autorización

### Campos Recomendados para `users`

Basándome en las colecciones existentes, se recomienda crear una colección `users` con la siguiente estructura:

```typescript
interface User {
  uid: string;                    // Firebase Auth UID
  email: string;                  // Email del usuario
  role: 'admin' | 'business_owner' | 'auditor';
  profile: {
    displayName: string;
    photoURL?: string;
  };
  
  // Para business_owners
  businessProfileId?: string;     // Referencia a business_profiles
  
  // Para auditors
  auditorId?: string;            // Referencia a auditors
  
  // Metadatos
  createdAt: Timestamp;
  lastLogin: Timestamp;
  isActive: boolean;
  permissions: string[];
}
```

## Índices Recomendados

Para optimizar las consultas de autorización:

```
// Índice compuesto para buscar usuarios por rol y estado
users: role (ASC), isActive (ASC)

// Índice para buscar por businessProfileId
users: businessProfileId (ASC)

// Índice para buscar por auditorId  
users: auditorId (ASC)
```

## Reglas de Seguridad Firestore

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Business profiles - solo el owner o admin
    match /business_profiles/{profileId} {
      allow read: if request.auth != null && (
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.businessProfileId == profileId ||
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin'
      );
    }
    
    // Auditors - solo el auditor específico o admin
    match /auditors/{auditorId} {
      allow read: if request.auth != null && (
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.auditorId == auditorId ||
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin'
      );
    }
  }
}
```

---

*Esquema generado automáticamente. Revisar y validar según las necesidades del proyecto.*
