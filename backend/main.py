"""
Este archivo es el punto de entrada principal de la aplicación FastAPI.

Configura la aplicación FastAPI, define las rutas de la API, maneja excepciones y configura el registro de eventos.

"""
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from api.routes.router import api_router
from core.logging import setup_logger
from core.health import setup_health_routes
from core.errors import APIError, handle_exception

# Configura el logger
logger = setup_logger("main")

# Crear aplicación FastAPI
app = FastAPI(
    title="AI Workflow Assistant",
    description="API para automatización de tareas con IA",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Para producción, limitar a orígenes específicos(https://www.google.com, http://localhost:8000, etc.)
    allow_credentials=True,  # Para producción, establecer a False
    allow_methods=[
        "*"
    ],  # Para producción, limitar a métodos específicos(POST,GET,PUT,DELETE,...)
    allow_headers=["*"],  # Para producción, limitar a encabezados específicos
)

# Incluir rutas API
app.include_router(api_router, prefix="/api/v1")

# Configurar health check
setup_health_routes(app)


# Manejador global de excepciones
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """
    Manejador global para excepciones de tipo APIError

    Args:
        request: Request object
        exc: Excepción APIError lanzada

    Returns:
        JSONResponse: Respuesta JSON con formato estandarizado
    """
    logger.error(
        f"Error en endpoint {request.url.path}: {exc.code} - {exc.message}",
        extra={"details": exc.details},
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


# Manejador para excepciones no controladas
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Manejador para excepciones no manejadas explícitamente

    Args:
        request: Request object
        exc: Excepción no controlada

    Returns:
        JSONResponse: Respuesta JSON formateada con información del error
    """
    # Convertir excepción genérica a nuestro formato estándar
    api_error = handle_exception(exc)

    logger.error(
        f"Error no controlado en endpoint {request.url.path}: {str(exc)}",
        exc_info=True,
        extra={"error_type": type(exc).__name__},
    )

    return JSONResponse(
        status_code=api_error.status_code,
        content=api_error.to_dict(),
    )


def custom_openapi():
    """
    Personaliza el esquema OpenAPI para la aplicación FastAPI.

    Returns:
        dict: Esquema OpenAPI personalizado
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AI Workflow Assistant",
        version="1.0.0",
        description="API para automatización de tareas con IA",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Eventos de inicio/apagado
@app.on_event("startup")
async def startup_event():
    """
    Evento de inicio de la aplicación.

    Este evento se ejecuta cuando la aplicación FastAPI se inicia.
    Aquí puedes realizar cualquier inicialización necesaria, como establecer conexiones,
    configurar pools, etc.
    """
    logger.info("Iniciando aplicación...")
    # Inicializar aquí conexiones, pool, etc.


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento de apagado de la aplicación.

    Este evento se ejecuta cuando la aplicación FastAPI se apaga.
    Aquí puedes realizar cualquier limpieza necesaria, como cerrar conexiones, etc.
    """
    logger.info("Cerrando aplicación...")
    # Cerrar aquí conexiones, etc.


if __name__ == "__main__":
    """
    Punto de entrada principal de la aplicación FastAPI.

    Configura el servidor uvicorn para iniciar la aplicación FastAPI.
    """
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv(
        "LOG_LEVEL", "info"
    ).lower()  # info, debug, warning, error, critical

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level=log_level,
        reload=os.getenv("ENVIRONMENT", "development").lower()
        == "development",  # Para producción, establecer a False
    )
