from fastapi import APIRouter, Header, HTTPException, Request
from core.schemas import InputMessage, OutputMessage, RawTelegramMessage
from services.db import guardar_resumen
import os
from services.tasks import summarize, translate, classify

# ...existing code...

router = APIRouter()

# Mapa de tareas
TASKS = {
    "summarize": summarize.run,
    "translate": translate.run,
    "classify": classify.run,
}


@router.post("/mcp/invoke", response_model=OutputMessage)
def mcp_invoke(input_message: InputMessage, x_api_key: str = Header(default=None)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    task = input_message.task
    handler = TASKS.get(task)

    if not handler:
        return OutputMessage(success=False, result=None, error=f"Unknown task: {task}")

    try:
        result = handler(input_message.input, input_message.context)
        return OutputMessage(success=True, result=result, error=None)
    except Exception as e:
        return OutputMessage(success=False, result=None, error=str(e))


@router.post("/mcp/telegram", response_model=OutputMessage)
def mcp_telegram(raw_msg: RawTelegramMessage, x_api_key: str = Header(default=None)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Extraer texto y chat ID
        msg_text = raw_msg.message.get("text", "")
        user_id = str(raw_msg.message.get("chat", {}).get("id", "unknown"))

        if not msg_text.startswith("/"):
            return OutputMessage(
                success=False, result=None, error="Invalid command format"
            )

        # Parsear comando y argumentos
        parts = msg_text.strip().split(" ")
        task = parts[0][1:].lower()  # sin "/"
        text = " ".join(parts[1:])

        handler = TASKS.get(task)
        if not handler:
            return OutputMessage(
                success=False, result=None, error=f"Unknown task: {task}"
            )

        # Ejecutar tarea
        result = handler({"text": text}, {"user_id": user_id})

        # Guardar resumen si aplica
        if task == "summarize":
            from db import guardar_resumen

            guardar_resumen(user_id, text, result.get("summary", ""))

        return OutputMessage(success=True, result=result, error=None)

    except Exception as e:
        return OutputMessage(success=False, result=None, error=f"[EXCEPTION] {str(e)}")
