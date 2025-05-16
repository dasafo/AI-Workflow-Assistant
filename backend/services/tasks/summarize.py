from openai import AsyncOpenAI
import os
from services.db import guardar_consulta
from typing import Dict, Any
from core.logging import setup_logger
from core.cache import cache_response
from core.retry import with_retry
from core.errors import (
    OpenAIError,
    MissingParameterError,
    OpenAITimeoutError,
    OpenAIRateLimitError,
)
import asyncio
import openai

# Configure logging
logger = setup_logger("services.tasks.summarize")

# Initialize AsyncOpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=float(os.getenv("OPENAI_TIMEOUT", "30.0")),
    max_retries=0,  # Usamos nuestro propio sistema de reintentos
)


# Caché de resumen
@cache_response(
    ttl=int(os.getenv("SUMMARY_CACHE_TTL", "86400"))
)  # 24 horas por defecto
async def run(input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Summarize text using OpenAI's GPT model asynchronously

    Args:
        input: Dictionary containing the text to summarize
        context: Dictionary containing user context information

    Returns:
        Dictionary containing the summary and length information

    Raises:
        MissingParameterError: If text is empty
        OpenAIError: For OpenAI API related errors
        OpenAITimeoutError: If OpenAI API times out
        OpenAIRateLimitError: If rate limit is exceeded
    """
    text = input.get("text", "")
    user_id = context.get("user_id", "desconocido")

    # Validate input
    if not text.strip():
        raise MissingParameterError("text")

    if not os.getenv("OPENAI_API_KEY"):
        raise OpenAIError(message="API key de OpenAI no configurada")

    try:
        logger.info(f"Generando resumen para usuario {user_id}")
        # Llamar a la función protegida con reintentos
        response = await call_openai_with_retry(text)

        resumen = response.choices[0].message.content.strip()

        # Persistencia en la tabla unificada
        try:
            await guardar_consulta(
                user_id=user_id,
                tipo_tarea="resumir",
                texto_original=text,
                resultado=resumen,
                metadata={
                    "model": "gpt-4o-mini-2024-07-18",
                    "original_length": len(text),
                    "summary_length": len(resumen),
                },
            )
            logger.info("Resumen guardado en base de datos")
        except Exception as e:
            logger.error(f"Error al guardar en base de datos: {str(e)}")
            # Continuamos aunque falle la persistencia

        return {
            "summary": resumen,
            "original_length": len(text),
            "summary_length": len(resumen),
            "model_used": "gpt-4o-mini-2024-07-18",
            "cached": False,
        }

    # Manejo de excepciones
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout al conectar con OpenAI: {str(e)}")
        timeout_value = float(os.getenv("OPENAI_TIMEOUT", "30.0"))
        raise OpenAITimeoutError(
            timeout=timeout_value, details={"error_type": "asyncio.TimeoutError"}
        )
    except openai.RateLimitError as e:
        logger.error(f"Rate limit excedido en OpenAI: {str(e)}")
        raise OpenAIRateLimitError(details={"original_error": str(e)})
    except openai.APIError as e:
        logger.error(f"Error de API de OpenAI: {str(e)}")
        raise OpenAIError(message=f"Error en la API de OpenAI: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado al generar resumen: {str(e)}")
        raise OpenAIError(message=f"Error al generar resumen: {str(e)}")


@with_retry
async def call_openai_with_retry(text: str):
    """
    Función protegida con reintentos para llamar a la API de OpenAI

    Args:
        text: Texto a resumir

    Returns:
        Respuesta de OpenAI
    """
    logger.debug("Llamando a OpenAI API para resumir texto...")

    response = await client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": "Resume el texto de forma clara y concisa y termina siempre en un punto y nunca abruptamente.",
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_tokens=200,
    )

    logger.debug("Respuesta recibida de OpenAI API")
    return response
