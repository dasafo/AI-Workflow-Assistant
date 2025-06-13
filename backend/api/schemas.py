"""
Este módulo define los esquemas de datos para la API.

Incluye modelos para solicitudes y respuestas de estado, procesamiento de texto, consulta de historial y consulta inteligente.

"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Modelos para gestión de estado de usuario
class EstadoUsuarioRequest(BaseModel):
    chat_id: int
    modo: str  # '/resumir', '/traducir', '/clasificar', '/consultar'


# Modelo para respuesta de estado de usuario
class EstadoUsuarioResponse(BaseModel):
    chat_id: int
    modo_actual: Optional[str] = None
    mensaje: str
    success: bool = True


# Modelos para procesamiento de texto
class ProcesarRequest(BaseModel):
    chat_id: int
    texto: str
    tipo_tarea: Optional[str] = None  # Si no se proporciona, se detecta del estado


# Modelo para respuesta de procesamiento de texto
class ProcesarResponse(BaseModel):
    chat_id: int  # Añadido para que Telegram sepa a dónde enviar la respuesta
    resultado: str
    tipo_tarea: str
    success: bool = True
    mensaje: Optional[str] = None


# Modelos para consulta de historial
class ConsultaHistorialRequest(BaseModel):
    chat_id: int
    tipo_tarea: Optional[str] = None  # Si se proporciona, filtra por tipo
    limit: int = 5  # Número máximo de resultados


# Modelo para item de consulta de historial
class ConsultaItem(BaseModel):
    id: int
    tipo_tarea: str
    texto_original: str
    resultado: str
    fecha: datetime


# Modelo para respuesta de consulta de historial
class ConsultaHistorialResponse(BaseModel):
    consultas: List[ConsultaItem]
    total: int
    success: bool = True
    mensaje: Optional[str] = None


# Modelo para solicitud de interpretación de consulta
class InterpretarConsultaRequest(BaseModel):
    texto: str


# Modelo para respuesta de interpretación de consulta
class InterpretarConsultaResponse(BaseModel):
    tipo_tarea: Optional[str] = None
    limit: int = 5
    orden: str = "desc"


# Modelo para solicitud de consulta inteligente
class ConsultaInteligenteRequest(BaseModel):
    chat_id: int
    texto: str
