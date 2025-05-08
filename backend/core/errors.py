from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from core.logging import setup_logger

logger = setup_logger("core.errors")

# Definición de códigos de error
ERROR_CODES = {
    # Errores de autenticación (1xx)
    "INVALID_API_KEY": "E101",
    "MISSING_API_KEY": "E102",
    "EXPIRED_TOKEN": "E103",
    # Errores de validación (2xx)
    "INVALID_INPUT": "E201",
    "MISSING_PARAMETER": "E202",
    "INVALID_TASK": "E203",
    # Errores de servicios externos (3xx)
    "OPENAI_API_ERROR": "E301",
    "OPENAI_TIMEOUT": "E302",
    "OPENAI_RATE_LIMIT": "E303",
    "OPENAI_CONTENT_FILTER": "E304",
    # Errores de base de datos (4xx)
    "DB_CONNECTION_ERROR": "E401",
    "DB_QUERY_ERROR": "E402",
    "DB_TRANSACTION_ERROR": "E403",
    # Errores de redis (5xx)
    "REDIS_CONNECTION_ERROR": "E501",
    "REDIS_OPERATION_ERROR": "E502",
    # Errores internos (9xx)
    "INTERNAL_SERVER_ERROR": "E901",
    "NOT_IMPLEMENTED": "E902",
    "UNKNOWN_ERROR": "E999",
}


class APIError(Exception):
    """
    Excepción base para errores de API.
    Incluye código de error, mensaje, y detalles opcionales.
    """

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.code = ERROR_CODES.get(code, ERROR_CODES["UNKNOWN_ERROR"])
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

        # Log del error
        logger.error(
            f"Error {self.code}: {self.message} | "
            f"Status: {self.status_code} | "
            f"Details: {self.details}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el error a un diccionario para la respuesta JSON"""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }

    def to_http_exception(self) -> HTTPException:
        """Convierte el error a una excepción HTTP para FastAPI"""
        return HTTPException(
            status_code=self.status_code,
            detail=self.to_dict(),
        )


# Errores de autenticación
class AuthenticationError(APIError):
    """Error de autenticación"""

    def __init__(
        self,
        code: str = "INVALID_API_KEY",
        message: str = "Credenciales de autenticación inválidas",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code, message, details, status_code=status.HTTP_401_UNAUTHORIZED
        )


class InvalidAPIKeyError(AuthenticationError):
    """API Key inválida"""

    def __init__(self, message: str = "API Key inválida o no proporcionada"):
        super().__init__("INVALID_API_KEY", message)


# Errores de validación
class ValidationError(APIError):
    """Error de validación de datos"""

    def __init__(
        self,
        code: str = "INVALID_INPUT",
        message: str = "Datos de entrada inválidos",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code, message, details, status_code=status.HTTP_400_BAD_REQUEST
        )


class InvalidTaskError(ValidationError):
    """Tarea no soportada o inválida"""

    def __init__(self, task: str):
        super().__init__(
            "INVALID_TASK",
            f"Tarea no soportada: {task}",
            {"task": task},
        )


class MissingParameterError(ValidationError):
    """Parámetro requerido no proporcionado"""

    def __init__(self, parameter: str):
        super().__init__(
            "MISSING_PARAMETER",
            f"Falta parámetro requerido: {parameter}",
            {"parameter": parameter},
        )


# Errores de OpenAI
class OpenAIError(APIError):
    """Error al interactuar con la API de OpenAI"""

    def __init__(
        self,
        code: str = "OPENAI_API_ERROR",
        message: str = "Error en la API de OpenAI",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_502_BAD_GATEWAY,
    ):
        super().__init__(code, message, details, status_code)


class OpenAITimeoutError(OpenAIError):
    """Timeout en la llamada a OpenAI"""

    def __init__(self, timeout: float = 0, details: Optional[Dict[str, Any]] = None):
        timeout_msg = f" después de {timeout} segundos" if timeout > 0 else ""
        super().__init__(
            "OPENAI_TIMEOUT",
            f"Timeout en la conexión con OpenAI{timeout_msg}",
            details,
        )


class OpenAIRateLimitError(OpenAIError):
    """Rate limit excedido en OpenAI"""

    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            "OPENAI_RATE_LIMIT",
            "Se ha excedido el límite de peticiones a OpenAI",
            details,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class OpenAIContentFilterError(OpenAIError):
    """Contenido filtrado por políticas de OpenAI"""

    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            "OPENAI_CONTENT_FILTER",
            "El contenido ha sido filtrado por políticas de OpenAI",
            details,
        )


# Errores de base de datos
class DatabaseError(APIError):
    """Error relacionado con la base de datos"""

    def __init__(
        self,
        code: str = "DB_CONNECTION_ERROR",
        message: str = "Error de conexión a la base de datos",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code, message, details, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Errores de Redis
class RedisError(APIError):
    """Error relacionado con Redis"""

    def __init__(
        self,
        code: str = "REDIS_CONNECTION_ERROR",
        message: str = "Error de conexión a Redis",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code, message, details, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Errores internos
class InternalServerError(APIError):
    """Error interno del servidor"""

    def __init__(
        self,
        message: str = "Error interno del servidor",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            "INTERNAL_SERVER_ERROR",
            message,
            details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Función para mapear excepciones estándar a nuestras excepciones personalizadas
def handle_exception(exc: Exception) -> APIError:
    """
    Convierte una excepción estándar a nuestro formato de error

    Args:
        exc: Excepción a convertir

    Returns:
        APIError: Error en nuestro formato estándar
    """
    # Intentamos detectar el tipo de error por el mensaje
    error_msg = str(exc).lower()

    # OpenAI errores
    if any(term in error_msg for term in ["openai", "api key", "gpt", "model"]):
        if "timeout" in error_msg:
            return OpenAITimeoutError(details={"original_error": str(exc)})
        elif any(
            term in error_msg
            for term in ["rate limit", "ratelimit", "too many requests", "429"]
        ):
            return OpenAIRateLimitError(details={"original_error": str(exc)})
        elif any(
            term in error_msg for term in ["content", "filter", "policy", "blocked"]
        ):
            return OpenAIContentFilterError(details={"original_error": str(exc)})
        else:
            return OpenAIError(message=str(exc), details={"original_error": str(exc)})

    # Errores de base de datos
    elif any(
        term in error_msg
        for term in ["database", "db", "sql", "postgres", "connection"]
    ):
        return DatabaseError(message=str(exc), details={"original_error": str(exc)})

    # Errores de Redis
    elif "redis" in error_msg:
        return RedisError(message=str(exc), details={"original_error": str(exc)})

    # Por defecto, devolvemos un error interno genérico
    return InternalServerError(
        message="Se ha producido un error inesperado",
        details={"original_error": str(exc), "error_type": type(exc).__name__},
    )
