"""
Este módulo proporciona funciones para interactuar con la base de datos PostgreSQL.

Incluye funciones para inicializar la base de datos, obtener sesiones de base de datos, guardar consultas, aplicar migraciones y gestionar el estado del usuario.

"""
import os
import logging
from typing import AsyncGenerator, Any, Dict
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, insert, create_engine, update, Index
from sqlalchemy.orm import sessionmaker
import asyncpg
from services.models import (
    ConsultaIA,
    EstadoUsuario,
    Base,
)
from core.logging import setup_logger
from pathlib import Path

# Configure logging
logger = setup_logger("services.db")

# Construye la URL para conexión asíncrona
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Configuración del pool de conexiones desde variables de entorno
POSTGRES_POOL_SIZE = int(os.getenv("POSTGRES_POOL_SIZE", "20"))
POSTGRES_MAX_OVERFLOW = int(os.getenv("POSTGRES_MAX_OVERFLOW", "10"))
POSTGRES_POOL_TIMEOUT = float(os.getenv("POSTGRES_POOL_TIMEOUT", "30"))
POSTGRES_POOL_RECYCLE = int(os.getenv("POSTGRES_POOL_RECYCLE", "1800"))

# URL de conexión a la base de datos
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


# Motor asíncrono con SQLAlchemy 2.0 y configuración optimizada del pool
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_size=POSTGRES_POOL_SIZE,  # Tamaño base del pool
    max_overflow=POSTGRES_MAX_OVERFLOW,  # Conexiones adicionales permitidas
    pool_timeout=POSTGRES_POOL_TIMEOUT,  # Tiempo de espera para obtener conexión
    pool_recycle=POSTGRES_POOL_RECYCLE,  # Reciclar conexiones cada 30 min
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_use_lifo=True,  # Estrategia LIFO para mejor reutilización
)


# Creador de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


# Inicialización asíncrona de tablas
async def init_db():
    """Inicializa la base de datos de forma asíncrona"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Crear índice único para evitar duplicados exactos en consultas_ia
        await conn.run_sync(
            lambda schema: Index(
                "idx_consultas_ia_unique",
                ConsultaIA.chat_id,
                ConsultaIA.tipo_tarea,
                ConsultaIA.texto_original,
                ConsultaIA.resultado,
                unique=True,
            ).create(schema)
        )

    logger.info("Base de datos inicializada")


# Proporciona una sesión de base de datos asíncrona
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Proporciona una sesión de base de datos asíncrona

    Yields:
        AsyncSession: Sesión asíncrona de SQLAlchemy
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


# Para compatibilidad con health checks síncronos
def get_db_session():
    """
    Para compatibilidad con funciones síncronas (como health checks)
    """
    # Creamos una sesión síncrona para este propósito específico
    sync_engine = create_engine(
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT', 5432)}/{os.getenv('POSTGRES_DB')}"
    )
    SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)
    return SessionLocal()


# Función unificada para guardar consultas IA
async def guardar_consulta(
    user_id: str,
    tipo_tarea: str,
    texto_original: str,
    resultado: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Guarda una consulta en la tabla unificada de forma asíncrona

    Args:
        user_id: Identificador del usuario (puede ser string o int)
        tipo_tarea: Tipo de tarea ('resumir', 'clasificar', 'traducir', etc.)
        texto_original: Texto original procesado
        resultado: Resultado de la operación
        metadata: Metadatos adicionales (idioma, confianza, etc.)
    """
    try:
        # Convertir user_id a integer si es posible para compatibilidad con chat_id
        chat_id = int(user_id) if user_id.isdigit() else 0

        # Extraer metadatos específicos
        metadata = metadata or {}
        idioma = metadata.get("idioma")

        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Crear la nueva consulta
                nueva_consulta = ConsultaIA(
                    chat_id=chat_id,
                    tipo_tarea=tipo_tarea,
                    texto_original=texto_original,
                    resultado=resultado,
                    idioma=idioma,
                    fecha=datetime.utcnow(),
                )
                session.add(nueva_consulta)

            logger.info(f"Consulta guardada para usuario {user_id}, tipo: {tipo_tarea}")
            return nueva_consulta.id

    except Exception as e:
        logger.error(f"Error al guardar consulta: {str(e)}")
        raise


# Funciones de compatibilidad simplificadas
async def guardar_resumen(user_id: str, texto_original: str, resumen: str) -> None:
    """
    Función de compatibilidad que redirecciona a guardar_consulta
    """
    logger.warning("Función guardar_resumen está obsoleta. Usar guardar_consulta.")
    await guardar_consulta(user_id, "resumir", texto_original, resumen)

