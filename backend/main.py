from fastapi import FastAPI
from pydantic import BaseModel
from api.routes.router import router as mcp_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Personal Workflow Assistant",
    description="API para procesamiento de tareas de IA",
    version="1.0.0",
)

# El endpoint de resumen simple debería moverse al router correspondiente
# y mantener solo la lógica principal aquí

# Incluir el router principal
app.include_router(mcp_router)


# This is a simple FastAPI application that provides an endpoint for summarizing text.
# It uses Pydantic for data validation and serialization.

# The application has two endpoints:
# 1. GET /: A health check endpoint that returns a simple message indicating the service is running.
# 2. POST /summarize: An endpoint that accepts a JSON payload with text to summarize and returns a summary.
# The summary is a simple truncation of the text to the first 100 characters, followed by "..." if the text is longer.


# Define the request model for the summarize endpoint
class SummaryRequest(BaseModel):
    text: str


# Define the response model for the summarize endpoint
@app.get("/")
# Health check endpoint
def read_root():
    return {"message": "AI Personal Workflow Assistant is running"}


# Define the summarize endpoint
@app.post("/summarize")
def summarize(request: SummaryRequest):
    summary = request.text[:100] + "..." if len(request.text) > 100 else request.text
    return {"summary": summary}


# Include the MCP router
# This allows the application to handle requests related to the Model Control Protocol (MCP)
# The MCP router is defined in the mcp.router module and handles requests to the "/mcp/invoke" endpoint.
app.include_router(mcp_router)
