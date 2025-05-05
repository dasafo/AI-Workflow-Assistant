from fastapi import APIRouter, Header, HTTPException
from core.schemas import InputMessage, OutputMessage
import os
import logging
from services.tasks import summarize, translate, classify
from services.db import guardar_resumen, guardar_traduccion, guardar_clasificacion

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()  # Asegúrate de que esta línea esté presente

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

    if x_api_key != os.getenv("API_KEY"):
        logger.warning("Unauthorized access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/mcp/invoke", response_model=OutputMessage)
async def mcp_invoke(
    input_message: InputMessage, x_api_key: str = Header(default=None)
):
    """
    Execute AI task through API
    """
    validate_api_key(x_api_key)

    task = input_message.task
    handler = TASKS.get(task)

    if not handler:
        logger.error(f"Unknown task requested: {task}")
        return OutputMessage(success=False, result=None, error=f"Unknown task: {task}")

    try:
        logger.info(
            f"Processing task: {task} from source: {input_message.context.source if input_message.context else 'unknown'}"
        )

        # Convert Pydantic model to dict if context exists
        context_dict = input_message.context.dict() if input_message.context else {}
        result = handler(input_message.input, context_dict)

        # Store in database based on task type
        try:
            user_id = context_dict.get("user_id", "unknown")
            text = input_message.input.get("text", "")

            if task == "summarize":
                guardar_resumen(user_id, text, result.get("summary", ""))
            elif task == "translate":
                guardar_traduccion(user_id, text, result.get("translation", ""))
            elif task == "classify":
                guardar_clasificacion(user_id, text, result.get("label", ""))
            logger.info(f"Task {task} result saved to database")
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            # Continue even if database storage fails

        logger.info(f"Task {task} completed successfully")
        return OutputMessage(success=True, result=result, error=None)
    except Exception as e:
        logger.error(f"Error processing task {task}: {str(e)}")
        return OutputMessage(success=False, result=None, error=str(e))
