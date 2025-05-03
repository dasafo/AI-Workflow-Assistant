from openai import OpenAI
import os
from services.db import guardar_traduccion

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run(input: dict, context: dict) -> dict:
    text = input.get("text", "")
    lang = input.get("lang", "en")
    user_id = context.get("user_id", "desconocido")

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

    guardar_traduccion(user_id, text, lang, traduccion)

    return {"translation": traduccion, "language": lang}