# Función de compatibilidad que redirecciona a guardar_consulta
# Guarda una traducción en la tabla unificada de forma asíncrona
async def guardar_traduccion(
    user_id: str,
    texto_original: str,
    traduccion: str,
    idioma_origen: str = "",
    idioma_destino: str = "en",
) -> None:
    """
    Función de compatibilidad que redirecciona a guardar_consulta
    """
    logger.warning("Función guardar_traduccion está obsoleta. Usar guardar_consulta.")
    await guardar_consulta(
        user_id,
        "traducir",
        texto_original,
        traduccion,
        metadata={"idioma": idioma_destino, "idioma_origen": idioma_origen},
    )

# Función de compatibilidad que redirecciona a guardar_consulta
# Guarda una clasificación en la tabla unificada de forma asíncrona
async def guardar_clasificacion(
    user_id: str,
    texto: str,
    clasificacion: str,
    confianza: float = 0.0,
    resultado_completo: str = "",
) -> None:
    """
    Función de compatibilidad que redirecciona a guardar_consulta
    """
    logger.warning(
        "Función guardar_clasificacion está obsoleta. Usar guardar_consulta."
    )
    resultado = resultado_completo if resultado_completo else clasificacion
    await guardar_consulta(
        user_id, "clasificar", texto, resultado, metadata={"confianza": confianza}
    )


# Aplica scripts de migración para optimizar la base de datos
async def apply_migrations(db_session):
    """Aplica scripts de migración para optimizar la base de datos"""
    try:
        migration_dir = Path("backend/migrations")
        if migration_dir.exists():
            for script_file in sorted(migration_dir.glob("*.sql")):
                with open(script_file, "r") as f:
                    sql_script = f.read()

                # Reemplazar variables
                sql_script = sql_script.replace(
                    "${POSTGRES_DB}", os.getenv("POSTGRES_DB")
                )

                # Ejecutar script
                await db_session.execute(sql_script)
                logger.info(f"Aplicada migración: {script_file.name}")

            await db_session.commit()
            logger.info("Todas las migraciones aplicadas con éxito")
    except Exception as e:
        logger.error(f"Error aplicando migraciones: {e}")
        await db_session.rollback()
        raise


# Para iniciar la BD en el arranque de la aplicación
async def startup_db_init():
    """Inicializa la base de datos al iniciar la aplicación"""
    await init_db()
    async with AsyncSessionLocal() as session:
        await apply_migrations(session)
    logger.info("Inicialización de base de datos y migraciones completadas")


# Obtiene el modo actual del usuario
async def obtener_modo_usuario(chat_id: int) -> Optional[str]:
    """
    Obtiene el modo actual del usuario

    Args:
        chat_id: ID del chat/usuario

    Returns:
        Modo actual o None si no existe
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(EstadoUsuario.modo_actual).where(
                    EstadoUsuario.chat_id == chat_id
                )
            )
            modo = result.scalar_one_or_none()
            return modo
    except Exception as e:
        logger.error(f"Error al obtener estado de usuario: {str(e)}")
        return None


async def establecer_modo_usuario(chat_id: int, modo: str) -> None:
    """
    Establece o actualiza el modo actual del usuario

    Args:
        chat_id: ID del chat/usuario
        modo: Nuevo modo a establecer
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Buscar si ya existe un registro para este usuario
                result = await session.execute(
                    select(EstadoUsuario).where(EstadoUsuario.chat_id == chat_id)
                )
                estado = result.scalar_one_or_none()

                if estado:
                    # Actualizar registro existente
                    await session.execute(
                        update(EstadoUsuario)
                        .where(EstadoUsuario.chat_id == chat_id)
                        .values(modo_actual=modo, fecha=datetime.utcnow())
                    )
                else:
                    # Crear nuevo registro
                    nuevo_estado = EstadoUsuario(
                        chat_id=chat_id, modo_actual=modo, fecha=datetime.utcnow()
                    )
                    session.add(nuevo_estado)

            logger.info(f"Modo {modo} establecido para usuario {chat_id}")
    except Exception as e:
        logger.error(f"Error al establecer modo de usuario: {str(e)}")
        raise


# Limpia (establece a NULL) el modo actual del usuario
async def limpiar_modo_usuario(chat_id: int) -> None:
    """
    Limpia (establece a NULL) el modo actual del usuario

    Args:
        chat_id: ID del chat/usuario
    """
    try:
        await establecer_modo_usuario(chat_id, None)
        logger.info(f"Modo limpiado para usuario {chat_id}")
    except Exception as e:
        logger.error(f"Error al limpiar modo de usuario: {str(e)}")
        raise
