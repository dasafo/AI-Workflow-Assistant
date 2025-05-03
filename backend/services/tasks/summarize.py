from openai import OpenAI
import os
from services.db import guardar_resumen

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run(input: dict, context: dict) -> dict:
    text = input.get("text", "")
    user_id = context.get("user_id", "desconocido")

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": "Resume el siguiente texto de forma clara y concisa.",
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_tokens=200,
    )

    resumen = response.choices[0].message.content.strip()

    # Persistencia
    guardar_resumen(user_id, text, resumen)

    return {"summary": resumen}
