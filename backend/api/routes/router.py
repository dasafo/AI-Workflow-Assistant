from fastapi import APIRouter, Header, HTTPException, Request
from core.schemas import InputMessage, OutputMessage
from core.logging import setup_logger
from core.errors import InvalidAPIKeyError, InvalidTaskError, handle_exception
from services.tasks import summarize, translate, classify
import os
import traceback

logger = setup_logger("api.router")

router = APIRouter()

TASKS = {
    "summarize": summarize.run,
    "translate": translate.run,
    "classify": classify.run,
}


def validate_api_key(x_api_key: str):
    """Validate API key from environment variables"""
    # Add debug logging for API key validation
    logger.debug(f"Expected API key: {os.getenv('API_KEY')}")
    logger.debug(f"Received API key: {x_api_key}")

    if not x_api_key:
        logger.warning("API key missing")
        raise InvalidAPIKeyError("API Key no proporcionada")

    if x_api_key != os.getenv("API_KEY"):
        logger.warning("Unauthorized access attempt")
        raise InvalidAPIKeyError("API Key incorrecta")


@router.post("/mcp/invoke", response_model=OutputMessage)
async def mcp_invoke(
    request: Request, input_message: InputMessage, x_api_key: str = Header(default=None)
):
    """
    Unified endpoint for all AI tasks
    """
    try:
        # Validar API key
        validate_api_key(x_api_key)

        # Obtener tarea y manejador
        task = input_message.task
        handler = TASKS.get(task)

        if not handler:
            logger.error(f"Unknown task requested: {task}")
            raise InvalidTaskError(task)

        # Logging contextual
        client_ip = request.client.host if request.client else "unknown"
        task_name = str(task)
        logger.info(
            f"Processing task: {task_name} | "
            f"Client: {client_ip} | "
            f"Input length: {len(str(input_message.input))} chars"
        )

        # Ejecutar tarea
        result = await handler(
            input_message.input,
            input_message.context.dict() if input_message.context else {},
        )

        # Log del resultado
        result_size = len(str(result)) if result else 0
        logger.info(
            f"Task {task_name} completed successfully | Result size: {result_size} chars"
        )

        return OutputMessage(success=True, result=result, error=None)

    except InvalidAPIKeyError as e:
        # Los errores de API key ya están formateados
        raise e.to_http_exception()

    except InvalidTaskError as e:
        # Los errores de tarea inválida ya están formateados
        raise e.to_http_exception()

    except Exception as e:
        # Capturar stacktrace para depuración
        stack_trace = traceback.format_exc()
        logger.error(f"Error processing task: {str(e)}\n{stack_trace}")

        # Convertir a nuestro formato de error estándar
        api_error = handle_exception(e)

        # Devolver respuesta de error
        return OutputMessage(
            success=False, result=None, error=f"{api_error.code}: {api_error.message}"
        )
