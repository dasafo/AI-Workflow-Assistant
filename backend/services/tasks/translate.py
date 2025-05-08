from openai import AsyncOpenAI
import os
import logging
from services.db import guardar_traduccion
from typing import Dict, Any
from core.logging import setup_logger
from core.cache import cache_response
from core.retry import with_retry
from core.errors import OpenAIError, MissingParameterError

# Configure logging
logger = setup_logger("services.tasks.translate")

# Initialize AsyncOpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=float(os.getenv("OPENAI_TIMEOUT", "30.0")),
    max_retries=0,  # Usamos nuestro propio sistema de reintentos
)


@cache_response(
    ttl=int(os.getenv("TRANSLATION_CACHE_TTL", "86400"))
)  # 24 horas por defecto
async def run(input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate text using OpenAI's GPT model asynchronously

    Args:
        input: Dictionary containing the text to translate and target language
        context: Dictionary containing user context information

    Returns:
        Dictionary containing the translation and language information

    Raises:
        MissingParameterError: If text is empty
        OpenAIError: For OpenAI API related errors
    """
    text = input.get("text", "")
    lang = input.get("lang", "en")
    user_id = context.get("user_id", "desconocido")

    # Validate input
    if not text.strip():
        raise MissingParameterError("text")

    if not os.getenv("OPENAI_API_KEY"):
        raise OpenAIError(message="API key de OpenAI no configurada")

    try:
        logger.info(f"Traduciendo texto para usuario {user_id} al idioma {lang}")
        # Llamar a la función protegida con reintentos
        response = await call_openai_with_retry(text, lang)

        traduccion = response.choices[0].message.content.strip()

        # Persistencia
        try:
            await guardar_traduccion(user_id, text, lang, traduccion)
            logger.info("Traducción guardada en base de datos")
        except Exception as e:
            logger.error(f"Error al guardar en base de datos: {str(e)}")
            # Continuamos aunque falle la persistencia

        return {
            "translation": traduccion,
            "original_length": len(text),
            "translation_length": len(traduccion),
            "language": lang,
            "model_used": "gpt-4o-mini-2024-07-18",
            "cached": False,
        }

    except Exception as e:
        logger.error(f"Error al traducir texto: {str(e)}")
        raise OpenAIError(message=f"Error al traducir texto: {str(e)}")


@with_retry
async def call_openai_with_retry(text: str, lang: str):
    """
    Función protegida con reintentos para llamar a la API de OpenAI

    Args:
        text: Texto a traducir
        lang: Idioma de destino

    Returns:
        Respuesta de OpenAI
    """
    logger.debug(f"Llamando a OpenAI API para traducir texto al {lang}...")

    response = await client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": f"Traduce el siguiente texto al idioma {lang}.",
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_tokens=400,
    )

    logger.debug("Respuesta recibida de OpenAI API")
    return response
