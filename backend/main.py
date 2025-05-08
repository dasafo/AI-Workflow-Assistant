from fastapi import FastAPI
from api.routes.router import router
from core.health import check_services
from core.logging import setup_logger
from services.db import startup_db_init

logger = setup_logger("main")

app = FastAPI()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return await check_services()


# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    """Inicialización de servicios en el arranque"""
    logger.info("Iniciando aplicación...")
    await startup_db_init()
    logger.info("Aplicación iniciada correctamente")


# Include API routes
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
