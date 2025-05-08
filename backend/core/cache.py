import os
import json
import hashlib
import redis
from typing import Dict, Any, Optional, Callable, TypeVar, ParamSpec, cast
import functools
import logging
from core.logging import setup_logger

# Configuración del logger
logger = setup_logger("core.cache")

# Configuración de Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_EXPIRE = int(os.getenv("REDIS_CACHE_TTL", "86400"))  # 24 horas por defecto

# Inicializar conexión Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
    socket_connect_timeout=5,
)

# Define tipos para los decoradores
T = TypeVar("T")
P = ParamSpec("P")


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Genera una clave de caché única basada en los argumentos

    Args:
        prefix: Prefijo para la clave (generalmente el nombre de la función)
        *args: Argumentos posicionales
        **kwargs: Argumentos con nombre

    Returns:
        str: Clave de caché única
    """
    # Creamos una representación de cadena de los argumentos
    args_str = json.dumps(args, sort_keys=True)
    kwargs_str = json.dumps(kwargs, sort_keys=True)

    # Generamos un hash para crear una clave compacta
    key_hash = hashlib.md5(f"{args_str}:{kwargs_str}".encode()).hexdigest()

    return f"{prefix}:{key_hash}"


def cache_response(
    ttl: int = REDIS_EXPIRE,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorador para cachear respuestas de funciones

    Args:
        ttl: Tiempo de vida en segundos para la entrada en caché

    Returns:
        Callable: Función decorada con capacidad de caché
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Generamos clave de caché única para esta función y argumentos
            cache_key = generate_cache_key(func.__name__, *args, **kwargs)

            try:
                # Intentamos obtener del caché
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for key: {cache_key}")
                    return cast(T, json.loads(cached_result))

                # Si no está en caché, llamamos a la función original
                logger.info(f"Cache miss for key: {cache_key}")
                result = func(*args, **kwargs)

                # Guardamos en caché
                redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(
                        result, default=str
                    ),  # default=str para manejar tipos no serializables
                )

                return result
            except redis.RedisError as e:
                # Si hay un error con Redis, log y continuamos sin caché
                logger.error(f"Redis error: {str(e)}")
                return func(*args, **kwargs)

        return wrapper

    return decorator


def clear_cache(prefix: Optional[str] = None) -> None:
    """
    Limpia las entradas de caché con el prefijo dado

    Args:
        prefix: Prefijo de las claves a eliminar. Si es None, elimina todas.
    """
    try:
        if prefix:
            # Eliminar claves con el prefijo especificado
            cursor = 0
            while True:
                cursor, keys = redis_client.scan(cursor, f"{prefix}:*", 100)
                if keys:
                    redis_client.delete(*keys)
                if cursor == 0:
                    break
            logger.info(f"Cleared cache with prefix: {prefix}")
        else:
            # Eliminar todas las claves (flushdb)
            redis_client.flushdb()
            logger.info("Cleared all cache entries")
    except redis.RedisError as e:
        logger.error(f"Error clearing cache: {str(e)}")


def get_cache_health() -> Dict[str, Any]:
    """
    Comprueba el estado de la conexión Redis

    Returns:
        Dict: Estado de la conexión Redis
    """
    try:
        # Prueba simple de Redis
        redis_client.ping()
        return {"status": "healthy", "details": "Redis connection OK"}
    except redis.RedisError as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {"status": "unhealthy", "details": str(e)}
