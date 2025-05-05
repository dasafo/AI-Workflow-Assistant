from openai import OpenAI
import os
import logging
from services.db import guardar_resumen
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run(input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Summarize text using OpenAI's GPT model

    Args:
        input: Dictionary containing the text to summarize
        context: Dictionary containing user context information

    Returns:
        Dictionary containing the summary and length information

    Raises:
        ValueError: If text is empty or API key is missing
    """
    text = input.get("text", "")
    user_id = context.get("user_id", "desconocido")

    # Validate input
    if not text.strip():
        raise ValueError("El texto no puede estar vacío")

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("API key de OpenAI no configurada")

    try:
        logger.info(f"Generando resumen para usuario {user_id}")
        response = client.chat.completions.create(
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

        resumen = response.choices[0].message.content.strip()

        # Persistencia
        try:
            guardar_resumen(user_id, text, resumen)
            logger.info("Resumen guardado en base de datos")
        except Exception as e:
            logger.error(f"Error al guardar en base de datos: {str(e)}")
            # Continuamos aunque falle la persistencia

        return {
            "summary": resumen,
            "original_length": len(text),
            "summary_length": len(resumen),
            "model_used": "gpt-4o-mini-2024-07-18",
        }

    except Exception as e:
        logger.error(f"Error al generar resumen: {str(e)}")
        raise ValueError(f"Error al generar resumen: {str(e)}")
