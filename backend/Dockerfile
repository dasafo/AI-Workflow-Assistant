# Stage 1: Builder - para compilar dependencias
FROM python:3.11-alpine AS builder

# Instalar dependencias para compilación
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libpq-dev \
    postgresql-dev

# Set working directory
WORKDIR /build

# Copiar solo requirements
COPY requirements.txt .

# Instalar dependencias en modo "wheel"
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# Stage 2: Final - imagen final con solo las dependencias necesarias
FROM python:3.11-alpine

# Add labels for better maintainability
LABEL maintainer="David" \
      description="AI Personal Workflow Assistant Backend" \
      version="1.0.0"

# Set essential environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PYTHONPATH=/app/backend

# Instalar dependencias runtime mínimas
RUN apk add --no-cache \
    libpq \
    curl

# Crear usuario no-root 
RUN addgroup -S appuser && adduser -S appuser -G appuser

# Set working directory
WORKDIR /app

# Copiar wheels del stage de build
COPY --from=builder /wheels /wheels

# Instalar dependencias desde wheels (mucho más rápido)
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copiar código de la aplicación
COPY . .

# Corregir permisos
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE $PORT

# Eliminamos el HEALTHCHECK de aquí ya que lo manejamos en docker-compose

# Start application - eliminamos flag --reload en producción
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]