# 🧠 AI Personal Workflow Assistant

> Un sistema de automatización inteligente con backend en FastAPI, flujos orquestados por `n8n` y comunicación estructurada mediante el protocolo MCP.


## 🚀 Descripción

Este proyecto demuestra cómo construir una arquitectura modular y extensible de automatización basada en inteligencia artificial. Su objetivo es asistir en tareas repetitivas como:

- Resumen automático de textos
- Clasificación de contenido
- Extracción de información clave
- Generación de reportes
- Notificaciones automatizadas vía Telegram, correo u otras herramientas



## 🧩 Tecnologías utilizadas

| Tecnología | Rol |
|------------|-----|
| **FastAPI** | Backend IA (MCP Host) |
| **n8n**     | Orquestador de flujos de trabajo |
| **MCP (Model Context Protocol)** | Protocolo de integración entre sistemas |
| **OpenAI (GPT-4o-mini)** | Motor de IA para resumen inteligente |
| **Docker + Compose** | Contenedores y orquestación |
| **Ngrok** (dev) | Exposición temporal de servicios locales |
| **PostgreSQL** | Persistencia de resúmenes y trazabilidad |



## 📁 Estructura del Proyecto

```bash
AI-Workflow-Assistant/
├── backend/                 # FastAPI + lógica IA modular
│   ├── api/
│   │   └── routes/          # Endpoints /mcp/invoke y /mcp/telegram
│   ├── core/                # Esquemas y estructuras MCP
│   ├── services/            # db.py + tareas IA
│   │   └── tasks/           # summarize.py, classify.py, etc.
│   ├── models/              # Modelos locales o externos (reservado)
│   ├── plugins/             # (Reservado para futuros conectores)
│   └── main.py              # Punto de entrada
│
├── n8n-flows/               # Flujos exportados desde n8n (JSON)
├── docs/                    # Documentación técnica
│   └── GUIDE.md             # Hoja de ruta técnica detallada
│
├── docker-compose.yml       # Orquestación backend + PostgreSQL + n8n
├── Makefile
├── .env                     # Variables de entorno
├── .env.example             # Plantilla de configuración
└── README.md                # Este archivo
```

## 🧠 Arquitectura general

[Telegram / Webhook HTTP]
         ↓
        n8n (Docker)
         ↓
POST /mcp/invoke → FastAPI backend
         ↓
Procesamiento IA (plugin: summarize, etc.)
         ↓
[PostgreSQL] + [Telegram Notif] + [Google Sheets]

## ⚙️ Cómo levantar el proyecto

**1.** Clona el repositorio:

```bash
git clone https://github.com/tuusuario/AI-Workflow-Assistant.git
cd AI-Workflow-Assistant
```

**2.** Crea tu archivo de entorno desde el ejemplo:

```bash
cp .env.example .env
```

 **3.** Levanta los servicios:

```bash
docker compose up --build
make up # con Makefile
```

## 🧪 Prueba rápida del backend (curl)

```bash
curl -X POST http://localhost:8000/mcp/invoke \
  -H "Content-Type: application/json" \
  -H "x-api-key: <TU_API_KEY>" \
  -d '{
    "task": "summarize",
    "input": { "text": "Texto de prueba para resumir automáticamente..." },
    "context": { "user_id": "demo_user" }
  }'
```

Deberías recibir una respuesta estructurada en formato MCP con el resumen generado y ver el dato guardado en PostgreSQL.

## 🌐 Accesos locales
| Servicio | URL |
|------------|-----|
| **FastAPI (backend)** | http://localhost:8000 |
| **Docs API** |	http://localhost:8000/docs |
| **n8n (UI)** |	http://localhost:5678 | 

El acceso a `n8n` requiere las credenciales definidas en `.env`.

## 🧠 Integración con OpenAI

Este proyecto utiliza OpenAI GPT-4o-mini para generar resúmenes reales a través del plugin summarize.

- Cuando task == "summarize":

    - El backend llama a OpenAI (gpt-4o-mini-2024-07-18)

    - Recibe un resumen del texto

    - Lo guarda en PostgreSQL

    - Lo envía a Telegram y Google Sheets

**Variable requerida:**

```bash
OPENAI_API_KEY=sk-xxxxxx
```

La temperatura está fijada en `0.3` y el límite en `200 tokens`.

## 🧪 Flujos en n8n

- Entrada: Telegram, Webhook HTTP, Email

- Acción: Llama al backend `/mcp/invoke`

- Salida:

  - Mensaje de respuesta por Telegram

  - Fila añadida a Google Sheets

  - Registro persistente en PostgreSQL

Puedes importar los flujos desde la carpeta `n8n-flows/`.

## 🔐 Seguridad por API Key

El endpoint `/mcp/invoke` del backend requiere una API Key para autorizar las peticiones.

- Se debe incluir un header personalizado:
```http
  X-API-Key: <tu_api_key>
```


- Esta clave se define en el archivo `.env`:
- 
```http
API_KEY= <clave>
```

En n8n se puede usar directamente o vía `{{ $env.API_KEY }}`.

## 📄 Documentación técnica extendida

Consulta la guía completa del proyecto en `docs/GUIDE.md`

Incluye:

- Estructura detallada del backend

- Hoja de ruta y fases del proyecto

- Plugins IA disponibles y planificados
  
- Seguridad por API Key
  
- Integración con OpenAI

- Variables de entorno

- Buenas prácticas para portafolio técnico

## 🔧 Atajos de desarrollo (Makefile)

El proyecto incluye un `Makefile` con comandos útiles como:

```bash
make up         # Levanta los servicios con Docker
make stop       # Detiene los servicios
make curl       # Prueba el endpoint de resumen
make db         # Accede a la base de datos PostgreSQL
make restart    # Reinicia backend con build
make help       # Para ver todos los comandos disponibles
```

## 📸 Capturas o demo (opcional)

[Aquí puedes añadir capturas de pantalla o un enlace a un vídeo demo en YouTube o Loom]


## 👨‍💻 Autor

Contacto: [dasafodata.com](https://dasafodata.com)

📍 Zaragoza, España

## 📝 Licencia

MIT License