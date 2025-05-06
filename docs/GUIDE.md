# 🧠 AI Personal Workflow Assistant – Guía de Desarrollo

## 📋 Índice
- [🧠 AI Personal Workflow Assistant – Guía de Desarrollo](#-ai-personal-workflow-assistant--guía-de-desarrollo)
  - [📋 Índice](#-índice)
  - [🎯 Descripción del Proyecto](#-descripción-del-proyecto)
  - [📁 Estructura del Repositorio](#-estructura-del-repositorio)
  - [⚙️ Automatización con Makefile](#️-automatización-con-makefile)
      - [📋 Comandos disponibles](#-comandos-disponibles)
  - [🗺️ Hoja de Ruta del Proyecto](#️-hoja-de-ruta-del-proyecto)
    - [✅ FASE 0: Preparación](#-fase-0-preparación)
    - [🔧 FASE 1: Backend en FastAPI como MCP Host](#-fase-1-backend-en-fastapi-como-mcp-host)
    - [🔁 FASE 2: Integración con n8n](#-fase-2-integración-con-n8n)
    - [🧠 FASE 3: Plugins de IA](#-fase-3-plugins-de-ia)
    - [📦 FASE 4: Arquitectura profesional](#-fase-4-arquitectura-profesional)
    - [🧪 FASE 5: Calidad y preparación para portafolio](#-fase-5-calidad-y-preparación-para-portafolio)
  - [🏗️ Arquitectura del Sistema](#️-arquitectura-del-sistema)
    - [Core Components](#core-components)
    - [Características Implementadas](#características-implementadas)
  - [🔄 Comandos útiles](#-comandos-útiles)
  - [🧪 Test del backend con curl](#-test-del-backend-con-curl)
  - [✨ Recursos útiles](#-recursos-útiles)
  - [📌 Autor](#-autor)
  - [🛠️ Comandos de Desarrollo](#️-comandos-de-desarrollo)

---

## 🎯 Descripción del Proyecto

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
├── backend/
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── router.py     # Endpoint unificado `/mcp/invoke`
│   ├── core/
│   │   ├── __init__.py
│   │   ├── schemas.py       # Schemas Pydantic (Input/Output Messages)
│   │   ├── models.py        # Modelos SQLAlchemy
│   │   ├── logging.py       # Configuración centralizada de logs
│   │   └── health.py        # Health checks unificados
│   ├── services/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   └── tasks/
│   │       ├── __init__.py
│   │       ├── summarize.py
│   │       ├── translate.py
│   │       └── classify.py
│   ├── main.py
│   └── requirements.txt
├── docs/
│   ├── GUIDE.md
│   └── workflow.md          # Documentación técnica
└── ... existing files ...
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
- [x] Configurar correctamente el webhook con ngrok usando `WEBHOOK_URL` para evitar puertos no permitidos por Telegram
- [x] Validar que el bot de Telegram activa correctamente el Trigger en n8n

---

### 🧠 FASE 3: Plugins de IA
- [x] `summarize`: resumen de texto largo
- [x] `classify`: detección de intención o urgencia
- [x] `translate`: traducir texto
- [ ] `extract`: extracción de entidades clave (personas, fechas, números)
- [ ] `report`: generación de resumen semanal (integración con Google Calendar opcional)
- [ ] `generate`: generación de texto o informes

---

### 📦 FASE 4: Arquitectura profesional
- [x] Dockerizar backend + postgree en `docker-compose.yml`
- [x] Estructura modular profesional (con /api, /services, /core)
- [x] Habilitar logging y trazabilidad centralizada
- [x] Añadir health checks unificados
- [x] Persistencia con PostgreSQL
- [x] Documentación OpenAPI en `/docs`
- [x] Seguridad con API Key en el backend
- [ ] Autenticación JWT (pendiente)
- [ ] Endpoint GET para consultar histórico

---

### 🧪 FASE 5: Calidad y preparación para portafolio
- [x] Añadir ejemplos reales de uso
- [ ] Capturas de pantalla o vídeo demo
- [x] README completo con descripción, arquitectura, instrucciones de uso
- [ ] Despliegue real en dominio propio (por ejemplo: `assistant.dasafodata.com`)
- [ ] Preparar presentación en LinkedIn y demo pública

---

## 🏗️ Arquitectura del Sistema

### Core Components
1. **API Layer** (`/api/routes/`)
   - Endpoint unificado MCP
   - Validación de API keys
   - Manejo de errores centralizado

2. **Core Layer** (`/core/`)
   - Schemas de datos (Pydantic)
   - Logging centralizado
   - Health checks
   - Modelos de base de datos

3. **Services Layer** (`/services/`)
   - Tareas de IA
   - Persistencia
   - Lógica de negocio

### Características Implementadas
- Logging centralizado y consistente
- Health checks unificados
- Variables de entorno centralizadas
- Seguridad básica con API keys
- Schemas validados con Pydantic
- Persistencia en PostgreSQL

---

## 🔄 Comandos útiles
``` bash
# Levantar los servicios
docker compose up -d
make up # usando makefile

# Reconstruir backend tras cambios en dependencias
docker compose build backend
make build # usando makefile

# Parar y eliminar contenedores
docker compose down
make stop # usando makefile

# Ver logs en tiempo real del backend
docker compose logs -f backend
make logs # usando makefile
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

---

## 🛠️ Comandos de Desarrollo

```bash
# Inicializar proyecto
cp .env.example .env
make build

# Desarrollo
make up           # Iniciar servicios
make logs        # Ver logs
make ps          # Estado de contenedores

# Testing
make test        # Ejecutar tests
make health-check # Verificar estado

# Database
make db          # Acceder a PostgreSQL
make reset-db    # Reset DB (⚠️ cuidado)
```