import os
import logging
from typing import AsyncGenerator
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, insert, create_engine
from sqlalchemy.orm import sessionmaker
import asyncpg
from services.models import Clasificacion, Resumen, Traduccion, Base
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
)  # Motor asíncrono con SQLAlchemy 2.0


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
    logger.info("Base de datos inicializada")


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


async def guardar_resumen(user_id: str, texto_original: str, resumen: str) -> None:
    """
    Guarda un resumen en la base de datos de forma asíncrona

    Args:
        user_id: Identificador del usuario
        texto_original: Texto original
        resumen: Resumen generado
    """
    try:
        async with AsyncSessionLocal() as session:
            nuevo_resumen = Resumen(
                user_id=user_id,
                texto_original=texto_original,
                resumen=resumen,
                fecha=datetime.utcnow(),
            )
            session.add(nuevo_resumen)
            await session.commit()
            logger.info(f"Resumen guardado para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error al guardar resumen: {str(e)}")
        raise


async def guardar_traduccion(
    user_id: str, texto_original: str, idioma: str, traduccion: str
) -> None:
    """
    Guarda una traducción en la base de datos de forma asíncrona

    Args:
        user_id: Identificador del usuario
        texto_original: Texto original
        idioma: Código del idioma destino
        traduccion: Texto traducido
    """
    try:
        async with AsyncSessionLocal() as session:
            nueva_traduccion = Traduccion(
                user_id=user_id,
                texto_original=texto_original,
                traduccion=traduccion,
                idioma=idioma,
                fecha=datetime.utcnow(),
            )
            session.add(nueva_traduccion)
            await session.commit()
            logger.info(f"Traducción guardada para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error al guardar traducción: {str(e)}")
        raise


async def guardar_clasificacion(user_id: str, texto: str, clasificacion: str) -> None:
    """
    Guarda una clasificación en la base de datos de forma asíncrona

    Args:
        user_id: Identificador del usuario
        texto: Texto original
        clasificacion: Resultado de la clasificación
    """
    try:
        async with AsyncSessionLocal() as session:
            nueva_clasificacion = Clasificacion(
                user_id=user_id, texto=texto, clasificacion=clasificacion
            )
            session.add(nueva_clasificacion)
            await session.commit()
            logger.info(f"Clasificación guardada para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error al guardar clasificación: {str(e)}")
        raise


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
