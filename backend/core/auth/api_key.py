import os
from fastapi import Depends, HTTPException, Header, status, Request
from core.logging import setup_logger

logger = setup_logger("core.auth.api_key")

# Obtener API_KEY del entorno, con valor por defecto seguro en desarrollo
API_KEY = os.getenv("API_KEY", "")

# Verificar que se ha configurado API_KEY
if not API_KEY:
    logger.warning(
        "⚠️ API_KEY no configurada en variables de entorno. La API no estará protegida!"
    )


def verify_api_key(
    request: Request,
    x_api_key: str = Header(..., description="API Key para autenticación"),
):
    """
    Verifica la API Key proporcionada en el header x-api-key.

    Args:
        request: Request de FastAPI
        x_api_key: API Key proporcionada en el header

    Returns:
        str: API Key válida

    Raises:
        HTTPException: Si la API Key es inválida o no ha sido proporcionada
    """
    # Permitir health check sin api key
    if request.url.path == "/health" or request.url.path == "/api/v1/health":
        return x_api_key

    # En modo desarrollo, si no hay API_KEY configurada, permitir todas las peticiones
    # pero registrar una advertencia
    if not API_KEY:
        logger.warning(
            f"⚠️ Solicitud sin validación de API_KEY: {request.method} {request.url.path}"
        )
        return x_api_key

    # En producción, verificar API_KEY
    if x_api_key != API_KEY:
        # Registrar intento no autorizado con información limitada por seguridad
        logger.warning(
            f"🔒 Intento de acceso no autorizado: {request.client.host} - {request.method} {request.url.path}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return x_api_key
