import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run(input_data: dict, context: dict) -> dict:
    text = input_data.get("text", "")

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": "Clasifica el texto en: educación, negocios, ciencia, salud, entretenimiento, política, tecnología u otro.",
            },
            {"role": "user", "content": f"Clasifica este texto:\n\n{text}"},
        ],
        temperature=0,
        max_tokens=100,
    )

    category = response.choices[0].message.content.strip()

    return {"category": category, "input": input_data, "context": context}
