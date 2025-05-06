# 🧠 AI Workflow Assistant - Resumen del Proyecto

## 🎯 Descripción General
Sistema de automatización inteligente que integra IA para procesar y automatizar tareas usando FastAPI, n8n y OpenAI.

## 🏗️ Arquitectura Principal

### 1. Backend (FastAPI)
- Implementa el protocolo MCP (Model Context Protocol)
- Maneja tres tareas principales:
  - `summarize`: Resúmenes automáticos de texto
  - `translate`: Traducción entre idiomas
  - `classify`: Clasificación de contenido
- Usa OpenAI GPT-4-mini como motor de IA
- Almacena resultados en PostgreSQL

### 2. Orquestación (n8n)
- Maneja flujos de trabajo automatizados
- Integración con Telegram para recibir comandos
- Webhooks para comunicación externa
- Procesa y envía peticiones al backend

### 3. Base de Datos (PostgreSQL)
- Almacena historial de traducciones
- Guarda resúmenes generados
- Mantiene registro de clasificaciones
- Permite trazabilidad de operaciones

## 🚀 Estructura y Componentes

### 📦 Estructura del Proyecto
```
AI-Workflow-Assistant/
├── backend/
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── router.py      # API endpoints y validación
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py         # Modelos SQLAlchemy
│   │   └── schemas.py        # Schemas Pydantic
│   └── services/
│       ├── __init__.py
│       ├── db.py             # Gestión BD
│       └── tasks/            # Servicios IA
│           ├── __init__.py
│           ├── summarize.py
│           ├── translate.py
│           └── classify.py
├── docs/                     # Documentación
├── n8n-flows/               # Flujos n8n
└── docker/                  # Config. Docker
```

### 🔧 Componentes Principales
1. **Backend Core**
   - Punto de entrada FastAPI
   - Configuración centralizada de logging
   - Health check endpoint
   - Registro de rutas
   - Inicialización BD

2. **API (`router.py`)**
     - Endpoint unificado `/api/v1/mcp/invoke`
     - Maneja todas las tareas (summarize, translate, classify)
     - Validación API key
     - Procesamiento de contexto
     - Logging estructurado
     - Input/Output estandarizado
     - Schemas Pydantic
     - Manejo de errores consistente
     - Respuestas tipadas

3. **Servicios IA (`/services/tasks/`)**
   - Integración OpenAI
   - Procesamiento de texto
   - Persistencia en BD
   - Manejo de errores

4. **Base de Datos (`db.py`)**
   - Conexión PostgreSQL
   - Operaciones CRUD
   - Migraciones
   - Backups

### 🔄 Flujo de Trabajo
1. Usuario → Telegram Bot
2. n8n procesa comando
3. Backend procesa con IA
4. Respuesta → Usuario

### 🛠️ Stack Tecnológico
- FastAPI 0.104.1 (Python 3.11)
- PostgreSQL 14-alpine
- n8n latest
- Docker + Docker Compose

### 🔐 Seguridad
- API keys
- HTTPS
- Usuarios no-root
- Variables de entorno

## 📝 Comandos y Testing
```bash
# Iniciar servicios
make up

# Ver logs
make logs

# Tests
make test

# Base de datos
make db
```

### 📝 Logs
- Formato estandarizado
- Niveles configurables
- Salida unificada
- Contexto por módulo
- Timestamps consistentes