# 🧠 AI Personal Workflow Assistant

> Un sistema de automatización inteligente con backend en FastAPI, flujos orquestados por `n8n` y comunicación estructurada mediante el protocolo MCP.

---

## 🚀 Descripción

Este proyecto demuestra cómo construir una arquitectura modular y extensible de automatización basada en inteligencia artificial. Su objetivo es asistir en tareas repetitivas como:

- Resumen automático de textos
- Clasificación de contenido
- Extracción de información clave
- Generación de reportes
- Notificaciones automatizadas vía Telegram, correo u otras herramientas

---

## 🧩 Tecnologías utilizadas

| Tecnología | Rol |
|------------|-----|
| **FastAPI** | Backend IA (MCP Host) |
| **n8n**     | Orquestador de flujos de trabajo |
| **MCP (Model Context Protocol)** | Protocolo de integración entre sistemas |
| **OpenAI / Transformers** | Motor de IA para plugins |
| **Docker + Compose** | Contenedores y orquestación |
| **Ngrok** (dev) | Exposición temporal de servicios locales |

---

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
