from fastapi import FastAPI
from pydantic import BaseModel

from mcp.router import router as mcp_router

app = FastAPI()

class SummaryRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"message": "AI Personal Workflow Assistant is running"}

@app.post("/summarize")
def summarize(request: SummaryRequest):
    summary = request.text[:100] + "..." if len(request.text) > 100 else request.text
    return {"summary": summary}


app.include_router(mcp_router)