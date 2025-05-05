from openai import OpenAI
import os
import logging
from services.db import guardar_clasificacion
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run(input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify text using OpenAI's GPT model

    Args:
        input: Dictionary containing the text to classify
        context: Dictionary containing user context information

    Returns:
        Dictionary containing the classification and confidence information

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
        logger.info(f"Clasificando texto para usuario {user_id}")
        response = client.chat.completions.create(
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

        clasificacion = response.choices[0].message.content.strip()

        # Persistencia
        try:
            guardar_clasificacion(user_id, text, clasificacion)
            logger.info("Clasificación guardada en base de datos")
        except Exception as e:
            logger.error(f"Error al guardar en base de datos: {str(e)}")
            # Continuamos aunque falle la persistencia

        return {
            "classification": clasificacion,
            "text_length": len(text),
            "confidence": "high",  # Podríamos obtenerlo del modelo
            "model_used": "gpt-4o-mini-2024-07-18",
        }

    except Exception as e:
        logger.error(f"Error al clasificar texto: {str(e)}")
        raise ValueError(f"Error al clasificar texto: {str(e)}")
