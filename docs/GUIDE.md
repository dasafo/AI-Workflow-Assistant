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
  - [🚀 Optimización de rendimiento](#-optimización-de-rendimiento)
    - [Sistema de caché con Redis](#sistema-de-caché-con-redis)
    - [Optimización de Docker](#optimización-de-docker)
    - [Asincronía completa](#asincronía-completa)
    - [Manejo de errores y reintentos](#manejo-de-errores-y-reintentos)
    - [Optimización de base de datos PostgreSQL](#optimización-de-base-de-datos-postgresql)
      - [Implementación de índices](#implementación-de-índices)
      - [Configuración del pool de conexiones](#configuración-del-pool-de-conexiones)
      - [Optimizaciones adicionales](#optimizaciones-adicionales)
  - [🔧 Troubleshooting](#-troubleshooting)
    - [Problemas Comunes](#problemas-comunes)
  - [🚀 Guía de Producción](#-guía-de-producción)
    - [Requisitos de Sistema](#requisitos-de-sistema)
    - [Configuración de SSL](#configuración-de-ssl)
    - [Backup y Recuperación](#backup-y-recuperación)
  - [📊 Monitoreo](#-monitoreo)
    - [Métricas Clave](#métricas-clave)
    - [Herramientas Recomendadas](#herramientas-recomendadas)

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
│   │   
│   ├── core/
│   │   ├── __init__.py
│   │   ├── schemas.py       # Schemas Pydantic (Input/Output Messages)
│   │   ├── models.py        # Modelos SQLAlchemy
│   │   ├── logging.py       # Configuración centralizada de logs
│   │   └── health.py        # Health checks unificados
│   │   └── cache.py         # cache con remis
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

## 🚀 Optimización de rendimiento

### Sistema de caché con Redis

El proyecto ahora incluye un sistema de caché utilizando Redis para optimizar las consultas frecuentes a la API de OpenAI:

- **Reducción de costos**: Al cachear respuestas similares, se reduce el número de llamadas a la API.
- **Mejora de velocidad**: Las respuestas cacheadas se entregan instantáneamente, sin esperar a la API.
- **Configuración flexible**: Tiempos de vida (TTL) configurables por cada tipo de tarea.

Para configurar el sistema de caché, ajusta las siguientes variables en tu archivo `.env`:

```bash
# Redis - Sistema de caché
REDIS_HOST=redis           # Host del servidor Redis
REDIS_PORT=6379            # Puerto de Redis
REDIS_DB=0                 # Base de datos Redis
REDIS_CACHE_TTL=86400      # TTL general (24h)
SUMMARY_CACHE_TTL=86400    # TTL para resúmenes
TRANSLATION_CACHE_TTL=86400  # TTL para traducciones
CLASSIFICATION_CACHE_TTL=86400  # TTL para clasificaciones
```

Para limpiar la caché en casos necesarios, puedes añadir un nuevo endpoint en el futuro o reiniciar el contenedor de Redis:

```bash
# Reiniciar sólo Redis
docker restart ai-workflow-redis
```

### Optimización de Docker

El proyecto ahora utiliza una imagen Docker más eficiente y ligera mediante:

- **Multi-stage builds**: Separamos la fase de compilación de la imagen final para reducir el tamaño.
- **Alpine como base**: Usamos Alpine Linux para una imagen más pequeña (aprox. 70% de reducción).
- **Wheels pre-compilados**: Las dependencias se compilan en la primera fase y solo se instalan los binarios en la imagen final.

Beneficios de estas optimizaciones:

- **Menor tamaño de imagen**: De ~1GB con slim a ~300MB con Alpine y multi-stage.
- **Despliegue más rápido**: Menor tiempo de descarga y arranque de contenedores.
- **Mayor seguridad**: Superficie de ataque reducida al incluir menos componentes.

Para reconstruir la imagen con estas optimizaciones:

```bash
# Reconstruir la imagen del backend
make build

# O manualmente
docker-compose build backend
```

### Asincronía completa

El backend ahora implementa asincronía completa en todos sus componentes:

- **SQLAlchemy 2.0 Async**: Conexiones asíncronas a base de datos para mejor rendimiento.
- **AsyncOpenAI**: Cliente asíncrono para las llamadas a la API de OpenAI.
- **Operaciones asíncronas**: Todas las operaciones de I/O son asíncronas (DB, API, caché).

Beneficios de la asincronía:

- **Mayor concurrencia**: Permite manejar múltiples solicitudes simultáneas sin bloquear hilos.
- **Mejor rendimiento**: Aprovecha eficientemente los tiempos de espera de I/O.
- **Escalabilidad**: La aplicación puede manejar más carga con los mismos recursos.

Para entender el modelo asíncrono, observa cómo se definen y utilizan las funciones:

```python
# Ejemplo de función asíncrona
@cache_response(ttl=86400)
async def run(input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    response = await client.chat.completions.create(...)
    await guardar_resumen(...)
    return {...}
```

Todos los endpoints ahora son asíncronos, lo que mejora significativamente el rendimiento general de la aplicación.

### Manejo de errores y reintentos

El sistema ahora incluye un manejo de errores robusto y un mecanismo de reintentos automáticos:

- **Errores estructurados**: Sistema de errores estandarizado con códigos, mensajes descriptivos y detalles.
- **Reintentos automáticos**: Las llamadas a OpenAI se reintentan automáticamente ante fallos temporales.
- **Backoff exponencial**: Tiempo creciente entre reintentos para evitar sobrecargar servicios externos.
- **Jitter aleatorio**: Previene tormentas de reintentos sincronizados en entornos multiusuario.

El sistema de reintentos se implementa mediante un decorador que se puede aplicar a cualquier función asíncrona:

```python
@with_retry
async def call_openai_with_retry(text: str):
    # Esta función se reintentará automáticamente si falla
    response = await client.chat.completions.create(...)
    return response
```

Beneficios del sistema de errores y reintentos:

- **Mayor fiabilidad**: El sistema es resiliente ante fallos temporales de red o servicios.
- **Mejor diagnóstico**: Los errores incluyen códigos estandarizados y detalles para facilitar la solución.
- **Mensajes coherentes**: Los usuarios reciben información clara sobre los problemas.
- **Logs mejorados**: Cada error se registra con su código, mensaje y stack trace para facilitar depuración.

Para configurar los reintentos, ajusta estas variables en el `.env`:

```bash
# Configuración de reintentos
OPENAI_TIMEOUT=30.0          # Timeout en segundos
OPENAI_MAX_RETRIES=3         # Número máximo de reintentos
OPENAI_RETRY_DELAY_BASE=1.0  # Retraso base (segundos)
OPENAI_RETRY_DELAY_MAX=10.0  # Retraso máximo (segundos)
OPENAI_RETRY_JITTER=0.1      # Factor de aleatoriedad
```

### Optimización de base de datos PostgreSQL

#### Implementación de índices

La aplicación utiliza índices estratégicos para mejorar significativamente el rendimiento de consultas frecuentes:

```sql
-- Índice para búsquedas por user_id (muy común en filtros)
CREATE INDEX idx_translations_user_id ON translations(user_id);

-- Índice para búsquedas por fecha (para reportes y análisis)
CREATE INDEX idx_summaries_created_at ON summaries(created_at);

-- Índice compuesto para búsquedas combinadas
CREATE INDEX idx_classifications_user_type ON classifications(user_id, content_type);

-- Índice de texto para búsquedas en contenido
CREATE INDEX idx_content_search ON summaries USING gin(to_tsvector('spanish', content));
```

Estos índices se aplican automáticamente durante la inicialización de la base de datos mediante los scripts de migración en `./backend/migrations`.

#### Configuración del pool de conexiones

El sistema implementa un pool de conexiones optimizado para equilibrar rendimiento y recursos:

```python
# En backend/services/db.py
async def get_db_pool():
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=20,               # Tamaño base del pool
        max_overflow=10,            # Conexiones adicionales permitidas
        pool_timeout=30,            # Tiempo de espera para obtener conexión
        pool_recycle=1800,          # Reciclar conexiones cada 30 min
        pool_pre_ping=True,         # Verificar conexiones antes de usarlas
        pool_use_lifo=True,         # Estrategia LIFO para mejor reutilización
    )
    return engine
```

Para configurar estos parámetros según tus necesidades, ajusta las siguientes variables en `.env`:

```bash
# Configuración pool de PostgreSQL
POSTGRES_POOL_SIZE=20
POSTGRES_MAX_OVERFLOW=10
POSTGRES_POOL_TIMEOUT=30
POSTGRES_POOL_RECYCLE=1800
```

#### Optimizaciones adicionales

- **Vacuum automático**: Configurado para ejecutarse periódicamente y mantener la base de datos optimizada
- **Statement timeout**: Limita la duración máxima de consultas para evitar bloqueos prolongados
- **Particionamiento**: Para tablas que crecen significativamente (implementado en `summaries` por fecha)

Para aplicar estas optimizaciones en un entorno de producción, utiliza:

```bash
# Aplicar optimizaciones de PostgreSQL
make optimize-db
```

## 🔧 Troubleshooting

### Problemas Comunes
1. **Redis Port in Use**
   ```bash
   # Solución 1: Cambiar puerto
   REDIS_PORT=6380
   
   # Solución 2: Detener Redis local
   sudo service redis-server stop
   ```

2. **Database Connection Issues**
   ...

3. **API Key Problems**
   ...

## 🚀 Guía de Producción

### Requisitos de Sistema
- CPU: 2+ cores
- RAM: 4GB mínimo
- Disco: 20GB SSD

### Configuración de SSL
...

### Backup y Recuperación
...

## 📊 Monitoreo

### Métricas Clave
- Latencia de API
- Uso de CPU/RAM
- Tasa de errores
- Uso de caché

### Herramientas Recomendadas
...