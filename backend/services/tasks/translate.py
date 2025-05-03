import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run(input_data: dict, context: dict) -> dict:
    text = input_data.get("text", "")
    target_lang = input_data.get("target_lang", "en")  # default: inglés

    prompt = f"Traduce al idioma '{target_lang}':\n\n{text}"

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": "Eres un traductor profesional que respeta el significado y el tono del texto.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=300,
    )

    translated_text = response.choices[0].message.content.strip()

    return {"translation": translated_text, "input": input_data, "context": context}
