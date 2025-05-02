# 🧠 AI Personal Workflow Assistant – Guía de Desarrollo

Este proyecto demuestra cómo construir un sistema de automatización inteligente basado en IA, utilizando un backend modular compatible con el protocolo MCP y flujos orquestados desde `n8n`.

Este proyecto integra automatizaciones con inteligencia artificial usando:
- `n8n` como orquestador de flujos
- `FastAPI` como backend inteligente
- Protocolo **MCP (Model Context Protocol)** para estructurar la comunicación entre componentes
- IA para tareas como resumen de textos, clasificación, generación de reportes, etc.
- Notificaciones en Telegram, emails o dashboards
- Persistencia en PostgreSQL para trazabilidad y análisis
- Contenerización profesional con Docker

---

## 📁 Estructura del Repositorio

```bash
AI-Workflow-Assistant/
├── backend/                   # Backend en FastAPI actuando como MCP Host
│   ├── main.py                # Punto de entrada principal
│   ├── db.py                  # Conexión y persistencia en PostgreSQL
│   ├── requirements.txt       # Dependencias de Python
│   ├── mcp/                   # Lógica del protocolo MCP (Input/Output, contexto, etc.)
│   ├── plugins/               # Módulos de IA: summarize, classify, extract...
│   └── models/                # Integraciones con OpenAI, HuggingFace, o modelos locales
│
├── n8n-flows/                 # Flujos exportados de n8n (en formato JSON)
│
├── docs/
│   └── GUIDE.md               # Guía de desarrollo del proyecto (esta misma hoja de ruta)
│
├── docker-compose.yml         # Orquestación del backend, PostgreSQL y n8n con Docker
│
├── .env
├── .env.example
│
├── .gitignore
└── README.md                  # Descripción general del proyecto
```


## ⚙️ Automatización con Makefile

Se incluye un `Makefile` para automatizar tareas de desarrollo y testing:

#### 📋 Comandos disponibles

| Comando         | Descripción                                     |
|-----------------|-------------------------------------------------|
| `make up`       | Levanta backend, PostgreSQL y n8n con Docker    |
| `make stop`     | Detiene los contenedores                        |
| `make build`    | Reconstruye la imagen del backend               |
| `make restart`  | Reinicia el backend con build                   |
| `make logs`     | Muestra logs en tiempo real del backend         |
| `make curl`     | Prueba el endpoint `/mcp/invoke` vía `curl`     |
| `make db`       | Accede al cliente `psql` dentro del contenedor  |
| `make reset-db` | Elimina volumen de datos de PostgreSQL (⚠️)     |
| `make help`     | Muestra la lista de comandos disponibles        |

## 🗺️ Hoja de Ruta del Proyecto

### ✅ FASE 0: Preparación
- [x] Crear repositorio Git (estructura base arriba)
- [x] Tener un VPS o servidor (Google Cloud, local, etc.)
- [x] Tener Docker y Docker Compose configurados
- [x] Tener instalado y accesible `n8n` en dominio o subdominio

---

### 🔧 FASE 1: Backend en FastAPI como MCP Host
- [x] Crear API básica con FastAPI
- [x] Estructurar entrada/salida según formato MCP (`InputMessage`, `OutputMessage`)
- [x] Implementar enrutador `/mcp/invoke` que acepte peticiones JSON
- [x] Definir estructura de contexto (`context`, `history`, `task`, `metadata`)
- [x] Añadir un primer **plugin**: `summarize` (usando OpenAI o transformers locales)
- [x] Testear localmente el endpoint `/mcp/invoke`

---

### 🔁 FASE 2: Integración con n8n
- [x] Crear flujo en n8n que reciba documentos por Webhook
- [x] Enviar texto al endpoint `/mcp/invoke` con estructura MCP
- [x] Recibir y parsear la respuesta para:
  - [x] Enviar mensaje a Telegram o email
  - [x] Guardar en base de datos (opcional)
  - [x] Registrar en Google Sheets
- [x] Exportar el flujo a `n8n-flows/` como JSON

---

### 🧠 FASE 3: Plugins de IA
- [x] `summarize`: resumen de texto largo
- [ ] `classify`: detección de intención o urgencia
- [ ] `extract`: extracción de entidades clave (personas, fechas, números)
- [ ] `report`: generación de resumen semanal (integración con Google Calendar opcional)
- [ ] `generate`: generación de texto o informes

---

### 📦 FASE 4: Arquitectura profesional
- [x] Dockerizar todo: backend + n8n en `docker-compose.yml`
- [x] Habilitar logging y trazabilidad (logs de llamadas, errores)
- [ ] Añadir autenticación (token simple o JWT)
- [x] Persistencia con PostgreSQL
- [x] Documentación OpenAPI en `/docs`
- [ ] Endpoint GET para consultar resúmenes guardados

---

### 🧪 FASE 5: Calidad y preparación para portafolio
- [x] Añadir ejemplos reales de uso
- [ ] Capturas de pantalla o vídeo demo
- [x] README completo con descripción, arquitectura, instrucciones de uso
- [ ] Despliegue real en dominio propio (por ejemplo: `assistant.dasafodata.com`)
- [ ] Preparar presentación en LinkedIn y demo pública

---

## 🔄 Comandos útiles
``` bash
# Levantar los servicios
docker compose up -d

# Reconstruir backend tras cambios en dependencias
docker compose build backend

# Parar y eliminar contenedores
docker compose down

# Ver logs en tiempo real del backend
docker compose logs -f backend
```

## 🧪 Test del backend con curl
``` bash
curl -X POST https://<tu_ngrok>.ngrok-free.app/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "task": "summarize",
    "input": { "text": "Texto largo que será resumido..." },
    "context": { "source": "n8n", "user_id": "david" }
  }'
```

## ✨ Recursos útiles

- [n8n Documentation](https://docs.n8n.io)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Model Context Protocol (OpenAI)](https://github.com/openai/openai-python/tree/main/openai/mc)
- [Langchain (opcional)](https://python.langchain.com)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

---

## 📌 Autor
David – dasafodata | Zaragoza, España  
Contacto: [dasafodata.com](https://dasafodata.com)  