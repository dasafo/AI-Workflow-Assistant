from openai import OpenAI
import os
from services.db import guardar_clasificacion

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run(input: dict, context: dict) -> dict:
    text = input.get("text", "")
    user_id = context.get("user_id", "desconocido")

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

    guardar_clasificacion(user_id, text, clasificacion)

    return {"classification": clasificacion}
