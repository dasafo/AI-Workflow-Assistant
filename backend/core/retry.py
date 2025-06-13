"""
Este módulo proporciona un decorador para reintentar funciones asíncronas en caso de excepciones específicas.

Utiliza un enfoque de backoff exponencial con jitter para controlar el tiempo de espera entre reintentos.

"""
import asyncio
import functools
import os
import time
from typing import TypeVar, Callable, Awaitable, Optional, Any, Dict, List, Union, Type
from core.logging import setup_logger

logger = setup_logger("core.retry")

# T: Tipo de retorno de la función
T = TypeVar("T")

# Configuración desde variables de entorno
MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
RETRY_DELAY_BASE = float(os.getenv("OPENAI_RETRY_DELAY_BASE", "1.0"))
RETRY_DELAY_MAX = float(os.getenv("OPENAI_RETRY_DELAY_MAX", "10.0"))
RETRY_JITTER = float(os.getenv("OPENAI_RETRY_JITTER", "0.1"))

# Lista de excepciones que son retryables
RETRYABLE_EXCEPTIONS: List[Type[Exception]] = [
    TimeoutError,
    ConnectionError,
    ConnectionRefusedError,
    ConnectionResetError,
    asyncio.TimeoutError,
]

# Intentamos importar OpenAI exceptions
try:
    from openai import (
        RateLimitError,
        APIConnectionError,
        APITimeoutError,
        InternalServerError,
    )

    RETRYABLE_EXCEPTIONS.extend(
        [RateLimitError, APIConnectionError, APITimeoutError, InternalServerError]
    )
    logger.info("OpenAI exceptions loaded for retry handling")
except ImportError:
    logger.warning("OpenAI exceptions not found, retry will use basic exceptions only")


# Calcula el tiempo de espera con backoff exponencial y jitter
def exponential_backoff(retry_count: int) -> float:
    """
    Calcula el tiempo de espera con backoff exponencial y jitter

    Args:
        retry_count: Número de intento actual

    Returns:
        float: Tiempo de espera en segundos
    """
    delay = min(RETRY_DELAY_MAX, RETRY_DELAY_BASE * (2 ** (retry_count - 1)))
    jitter = delay * RETRY_JITTER * (2 * (0.5 - (time.time() % 1)))  # Jitter aleatorio
    return max(0, delay + jitter)  # Aseguramos que no sea negativo


def is_retryable_exception(exception: Exception) -> bool:
    """
    Determina si una excepción debe provocar un reintento

    Args:
        exception: La excepción a evaluar

    Returns:
        bool: True si se debe reintentar, False en caso contrario
    """
    for exception_class in RETRYABLE_EXCEPTIONS:
        if isinstance(exception, exception_class):
            return True

    # Comprobación específica para errores OpenAI por mensaje
    error_msg = str(exception).lower()
    if any(
        term in error_msg
        for term in [
            "timeout",
            "rate limit",
            "exceeded",
            "server error",
            "connection",
            "503",
            "429",
        ]
    ):
        return True

    return False


def async_retry(
    max_retries: Optional[int] = None,
    retryable_exceptions: Optional[List[Type[Exception]]] = None,
    on_retry: Optional[Callable[[int, Exception], Awaitable[None]]] = None,
):
    """
    Decorador para reintentar funciones asíncronas en caso de excepciones específicas

    Args:
        max_retries: Número máximo de reintentos (None usa el valor por defecto)
        retryable_exceptions: Lista de excepciones que provocan reintentos (None usa la lista por defecto)
        on_retry: Callback ejecutado antes de cada reintento

    Returns:
        Callable: Decorador configurado
    """
    _max_retries = max_retries if max_retries is not None else MAX_RETRIES
    _retryable_exceptions = (
        retryable_exceptions if retryable_exceptions is not None else None
    )

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for retry_count in range(
                1, _max_retries + 2
            ):  # +2 porque el primer intento no es reintento
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Decidir si reintentamos
                    should_retry = False
                    if _retryable_exceptions:
                        if any(
                            isinstance(e, ex_class)
                            for ex_class in _retryable_exceptions
                        ):
                            should_retry = True
                    else:
                        should_retry = is_retryable_exception(e)

                    # Si estamos en el último intento o no es retryable, propagamos la excepción
                    if retry_count > _max_retries or not should_retry:
                        logger.warning(
                            f"Error no reintentable o máximo de reintentos alcanzado: {type(e).__name__}: {str(e)}"
                        )
                        raise

                    # Calculamos el tiempo de espera
                    delay = exponential_backoff(retry_count)

                    # Log del reintento
                    logger.warning(
                        f"Reintento {retry_count}/{_max_retries} después de error: "
                        f"{type(e).__name__}: {str(e)}. Esperando {delay:.2f}s"
                    )

                    # Ejecutar callback si existe
                    if on_retry:
                        await on_retry(retry_count, e)

                    # Esperar antes de reintentar
                    await asyncio.sleep(delay)

            # Este punto nunca debería alcanzarse, pero por si acaso
            if last_exception:
                raise last_exception
            raise RuntimeError("Error desconocido en sistema de reintentos")

        return wrapper

    return decorator


# Uso simple sin parámetros adicionales para cualquier función
def with_retry(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """
    Decorador simple para aplicar la política de reintentos por defecto

    Args:
        func: Función asíncrona a decorar

    Returns:
        Callable: Función decorada con reintentos
    """
    return async_retry()(func)
