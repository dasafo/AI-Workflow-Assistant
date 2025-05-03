from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class Context(BaseModel):
    # Optional source of the request (e.g., API, UI, etc.)
    source: Optional[str] = None
    # Optional user identifier
    user_id: Optional[str] = None
    # Optional metadata dictionary for additional context
    # This can include any key-value pairs relevant to the request
    metadata: Optional[Dict[str, Any]] = None


class InputMessage(BaseModel):
    # Task name or identifier to be performed
    task: str
    # Input data required for the task
    input: Dict[str, Any]
    # Optional context information
    context: Optional[Context] = None


class OutputMessage(BaseModel):
    # Indicates if the operation was successful
    success: bool
    # Result data if the operation succeeded
    result: Optional[Dict[str, Any]] = None
    # Error message if the operation failed
    error: Optional[str] = None


class RawTelegramMessage(BaseModel):
    message: dict  # mensaje entero que llega desde Telegram
