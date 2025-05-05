from fastapi import FastAPI
from api.routes.router import router  # Cambia la importación
import logging
from services.database import Base, engine
from services import models  # importa para registrar Resumen, etc.

Base.metadata.create_all(bind=engine)  # crea las tablas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Workflow Assistant",
    description="API para procesar tareas de IA",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health_check():
    """Endpoint para verificar la salud del servicio"""
    return {
        "status": "healthy",
        "service": "AI Workflow Assistant",
        "version": "1.0.0",
    }


# Include API routes
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
