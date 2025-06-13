"""
Este módulo define el router principal de la API.

Incluye el router de endpoints profesionales y configura las rutas de la API.

"""
from fastapi import APIRouter
from core.logging import setup_logger
from api.workflow_endpoints import router as workflow_router

logger = setup_logger("api.router")

# Rename to api_router to match what's imported in main.py
api_router = APIRouter()

# Incluir el router de endpoints profesionales
api_router.include_router(workflow_router)
