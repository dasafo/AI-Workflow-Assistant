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
| **OpenAI / Transformers** | Motor de IA para plugins |
| **Docker + Compose** | Contenedores y orquestación |
| **Ngrok** (dev) | Exposición temporal de servicios locales |



## 📁 Estructura del Proyecto

```bash
AI-Workflow-Assistant/
├── backend/                 # FastAPI + lógica IA modular
│   ├── mcp/                 # Estructuras MCP y endpoint /mcp/invoke
│   ├── plugins/             # Funciones IA (summarize, classify, extract...)
│   ├── models/              # Modelos locales o externos
│   └── requirements.txt     # Dependencias Python
│
├── n8n-flows/               # Flujos exportados desde n8n (JSON)
├── docs/                    # Documentación técnica
│   └── GUIDE.md             # Hoja de ruta técnica detallada
│
├── docker-compose.yml       # Orquestación backend + n8n
├── .env                     # Variables de entorno (no se versiona)
├── .env.example             # Plantilla para configuración
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
```

## 🧪 Prueba rápida del backend (curl)

```bash
curl -X POST http://localhost:8000/mcp/invoke \
  -H "Content-Type: application/json" \
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

## 🧪 Flujos en n8n

- Entrada: Telegram, Webhook HTTP, Email

- Acción: Llama al backend `/mcp/invoke`

- Salida:

  - Mensaje de respuesta por Telegram

  - Fila añadida a Google Sheets

  - Registro persistente en PostgreSQL

Puedes importar los flujos desde la carpeta `n8n-flows/`.

## 📄 Documentación técnica extendida

Consulta la guía completa del proyecto en `docs/GUIDE.md`

Incluye:

- Estructura detallada del backend

- Hoja de ruta y fases del proyecto

- Plugins IA disponibles y planificados

- Comandos útiles

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