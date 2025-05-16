from openai import AsyncOpenAI
import os
import logging
import asyncio
import openai
from services.db import (
    guardar_consulta,
    obtener_modo_usuario,
    limpiar_modo_usuario,
)
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
logger = setup_logger("services.tasks.classify")

# Initialize AsyncOpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=float(os.getenv("OPENAI_TIMEOUT", "30.0")),
    max_retries=0,  # Usamos nuestro propio sistema de reintentos
)


# Caché de clasificación
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
        OpenAITimeoutError: If OpenAI API times out
        OpenAIRateLimitError: If rate limit is exceeded
    """
    text = input.get("text", "")
    user_id = context.get("user_id", "desconocido")
    chat_id = int(user_id) if user_id.isdigit() else 0

    # Verificar si el usuario está en modo clasificación
    if chat_id > 0:
        modo_actual = await obtener_modo_usuario(chat_id)
        if modo_actual != "/clasificar":
            logger.info(
                f"Usuario {chat_id} no está en modo clasificación, está en: {modo_actual}"
            )
            # Si no está en modo clasificación, verificamos su modo actual
            if modo_actual:
                # Aquí se podría redirigir a otro servicio según el modo
                pass

    # Validate input
    if not text.strip():
        raise MissingParameterError("text")

    if not os.getenv("OPENAI_API_KEY"):
        raise OpenAIError(message="API key de OpenAI no configurada")

    try:
        logger.info(f"Clasificando texto para usuario {user_id}")
        # Llamar a la función protegida con reintentos
        response = await call_openai_with_retry(text)

        # Procesamiento de la respuesta
        clasificacion_raw = response.choices[0].message.content.strip()

        # Parsear la clasificación JSON-like
        clasificacion = parse_classification(clasificacion_raw)

        # Guardar en base de datos unificada
        try:
            if chat_id > 0:
                await limpiar_modo_usuario(chat_id)

            await guardar_consulta(
                user_id=user_id,
                tipo_tarea="clasificar",
                texto_original=text,
                resultado=clasificacion_raw,
                metadata={
                    "category": clasificacion.get("category", ""),
                    "urgency": clasificacion.get("urgency", ""),
                    "confidence": clasificacion.get("confidence", 0.0),
                    "model": "gpt-4o-mini-2024-07-18",
                },
            )
            logger.info("Clasificación guardada en base de datos")
        except Exception as e:
            logger.error(f"Error al guardar en base de datos: {str(e)}")
            # Continuamos aunque falle la persistencia

        return {
            "classification": clasificacion,
            "text_length": len(text),
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
        logger.error(f"Error inesperado al clasificar texto: {str(e)}")
        raise OpenAIError(message=f"Error al clasificar texto: {str(e)}")


# Parsea la respuesta de clasificación de OpenAI
def parse_classification(text: str) -> Dict[str, Any]:
    """
    Parsea la respuesta de clasificación de OpenAI

    Args:
        text: Respuesta textual de OpenAI

    Returns:
        Dict: Categoría y confianza
    """
    # Implementación simple - un parseo completo requeriría JSON.parse y manejo de errores
    result = {}

    # Extraer categoría
    if "categoría:" in text.lower():
        category_parts = text.lower().split("categoría:", 1)[1].split("\n", 1)
        if category_parts:
            result["category"] = category_parts[0].strip()

    # Intentar extraer nivel de urgencia
    if "urgencia:" in text.lower():
        urgency_parts = text.lower().split("urgencia:", 1)[1].split("\n", 1)
        if urgency_parts:
            urgency_text = urgency_parts[0].strip()
            if "alta" in urgency_text:
                result["urgency"] = "high"
            elif "media" in urgency_text:
                result["urgency"] = "medium"
            else:
                result["urgency"] = "low"

    # Extraer tema si existe
    if "tema:" in text.lower():
        theme_parts = text.lower().split("tema:", 1)[1].split("\n", 1)
        if theme_parts:
            result["theme"] = theme_parts[0].strip()

    # Confianza (default)
    result["confidence"] = 0.9

    return result


# Llama a la API de OpenAI con reintentos
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
                "content": """Clasifica el siguiente texto según:
                - Categoría: consulta/solicitud/informe/queja/urgencia/otro
                - Urgencia: alta/media/baja
                - Tema: recursos humanos/finanzas/IT/marketing/ventas/legal/otro

                Responde usando exactamente el formato:
                Categoría: [categoria]
                Urgencia: [urgencia]
                Tema: [tema]
                """,
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_tokens=100,
    )

    logger.debug("Respuesta recibida de OpenAI API")
    return response
