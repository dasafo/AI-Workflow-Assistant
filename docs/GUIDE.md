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
    - [🔧 FASE 1: Backend en FastAPI](#-fase-1-backend-en-fastapi)
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
      - [1. Obtener certificados SSL](#1-obtener-certificados-ssl)
      - [2. Configuración en Docker Compose](#2-configuración-en-docker-compose)
      - [3. Configuración en FastAPI](#3-configuración-en-fastapi)
      - [4. Redirección de HTTP a HTTPS](#4-redirección-de-http-a-https)
      - [5. Renovación automática de certificados](#5-renovación-automática-de-certificados)
    - [Backup y Recuperación](#backup-y-recuperación)
      - [1. Backup Automatizado de PostgreSQL](#1-backup-automatizado-de-postgresql)
      - [2. Proceso de Recuperación](#2-proceso-de-recuperación)
      - [3. Backup de Flujos de n8n](#3-backup-de-flujos-de-n8n)
  - [📊 Monitoreo](#-monitoreo)
    - [Métricas Clave](#métricas-clave)
    - [Herramientas Recomendadas](#herramientas-recomendadas)
  - [🔄 Actualizaciones y Mejoras](#-actualizaciones-y-mejoras)
    - [Unificación de Modelos de Datos](#unificación-de-modelos-de-datos)
    - [Manejo Robusto de Errores](#manejo-robusto-de-errores)
    - [Limpieza de Código Legacy](#limpieza-de-código-legacy)

---

## 🎯 Descripción del Proyecto

Este proyecto demuestra cómo construir un sistema de automatización inteligente basado en IA, utilizando un backend modular y flujos orquestados desde `n8n`.

Este proyecto integra automatizaciones con inteligencia artificial usando:
- `n8n` como orquestador de flujos
- `FastAPI` como backend inteligente
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
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── router.py       # Router principal
│   │   ├── workflow_endpoints.py # Endpoints principales
│   │   └── schemas.py         # Esquemas Pydantic
│   ├── core/
│   │   ├── __init__.py
│   │   ├── errors.py          # Manejo de errores y excepciones globales
│   │   ├── health.py          # Health checks unificados
│   │   ├── logging.py         # Configuración centralizada de logs
│   │   └── cache.py           # Sistema de caché con Redis
│   ├── services/
│   │   ├── __init__.py
│   │   ├── db.py              # Gestión unificada de base de datos
│   │   ├── models.py          # Modelos SQLAlchemy unificados (ConsultaIA, EstadoUsuario)
│   │   └── tasks/
│   │       ├── __init__.py
│   │       ├── summarize.py   # Servicio de resumen con manejo de errores
│   │       ├── translate.py   # Servicio de traducción con manejo de errores
│   │       └── classify.py    # Servicio de clasificación con manejo de errores
│   ├── migrations/            # Migraciones de base de datos
│   ├── main.py                # Punto de entrada con handler de excepciones global
│   └── requirements.txt
├── docs/
│   ├── GUIDE.md
│   └── workflow.md            # Documentación técnica
└── ... existing files ...
```


## ⚙️ Automatización con Makefile

Se incluye un `Makefile` para automatizar tareas de desarrollo y testing:

#### 📋 Comandos disponibles

| Comando         | Descripción                                     |
|-----------------|-------------------------------------------------|
| `make up`       | Levanta backend, PostgreSQL y n8n con Docker    |
| `make down`     | Detiene los contenedores                        |
| `make build`    | Reconstruye la imagen del backend               |
| `make restart`  | Reinicia el backend con build                   |
| `make logs`     | Muestra logs en tiempo real del backend         |
| `make ps`       | Lista los contenedores en ejecución             |
| `make db`       | Accede al cliente `psql` dentro del contenedor  |
| `make reset-db` | Elimina volumen de datos de PostgreSQL (⚠️)     |
| `make clean`    | Limpia archivos temporales y caché              |
| `make test`     | Ejecuta tests del backend                       |
| `make help`     | Muestra la lista de comandos disponibles        |

## 🗺️ Hoja de Ruta del Proyecto

### ✅ FASE 0: Preparación
- [x] Crear repositorio Git (estructura base arriba)
- [x] Tener un VPS o servidor (Google Cloud, local, etc.)
- [x] Tener Docker y Docker Compose configurados
- [x] Tener instalado y accesible `n8n` en dominio o subdominio

---

### 🔧 FASE 1: Backend en FastAPI
- [x] Crear API básica con FastAPI
- [x] Implementar endpoints principales para procesamiento de texto
- [x] Definir estructura de peticiones/respuestas con Pydantic
- [x] Añadir procesamiento con OpenAI para tareas de IA
- [x] Testear localmente los endpoints

---

### 🔁 FASE 2: Integración con n8n
- [x] Crear flujo en n8n que reciba documentos por Webhook
- [x] Enviar texto al backend para procesar
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
- [x] Manejo robusto de errores
- [x] Unificación de modelos de base de datos
- [ ] Autenticación JWT (pendiente)
- [x] Endpoint para consultar histórico

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
   - Endpoints REST para interacción con el sistema
   - Validación de API keys
   - Manejo de errores centralizado

2. **Core Layer** (`/core/`)
   - Schemas de datos (Pydantic)
   - Logging centralizado
   - Health checks
   - Sistema de caché con Redis
   - Manejo global de excepciones

3. **Services Layer** (`/services/`)
   - Tareas de IA con manejo robusto de errores
   - Persistencia unificada en `ConsultaIA`
   - Lógica de negocio

### Características Implementadas
- Logging centralizado y consistente
- Health checks unificados
- Variables de entorno centralizadas
- Seguridad básica con API keys
- Schemas validados con Pydantic
- Persistencia unificada en PostgreSQL
- Manejo robusto de errores con códigos HTTP específicos
- Caché con Redis para optimizar rendimiento

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

# Limpiar archivos temporales
make clean
```

## 🧪 Test del backend con curl
``` bash
# Gestionar estado/modo de un usuario
curl -X POST http://localhost:8000/api/v1/estado \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "chat_id": 123456789,
    "modo": "/resumir"
  }'

# Procesar texto (resumir, traducir, clasificar)
curl -X POST http://localhost:8000/api/v1/procesar \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "chat_id": 123456789,
    "texto": "Texto que será procesado según el tipo de tarea especificado...",
    "tipo_tarea": "resumir"
  }'

# Consultar historial de operaciones
curl -X POST http://localhost:8000/api/v1/consultar \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "chat_id": 123456789,
    "tipo_tarea": "traducir",
    "limit": 5
  }'

# Consulta en lenguaje natural del historial
curl -X POST http://localhost:8000/api/v1/consultar-inteligente \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "chat_id": 123456789,
    "texto": "Muéstrame mis últimos resúmenes"
  }'

# Verificar estado del sistema
curl http://localhost:8000/health
```

## ✨ Recursos útiles

- [n8n Documentation](https://docs.n8n.io)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Langchain (opcional)](https://python.langchain.com)

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

# Limpieza
make clean       # Eliminar archivos temporales y caché
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
    await guardar_consulta(...)
    return {...}
```

Todos los endpoints ahora son asíncronos, lo que mejora significativamente el rendimiento general de la aplicación.

### Manejo de errores y reintentos

El sistema ahora incluye un manejo de errores robusto y un mecanismo de reintentos automáticos:

- **Errores estructurados**: Sistema de errores estandarizado con códigos, mensajes descriptivos y detalles.
- **Reintentos automáticos**: Las llamadas a OpenAI se reintentan automáticamente ante fallos temporales.
- **Backoff exponencial**: Tiempo creciente entre reintentos para evitar sobrecargar servicios externos.
- **Jitter aleatorio**: Previene tormentas de reintentos sincronizados en entornos multiusuario.
- **Códigos HTTP específicos**: 504 para timeouts, 429 para rate limits y 502 para errores de API.

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
-- Índices en la tabla unificada consultas_ia
CREATE INDEX idx_consultas_chat_id ON consultas_ia(chat_id);
CREATE INDEX idx_consultas_tipo_tarea ON consultas_ia(tipo_tarea);
CREATE INDEX idx_consultas_fecha ON consultas_ia(fecha);

-- Índice combinado para búsquedas comunes
CREATE INDEX idx_consultas_chat_tipo ON consultas_ia(chat_id, tipo_tarea);
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
- **Particionamiento**: Para tablas que crecen significativamente (implementado en `consultas_ia` por fecha)

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
   ```bash
   # Verificar que el contenedor de PostgreSQL está corriendo
   docker ps | grep ai-workflow-db
   
   # Verificar logs de PostgreSQL
   docker logs ai-workflow-db
   
   # Reiniciar el contenedor
   docker restart ai-workflow-db
   ```

3. **API Key Problems**
   ```bash
   # Verificar que API_KEY está correctamente configurada en .env
   grep API_KEY .env
   
   # Asegurarse de que el header se está enviando correctamente
   curl -v -H "x-api-key: TU_API_KEY" http://localhost:8000/health
   ```

4. **Errores de OpenAI API**
   ```bash
   # Verificar errores 429 (rate limit)
   grep "status_code=429" backend/logs/app.log
   
   # Verificar errores 504 (timeout)
   grep "status_code=504" backend/logs/app.log
   
   # Verificar la validez de tu API Key
   echo $OPENAI_API_KEY | grep "sk-"
   ```

## 🚀 Guía de Producción

### Requisitos de Sistema
- CPU: 2+ cores
- RAM: 4GB mínimo
- Disco: 20GB SSD

### Configuración de SSL

Para asegurar la comunicación con el sistema en producción, es necesario configurar SSL/TLS:

#### 1. Obtener certificados SSL

```bash
# Usando Certbot (Let's Encrypt)
sudo apt-get update
sudo apt-get install certbot
sudo certbot certonly --standalone -d tu-dominio.com -d www.tu-dominio.com
```

#### 2. Configuración en Docker Compose

Añade los siguientes volúmenes en el servicio de backend en `docker-compose.yml`:

```yaml
services:
  backend:
    # ... configuración existente ...
    volumes:
      - /etc/letsencrypt/live/tu-dominio.com/fullchain.pem:/app/certs/fullchain.pem:ro
      - /etc/letsencrypt/live/tu-dominio.com/privkey.pem:/app/certs/privkey.pem:ro
```

#### 3. Configuración en FastAPI

En el archivo `main.py`, configura el servidor con SSL:

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="/app/certs/privkey.pem",
        ssl_certfile="/app/certs/fullchain.pem"
    )
```

#### 4. Redirección de HTTP a HTTPS

Para forzar el uso de HTTPS, puede añadir un middleware en FastAPI:

```python
@app.middleware("http")
async def redirect_to_https(request, call_next):
    if request.url.scheme == "http":
        https_url = request.url.replace(scheme="https")
        return RedirectResponse(url=str(https_url))
    
    return await call_next(request)
```

#### 5. Renovación automática de certificados

Configurar un cron job para renovar automáticamente los certificados:

```bash
# Añadir a crontab
echo "0 3 * * * certbot renew --quiet && docker restart ai-workflow-assistant-backend" | sudo tee -a /etc/crontab
```

### Backup y Recuperación

La estrategia de backup y recuperación asegura la integridad y disponibilidad de los datos del sistema:

#### 1. Backup Automatizado de PostgreSQL

Configure backups diarios con el siguiente script:

```bash
#!/bin/bash
# /usr/local/bin/backup-ai-workflow.sh

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/backups/ai-workflow"
CONTAINER="ai-workflow-postgres"
DB_USER="postgres"
DB_NAME="workflow"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Ejecutar backup
docker exec $CONTAINER pg_dump -U $DB_USER -d $DB_NAME | gzip > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"

# Retener solo los últimos 7 días
find $BACKUP_DIR -name "db_backup_*.sql.gz" -type f -mtime +7 -delete
```

Configure cron para ejecutar diariamente:

```bash
# Añadir a crontab
sudo chmod +x /usr/local/bin/backup-ai-workflow.sh
echo "0 2 * * * /usr/local/bin/backup-ai-workflow.sh" | sudo tee -a /etc/crontab
```

#### 2. Proceso de Recuperación

Para restaurar desde un backup:

```bash
# Restaurar desde un backup específico
gunzip -c /var/backups/ai-workflow/db_backup_20240101_020000.sql.gz | docker exec -i ai-workflow-postgres psql -U postgres -d workflow
```

#### 3. Backup de Flujos de n8n

Configure backups automáticos de los flujos de n8n:

```bash
# Exportar flujos a archivos JSON (desde n8n)
curl -X GET "http://localhost:5678/rest/workflows" \
  -H "x-n8n-api-key: $N8N_API_KEY" \
  > /var/backups/ai-workflow/n8n_workflows_$(date +"%Y%m%d").json
```

## 📊 Monitoreo

### Métricas Clave

El monitoreo efectivo del sistema ayuda a garantizar un rendimiento óptimo y a detectar problemas antes de que afecten a los usuarios:

1. **Métricas de Servicio**:
   - Tiempo de respuesta (promedio, p95, p99)
   - Tasa de solicitudes (RPS)
   - Tasa de errores (5xx, 4xx)
   - Tiempo de procesamiento por tipo de tarea

2. **Métricas de Recursos**:
   - Uso de CPU y memoria
   - Uso de disco y operaciones I/O
   - Conexiones de red
   - Utilización de pool de conexiones DB

3. **Métricas de Aplicación**:
   - Tasa de hit/miss de caché
   - Latencia de llamadas a OpenAI
   - Número de reintentos
   - Errores por tipo de tarea

4. **Métricas de Negocio**:
   - Tareas procesadas por hora/día
   - Distribución por tipo de tarea
   - Usuarios activos
   - Tiempo de procesamiento promedio

### Herramientas Recomendadas

1. **Monitoreo de Infraestructura**:
   - **Prometheus**: Recolección de métricas y alertas
   - **Grafana**: Visualización de dashboards
   - **Node Exporter**: Métricas del sistema
   - **cAdvisor**: Métricas de contenedores
   - **AlertManager**: Gestión de alertas

2. **Configuración Básica de Prometheus**:

   Crear `prometheus.yml`:
   ```yaml
   global:
     scrape_interval: 15s
   
   scrape_configs:
     - job_name: 'backend'
       static_configs:
         - targets: ['backend:8000']
     
     - job_name: 'node'
       static_configs:
         - targets: ['node-exporter:9100']
     
     - job_name: 'cadvisor'
       static_configs:
         - targets: ['cadvisor:8080']
   ```

3. **Agregar servicios de monitoreo al docker-compose.yml**:

   ```yaml
   services:
     prometheus:
       image: prom/prometheus:latest
       volumes:
         - ./prometheus.yml:/etc/prometheus/prometheus.yml
         - prometheus_data:/prometheus
       ports:
         - "9090:9090"
     
     grafana:
       image: grafana/grafana:latest
       volumes:
         - grafana_data:/var/lib/grafana
       ports:
         - "3000:3000"
       depends_on:
         - prometheus
     
     node-exporter:
       image: prom/node-exporter:latest
       ports:
         - "9100:9100"
       restart: always
   
   volumes:
     prometheus_data:
     grafana_data:
   ```

4. **Dashboards Esenciales**:
   - Rendimiento general del sistema
   - Métricas de API por endpoint
   - Uso de recursos por contenedor
   - Rendimiento de base de datos
   - Errores y tiempos de respuesta

5. **Alertas Recomendadas**:
   - Tiempo de respuesta > 2 segundos
   - Tasa de error > 1%
   - Uso de CPU > 80%
   - Uso de memoria > 85%
   - Redis o PostgreSQL no responden
   - Espacio en disco < 10%

## 🔄 Actualizaciones y Mejoras

### Unificación de Modelos de Datos

Hemos realizado una consolidación significativa en los modelos de datos, eliminando clases antiguas y adoptando un enfoque más unificado:

- **Modelo Unificado**: Se ha reemplazado los modelos separados (`Resumen`, `Traduccion`, `Clasificacion`) por un único modelo `ConsultaIA` que almacena todas las consultas.
- **Estructura optimizada**: El nuevo modelo incluye un campo `tipo_tarea` que identifica el tipo de operación, y campos unificados para almacenar texto original y resultado.
- **Índices mejorados**: Se han añadido índices para optimizar las consultas frecuentes sobre `chat_id`, `tipo_tarea` y `fecha`.

Beneficios de la unificación:
- **Código más simple**: Lógica centralizada para persistencia de datos
- **Consultas más eficientes**: Una sola tabla para consultar todo el historial
- **Mantenimiento más sencillo**: Estructura de datos coherente y predecible
- **Evolución facilitada**: Añadir nuevas tareas no requiere nuevas tablas

El modelo actual se define así:

```python
class ConsultaIA(Base):
    __tablename__ = "consultas_ia"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    tipo_tarea = Column(String(50), nullable=False, index=True)  # 'resumir', 'clasificar', etc.
    texto_original = Column(Text, nullable=False)
    resultado = Column(Text)
    idioma = Column(String(20), nullable=True)  # Solo para traducciones
    fecha = Column(DateTime(timezone=True), server_default=func.now(), index=True)
```

### Manejo Robusto de Errores

Hemos implementado un sistema de manejo de errores mucho más robusto:

- **Tipos específicos de errores**: 
  - `OpenAITimeoutError`: Para timeouts de conexión (HTTP 504)
  - `OpenAIRateLimitError`: Para límites de tasa excedidos (HTTP 429)
  - `OpenAIError`: Para otros errores de la API (HTTP 502)

- **Manejo global de excepciones**: Añadido un manejador global que captura todas las excepciones no controladas y devuelve respuestas HTTP apropiadas.

- **Reintentos inteligentes**: Sistema de reintentos con backoff exponencial que reduce la carga en la API y mejora la fiabilidad.

- **Logging mejorado**: Registro detallado de excepciones con toda la información necesaria para el diagnóstico.

Este sistema garantiza que los usuarios reciban mensajes claros cuando ocurren problemas, y que el equipo técnico disponga de toda la información necesaria para diagnosticar y resolver problemas rápidamente.

### Limpieza de Código Legacy

Se ha realizado una importante limpieza de código legacy:

- **Eliminación de modelos antiguos**: Se han eliminado las clases `Resumen`, `Traduccion` y `Clasificacion` que ya no se utilizaban.

- **Limpieza del Makefile**: Se han comentado o eliminado referencias a endpoints que no existen en el código, como `/api/v1/mcp/invoke`.

- **Eliminación de migraciones obsoletas**: Archivos de migración obsoletos como `003_migrate_legacy_to_unified.sql` y `02_migrate_legacy_to_unified.sql` han sido eliminados.

- **Actualización de documentación**: Tanto el README como esta guía se han actualizado para reflejar con precisión el estado actual del proyecto.

Estas limpiezas ayudan a mantener el código más mantenible y comprensible, eliminando fuentes potenciales de confusión para los desarrolladores que trabajen en el proyecto en el futuro.