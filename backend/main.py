from fastapi import FastAPI
from api.routes.router import router
from core.health import check_services
from core.logging import setup_logger

logger = setup_logger("main")

app = FastAPI()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return await check_services()


# Include API routes
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
