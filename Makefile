# 🧠 AI Personal Workflow Assistant – Makefile

.PHONY: up down build build-fast logs restart fast-restart ps reset-db help ngrok-telegram test clean install

# === Variables ===
DOCKER_COMPOSE = docker compose
POSTGRES_CONTAINER = ai-workflow-db
API_URL = http://localhost:8000
N8N_URL = http://localhost:5678

# === Comandos básicos ===

## Levanta todos los servicios con Docker Compose
up: check-env
	$(DOCKER_COMPOSE) up -d

## Detiene todos los servicios
down:
	$(DOCKER_COMPOSE) down

## Reconstruye la imagen del backend
build: check-env
	$(DOCKER_COMPOSE) build --no-cache backend

## Reconstruye la imagen del backend sin usar --no-cache
build-fast: check-env
	$(DOCKER_COMPOSE) build backend

## Reconstruye todas las imágenes (incluye backend con optimizaciones)
build-all: check-env
	$(DOCKER_COMPOSE) build --no-cache

## Muestra los logs del backend
logs:
	$(DOCKER_COMPOSE) logs -f backend

## Reinicia el backend (rebuild + restart)
restart: down build up

## Reinicio rápido (sin reconstruir imagen desde cero)
fast-restart: down build-fast up

# === Utilidades para desarrollo ===

## Abre una shell de psql dentro del contenedor de PostgreSQL
db:
	docker exec -it $(POSTGRES_CONTAINER) psql -U david -d workflowdb

# Ejemplos de curl comentados (endpoint /api/v1/mcp/invoke no implementado)
# curl-summarize:
# 	curl -X POST $(API_URL)/api/v1/mcp/invoke \
# 	  -H "Content-Type: application/json" \
# 	  -H "x-api-key: $${API_KEY}" \
# 	  -d '{
# 	    "task": "summarize",
# 	    "input": { "text": "Texto de prueba para resumir automáticamente..." },
# 	    "context": { "user_id": "demo_user" }
# 	  }' | jq .
#
# curl-translate:
# 	curl -X POST $(API_URL)/api/v1/mcp/invoke \
# 	  -H "Content-Type: application/json" \
# 	  -H "x-api-key: $${API_KEY}" \
# 	  -d '{
# 	    "task": "translate",
# 	    "input": { "text": "Hello world", "lang": "es" },
# 	    "context": { "user_id": "demo_user" }
# 	  }' | jq .
#
# curl-classify:
# 	curl -X POST $(API_URL)/api/v1/mcp/invoke \
# 	  -H "Content-Type: application/json" \
# 	  -H "x-api-key: $${API_KEY}" \
# 	  -d '{
# 	    "task": "classify",
# 	    "input": { "text": "Este es un texto para clasificar" },
# 	    "context": { "user_id": "demo_user" }
# 	  }' | jq .

## Lista los contenedores en ejecución
ps:
	docker ps

## Borra volúmenes (⚠️ elimina datos persistentes)
reset-db:
	$(DOCKER_COMPOSE) down -v

## Limpia archivos temporales y caché
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# === Tests ===
test:
	pytest backend/tests -v

# === Instalación ===
install:
	pip install -r backend/requirements.txt

# === Ayuda ===
help:
	@echo "🧠 AI Personal Workflow Assistant"
	@echo "\nComandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[1;32m%-20s\033[0m %s\n", $$1, $$2}'
	@echo "\n  Comandos principales:"
	@echo "  \033[1;32mup                   \033[0m Inicia todos los servicios"
	@echo "  \033[1;32mdown                 \033[0m Detiene los servicios"
	@echo "  \033[1;32mbuild                \033[0m Reconstruye la imagen del backend"
	@echo "  \033[1;32mbuild-all            \033[0m Reconstruye todas las imágenes"
	@echo "  \033[1;32mlogs                 \033[0m Muestra logs del backend"
	@echo "  \033[1;32mrestart              \033[0m Reinicia los servicios"
	@echo "  \033[1;32mps                   \033[0m Lista contenedores activos"

# === Integraciones ===
ngrok-telegram:
	@echo "🔎 Obteniendo URL pública de ngrok..."
	@sleep 1
	@NGROK_URL=$$(curl -s localhost:4040/api/tunnels | jq -r '.tunnels[] | select(.proto=="https") | .public_url'); \
	if [ -z "$$NGROK_URL" ]; then \
	    echo "❌ No se encontró una URL HTTPS de ngrok. ¿Está corriendo ngrok?"; \
	    exit 1; \
	fi; \
	echo "🌍 URL pública: $$NGROK_URL"; \
	echo ""; \
	read -p "📋 URL local de n8n (http://localhost:5678/webhook/...): " URL_LOCAL; \
	URL_FINAL=$$(echo $$URL_LOCAL | sed "s|http://localhost:5678|$$NGROK_URL|"); \
	echo "🚀 Registrando webhook: $$URL_FINAL"; \
	curl -s $$URL_FINAL && echo "\n✅ Webhook registrado" || echo "\n❌ Error"

check-env:
	@if [ ! -f .env ]; then \
	    echo "❌ Error: .env file not found"; \
	    echo "💡 Tip: Copy .env.example to .env and fill in your values"; \
	    exit 1; \
	fi
	@echo "✅ .env file exists"

