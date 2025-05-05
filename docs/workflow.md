# 🧠 AI Workflow Assistant - Resumen del Proyecto

## 🎯 Descripción General
Un sistema de automatización inteligente que integra IA para procesar y automatizar tareas usando FastAPI, n8n y OpenAI.

## 🏗️ Arquitectura Principal

### 1. Backend (FastAPI)
- Implementa el protocolo MCP (Model Context Protocol)
- Maneja tres tareas principales:
  - `summarize`: Resúmenes automáticos de texto
  - `translate`: Traducción entre idiomas
  - `classify`: Clasificación de contenido
- Usa OpenAI GPT-3.5-turbo como motor de IA
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

## 🚀 Funcionalidades Principales

### Comandos de Telegram
- `/resumir`: Genera resúmenes de textos largos
- `/traducir`: Traduce texto entre idiomas
- `/clasificar`: Analiza la intención o tipo de texto

### API REST
- Endpoint principal: `/api/v1/mcp/invoke`
- Autenticación mediante API key
- Formato JSON estructurado
- Manejo de contexto y metadata

## 🔐 Seguridad
- API keys para acceso
- Usuarios no-root en Docker
- HTTPS para n8n
- Autenticación básica en n8n
- Variables de entorno seguras

## 🛠️ Stack Tecnológico

### Backend:
- FastAPI (Python 3.11)
- OpenAI API
- PostgreSQL 14

### Automatización:
- n8n para workflows
- Telegram Bot API
- Ngrok para túneles HTTPS

### Infraestructura:
- Docker + Docker Compose
- Makefile para automatización
- Logs estructurados

## 📦 Estructura del Proyecto
```
AI-Workflow-Assistant/
├── backend/
│   ├── api/          # Endpoints y rutas
│   ├── core/         # Schemas y configuración
│   └── services/     # Lógica de negocio y tareas
├── n8n-flows/        # Flujos de n8n exportados
└── docker/           # Configuración de contenedores
```

## 🔄 Flujo de Trabajo Típico
1. Usuario envía mensaje a bot de Telegram
2. n8n recibe el webhook y procesa el comando
3. Se envía petición al backend vía MCP
4. Backend procesa con OpenAI y guarda resultado
5. Respuesta se envía de vuelta al usuario

## 🎛️ Controles y Monitoreo
- Healthchecks en todos los servicios
- Logs centralizados
- Métricas de uso
- Persistencia de datos
- Backup automático

## 📁 Scripts Python del Proyecto

### Estructura Backend
```python
backend/
├── api/
│   ├── __init__.py
│   └── routes/
│       └── router.py      # Maneja los endpoints de la API
├── core/
│   ├── __init__.py
│   └── schemas.py         # Define los modelos de datos
└── services/
    ├── __init__.py
    ├── db.py             # Funciones de base de datos
    └── tasks/
        ├── __init__.py
        ├── summarize.py   # Servicio de resúmenes
        ├── translate.py   # Servicio de traducción
        └── classify.py    # Servicio de clasificación
```

### 🎯 Descripción de cada script

#### 1. [`router.py`](backend/api/routes/router.py)
- Maneja las rutas y endpoints de la API
- Define el endpoint principal `/mcp/invoke`
- Implementa validación de API key
- Encamina las peticiones a los servicios
- Maneja errores y logging

#### 2. [`schemas.py`](backend/core/schemas.py)
- Define modelos Pydantic para validación
- `TaskType`: Enum de tipos de tareas
- `Context`: Estructura de contexto
- `InputMessage`: Formato de entrada
- `OutputMessage`: Formato de respuesta

#### 3. [`db.py`](backend/services/db.py)
- Gestiona conexiones a PostgreSQL
- Funciones para guardar resultados:
  - `guardar_resumen()`
  - `guardar_traduccion()`
  - `guardar_clasificacion()`
- Manejo de errores de base de datos

#### 4-6. Scripts de Tareas
```python
# summarize.py, translate.py, classify.py
def run(input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    # Procesamiento específico de cada tarea
    # Integración con OpenAI GPT-3.5-turbo
    # Persistencia en base de datos
    # Retorno de resultados formateados
```

### 🧪 Testing
Cada módulo incluye tests unitarios para:
- Validación de entrada
- Procesamiento correcto
- Manejo de errores
- Persistencia en BD
- Formato de respuesta

### 📝 Logs
Sistema de logging estructurado para:
- Debugging
- Monitoreo
- Auditoría
- Análisis de uso