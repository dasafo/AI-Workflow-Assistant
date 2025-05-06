from fastapi import APIRouter, Header, HTTPException
from core.schemas import InputMessage, OutputMessage
from core.logging import setup_logger
from services.tasks import summarize, translate, classify
import os

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

    if x_api_key != os.getenv("API_KEY"):
        logger.warning("Unauthorized access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/mcp/invoke", response_model=OutputMessage)
async def mcp_invoke(
    input_message: InputMessage, x_api_key: str = Header(default=None)
):
    """
    Unified endpoint for all AI tasks
    """
    validate_api_key(x_api_key)

    task = input_message.task
    handler = TASKS.get(task)

    if not handler:
        logger.error(f"Unknown task requested: {task}")
        return OutputMessage(success=False, result=None, error=f"Unknown task: {task}")

    try:
        logger.info(f"Processing task: {task}")
        result = handler(
            input_message.input,
            input_message.context.dict() if input_message.context else {},
        )
        return OutputMessage(success=True, result=result, error=None)
    except Exception as e:
        logger.error(f"Error processing task {task}: {str(e)}")
        return OutputMessage(success=False, result=None, error=str(e))
