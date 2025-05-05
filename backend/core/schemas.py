from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from enum import Enum


class TaskType(str, Enum):
    """Valid task types for the API"""

    SUMMARIZE = "summarize"
    TRANSLATE = "translate"
    CLASSIFY = "classify"


# This class represents the context of a request.
# It includes optional fields for the source of the request, user ID, and metadata.
# The metadata field can be used to pass additional information as a dictionary.
class Context(BaseModel):
    """
    Context information for API requests

    Attributes:
        source: Origin of the request (e.g., 'api', 'telegram', 'web')
        user_id: Unique identifier for the user
        metadata: Additional context information
    """

    source: Optional[str] = Field(None, description="Source of the request")
    user_id: Optional[str] = Field(None, description="User identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context")


# This class represents the input message structure for the API.
# It includes the task to be performed, the input data, and optional context.
class InputMessage(BaseModel):
    """
    Input message structure for API requests

    Attributes:
        task: Type of task to perform
        input: Input data for the task
        context: Optional context information
    """

    task: TaskType = Field(..., description="Task to perform")
    input: Dict[str, Any] = Field(..., description="Input data for the task")
    context: Optional[Context] = Field(None, description="Context information")

    @validator("input")
    def validate_input(cls, v):
        """Validate input data has required fields"""
        if "text" not in v:
            raise ValueError("Input must contain 'text' field")
        return v


# This class represents the output message structure for the API.
# It indicates whether the operation was successful, and includes result data or an error message.
class OutputMessage(BaseModel):
    """
    Output message structure for API responses

    Attributes:
        success: Whether the operation was successful
        result: Result data if successful
        error: Error message if unsuccessful
    """

    success: bool = Field(..., description="Operation success status")
    result: Optional[Dict[str, Any]] = Field(None, description="Operation result")
    error: Optional[str] = Field(None, description="Error message if failed")

    @validator("result", "error")
    def validate_result_error(cls, v, values):
        """Validate result/error consistency"""
        if values.get("success") and not v and v is not None:
            raise ValueError("Success=True requires non-empty result")
        if not values.get("success") and not v and v is not None:
            raise ValueError("Success=False requires non-empty error")
        return v
