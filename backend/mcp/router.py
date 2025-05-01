from fastapi import APIRouter
from .schemas import InputMessage, OutputMessage

router = APIRouter()

@router.post("/mcp/invoke", response_model=OutputMessage)
def mcp_invoke(request: InputMessage):
    # Get the task name from the request
    task = request.task
    # Get the input data from the request
    data = request.input

    if task == "summarize":
        # Extract the text to summarize
        text = data.get("text", "")
        # Create a summary: first 100 characters, add "..." if text is longer
        summary = text[:100] + "..." if len(text) > 100 else text
        # Return a successful response with the summary
        return OutputMessage(success=True, result={"summary": summary})
    else:
        # Return an error response for unknown tasks
        return OutputMessage(success=False, error=f"Unknown task: {task}")
