from openai import OpenAI
import os
import logging
from services.db import guardar_traduccion
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run(input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate text using OpenAI's GPT model

    Args:
        input: Dictionary containing the text to translate and target language
        context: Dictionary containing user context information

    Returns:
        Dictionary containing the translation and language information

    Raises:
        ValueError: If text is empty or API key is missing
    """
    text = input.get("text", "")
    lang = input.get("lang", "en")
    user_id = context.get("user_id", "desconocido")

    # Validate input
    if not text.strip():
        raise ValueError("El texto no puede estar vacío")

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("API key de OpenAI no configurada")

    try:
        logger.info(f"Traduciendo texto para usuario {user_id} al idioma {lang}")
        response = client.chat.completions.create(
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

        traduccion = response.choices[0].message.content.strip()

        # Persistencia
        try:
            guardar_traduccion(user_id, text, lang, traduccion)
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
        }

    except Exception as e:
        logger.error(f"Error al traducir texto: {str(e)}")
        raise ValueError(f"Error al traducir texto: {str(e)}")
