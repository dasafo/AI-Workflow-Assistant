from openai import AsyncOpenAI
import os
import logging
import asyncio
import openai
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

# Configure logging
logger = setup_logger("services.tasks.translate")

# Initialize AsyncOpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=float(os.getenv("OPENAI_TIMEOUT", "30.0")),
    max_retries=0,  # Usamos nuestro propio sistema de reintentos
)


# Caché de traducción
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
        OpenAITimeoutError: If OpenAI API times out
        OpenAIRateLimitError: If rate limit is exceeded
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
        logger.info(f"Traduciendo texto para usuario {user_id}")

        # Detectar idioma origen (simplificado)
        source_lang = detect_language(text)

        # Determinar idioma destino (si el origen es español, traducir a inglés y viceversa)
        target_lang = "en" if source_lang == "es" else "es"
        if lang and lang != source_lang:
            target_lang = lang

        # Llamar a OpenAI con retry
        response = await call_openai_with_retry(text, source_lang, target_lang)

        traduccion = response.choices[0].message.content.strip()

        # Guardar en BD unificada
        try:
            await guardar_consulta(
                user_id=user_id,
                tipo_tarea="traducir",
                texto_original=text,
                resultado=traduccion,
                metadata={
                    "idioma": target_lang,
                    "idioma_origen": source_lang,
                    "model": "gpt-4o-mini-2024-07-18",
                },
            )
            logger.info(
                f"Traducción guardada en base de datos ({source_lang} -> {target_lang})"
            )
        except Exception as e:
            logger.error(f"Error al guardar traducción en base de datos: {str(e)}")
            # Continuamos aunque falle la persistencia

        return {
            "translation": traduccion,
            "source_language": source_lang,
            "target_language": target_lang,
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
        logger.error(f"Error inesperado al traducir texto: {str(e)}")
        raise OpenAIError(message=f"Error al traducir texto: {str(e)}")


# Detecta el idioma del texto (implementación simplificada)
def detect_language(text: str) -> str:
    """
    Detecta el idioma del texto (implementación simplificada)

    Args:
        text: Texto a analizar

    Returns:
        str: Código de idioma detectado ('es' o 'en')
    """
    # Implementación básica que asume que los textos con más caracteres
    # españoles que ingleses están en español
    spanish_chars = set("áéíóúüñ¿¡")
    english_specific = set("wk")
    # Contar caracteres específicos de español y inglés
    spanish_count = sum(1 for c in text.lower() if c in spanish_chars)
    english_count = sum(1 for c in text.lower() if c in english_specific)

    # Si tiene caracteres específicos de español, asumimos español
    if spanish_count > 0:
        return "es"
    # Si tiene muchos caracteres específicos de inglés, asumimos inglés
    elif english_count > 1:
        return "en"
    # Por defecto, asumimos inglés (la mayoría de los textos)
    else:
        return "en"


@with_retry
async def call_openai_with_retry(text: str, source_lang: str, target_lang: str):
    """
    Función protegida con reintentos para llamar a la API de OpenAI

    Args:
        text: Texto a traducir
        source_lang: Idioma origen
        target_lang: Idioma destino

    Returns:
        Respuesta de OpenAI
    """
    logger.debug(
        f"Llamando a OpenAI API para traducir texto de {source_lang} a {target_lang}..."
    )

    # Construir el prompt según el idioma destino
    if target_lang == "es":
        system_prompt = "Traduce el siguiente texto del inglés al español, manteniendo el tono y formato original."
    else:
        system_prompt = "Translate the following text from Spanish to English, maintaining the original tone and format."

    response = await client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_tokens=300,
    )

    logger.debug("Respuesta recibida de OpenAI API")
    return response
