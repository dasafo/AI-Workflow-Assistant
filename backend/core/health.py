from typing import Dict, Any
from sqlalchemy.sql import text
from services.db import get_db_session
import logging
from core.cache import get_cache_health
from datetime import datetime

logger = logging.getLogger(__name__)


# Verifica la conexión a la base de datos
async def check_database() -> Dict[str, Any]:
    """Verifica la conexión a la base de datos"""
    try:
        # Usamos la versión síncrona para health checks por simplicidad
        session = get_db_session()
        result = session.execute(text("SELECT 1"))
        session.close()
        return {"status": "healthy", "details": "Database connection OK"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "details": str(e)}


# Verifica el estado de todos los servicios
async def check_services() -> Dict[str, Any]:
    """Verifica el estado de todos los servicios"""
    db_status = await check_database()
    cache_status = get_cache_health()

    return {
        "status": "healthy"
        if all(s["status"] == "healthy" for s in [db_status, cache_status])
        else "unhealthy",
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "version": "1.0.0",
        "services": {"database": db_status, "cache": cache_status},
    }


# Configura las rutas de health check en la aplicación FastAPI
def setup_health_routes(app):
    """Configura las rutas de health check en la aplicación FastAPI"""
    from fastapi import APIRouter

    health_router = APIRouter(tags=["health"])

    @health_router.get("/health")
    async def health():
        """Endpoint de health check básico"""
        return {"status": "ok"}

    @health_router.get("/health/detailed")
    async def health_detailed():
        """Endpoint de health check detallado"""
        return await check_services()

    app.include_router(health_router)
