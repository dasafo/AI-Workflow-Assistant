from openai import AsyncOpenAI
import os
import logging
from services.db import guardar_clasificacion
from typing import Dict, Any
from core.logging import setup_logger
from core.cache import cache_response
from core.retry import with_retry
from core.errors import OpenAIError, MissingParameterError

# Configure logging
logger = setup_logger("services.tasks.classify")

# Initialize AsyncOpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=float(os.getenv("OPENAI_TIMEOUT", "30.0")),
    max_retries=0,  # Usamos nuestro propio sistema de reintentos
)


@cache_response(
    ttl=int(os.getenv("CLASSIFICATION_CACHE_TTL", "86400"))
)  # 24 horas por defecto
async def run(input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify text using OpenAI's GPT model asynchronously

    Args:
        input: Dictionary containing the text to classify
        context: Dictionary containing user context information

    Returns:
        Dictionary containing the classification and confidence information

    Raises:
        MissingParameterError: If text is empty
        OpenAIError: For OpenAI API related errors
    """
    text = input.get("text", "")
    user_id = context.get("user_id", "desconocido")

    # Validate input
    if not text.strip():
        raise MissingParameterError("text")

    if not os.getenv("OPENAI_API_KEY"):
        raise OpenAIError(message="API key de OpenAI no configurada")

    try:
        logger.info(f"Clasificando texto para usuario {user_id}")
        # Llamar a la función protegida con reintentos
        response = await call_openai_with_retry(text)

        clasificacion = response.choices[0].message.content.strip()

        # Persistencia
        try:
            await guardar_clasificacion(user_id, text, clasificacion)
            logger.info("Clasificación guardada en base de datos")
        except Exception as e:
            logger.error(f"Error al guardar en base de datos: {str(e)}")
            # Continuamos aunque falle la persistencia

        return {
            "classification": clasificacion,
            "text_length": len(text),
            "confidence": "high",  # Podríamos obtenerlo del modelo
            "model_used": "gpt-4o-mini-2024-07-18",
            "cached": False,
        }

    except Exception as e:
        logger.error(f"Error al clasificar texto: {str(e)}")
        raise OpenAIError(message=f"Error al clasificar texto: {str(e)}")


@with_retry
async def call_openai_with_retry(text: str):
    """
    Función protegida con reintentos para llamar a la API de OpenAI

    Args:
        text: Texto a clasificar

    Returns:
        Respuesta de OpenAI
    """
    logger.debug("Llamando a OpenAI API para clasificar texto...")

    response = await client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": "Clasifica este texto según su intención (por ejemplo: pregunta, información, opinión, urgente, irrelevante, etc.).",
            },
            {"role": "user", "content": text},
        ],
        temperature=0.2,
        max_tokens=100,
    )

    logger.debug("Respuesta recibida de OpenAI API")
    return response
