from fastapi import APIRouter, Header, HTTPException
from .schemas import InputMessage, OutputMessage
from db import guardar_resumen
import os
from openai import OpenAI

router = APIRouter()

# ✅ Nueva forma con SDK >=1.0.0
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_summary_with_openai(text: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # o gpt-4o-mini-2024-07-18
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
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[ERROR AL RESUMIR] {str(e)}"


@router.post("/mcp/invoke", response_model=OutputMessage)
def mcp_invoke(input_message: InputMessage, x_api_key: str = Header(default=None)):
    expected_key = os.getenv("API_KEY")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    task = input_message.task
    data = input_message.input

    if task == "summarize":
        text = data.get("text", "")
        summary = generate_summary_with_openai(text)

        user_id = input_message.context.user_id or "desconocido"
        guardar_resumen(user_id, text, summary)

        return OutputMessage(
            success=True,
            result={
                "summary": summary,
                "input": input_message.input,
                "context": input_message.context,
            },
            error=None,
        )

    else:
        return OutputMessage(success=False, result=None, error=f"Unknown task: {task}")
