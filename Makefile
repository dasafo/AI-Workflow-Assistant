# 🧠 AI Personal Workflow Assistant – Makefile

# === Comandos básicos ===

## Levanta todos los servicios con Docker Compose
up:
	docker compose up -d

## Detiene todos los servicios
stop:
	docker compose down

## Reconstruye la imagen del backend
build:
	docker compose build backend

## Muestra los logs del backend
logs:
	docker compose logs -f backend

## Reinicia el backend (rebuild + restart)
restart:
	docker compose down && docker compose build backend && docker compose up -d

# === Utilidades para desarrollo ===

## Abre una shell de psql dentro del contenedor de PostgreSQL
db:
	docker exec -it ai-workflow-assistant-postgres-1 psql -U david -d workflowdb

## Prueba el endpoint de resumen (requiere backend levantado)
curl:
	curl -X POST http://localhost:8000/mcp/invoke \
	  -H "Content-Type: application/json" \
	  -d '{
	    "task": "summarize",
	    "input": { "text": "Texto de prueba para resumir automáticamente..." },
	    "context": { "user_id": "demo_user" }
	  }' | jq .

## Lista los contenedores en ejecución
ps:
	docker ps

## Borra volúmenes (⚠️ elimina datos persistentes como la base de datos)
reset-db:
	docker compose down -v

# === Ayuda ===

## Muestra la lista de comandos disponibles
help:
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[1;32m%-20s\033[0m %s\n", $$1, $$2}'
