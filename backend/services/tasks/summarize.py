import os
from openai import OpenAI
from db import guardar_resumen

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run(input_data: dict, context: dict) -> dict:
    text = input_data.get("text", "")
    user_id = context.get("user_id", "desconocido")

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente que resume textos de forma concisa y clara.",
            },
            {"role": "user", "content": f"Resume el siguiente texto:\n\n{text}"},
        ],
        temperature=0.3,
        max_tokens=200,
    )

    summary = response.choices[0].message.content.strip()
    guardar_resumen(user_id, text, summary)

    return {"summary": summary, "input": input_data, "context": context}
