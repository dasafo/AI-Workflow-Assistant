from typing import Dict, Any
from sqlalchemy.sql import text
from services.db import get_db_session
import logging
from core.cache import get_cache_health

logger = logging.getLogger(__name__)


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


async def check_services() -> Dict[str, Any]:
    """Verifica el estado de todos los servicios"""
    db_status = await check_database()
    cache_status = get_cache_health()

    return {
        "status": "healthy"
        if all(s["status"] == "healthy" for s in [db_status, cache_status])
        else "unhealthy",
        "timestamp": "2024-05-06T14:30:00Z",
        "version": "1.0.0",
        "services": {"database": db_status, "cache": cache_status},
    }
