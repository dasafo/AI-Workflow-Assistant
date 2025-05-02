from fastapi import APIRouter
from .schemas import InputMessage, OutputMessage
from db import guardar_resumen

router = APIRouter()


@router.post("/mcp/invoke", response_model=OutputMessage)
def mcp_invoke(request: InputMessage):
    task = request.task
    data = request.input

    if task == "summarize":
        text = data.get("text", "")
        summary = text[:100] + "..." if len(text) > 100 else text

        # Guardar en PostgreSQL después de tener todo
        user_id = request.context.user_id or "desconocido"
        guardar_resumen(user_id, text, summary)

        return OutputMessage(
            success=True,
            result={
                "summary": summary,
                "input": request.input,
                "context": request.context,
            },
            error=None,
        )
    else:
        return OutputMessage(success=False, error=f"Unknown task: {task}")
