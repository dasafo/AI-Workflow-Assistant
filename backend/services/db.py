import os
import logging
import psycopg2
from psycopg2.extras import DictCursor
from contextlib import contextmanager
from datetime import datetime
from typing import Optional  # Importa explícitamente los modelos necesarios
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importamos los modelos de las tablas antes de ejecutar

# Construye la URL con las variables de entorno que ya usas arriba
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT', 5432)}/{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# SessionLocal se reutiliza donde quieras (incluido FastAPI)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db_session() -> Session:
    """
    Devuelve una sesión SQLAlchemy y la cierra automáticamente.
    health.py la usa para lanzar «SELECT 1».
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Ensures proper handling of connections and automatic closing
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT", 5432),
        )
        yield conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")


def guardar_resumen(user_id: str, texto_original: str, resumen: str) -> None:
    """
    Save summary to database
    Args:
        user_id: User identifier
        texto_original: Original text
        resumen: Generated summary
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO resumenes (user_id, texto_original, resumen, fecha)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, texto_original, resumen, datetime.utcnow()),
                )
                conn.commit()
                logger.info(f"Resumen guardado para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error al guardar resumen: {str(e)}")
        raise


def guardar_traduccion(
    user_id: str, texto_original: str, traduccion: str, idioma: str = "en"
) -> None:
    """
    Save translation to database
    Args:
        user_id: User identifier
        texto_original: Original text
        traduccion: Translated text
        idioma: Target language code
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO traducciones (user_id, texto_original, traduccion, idioma, fecha)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (user_id, texto_original, traduccion, idioma, datetime.utcnow()),
                )
                conn.commit()
                logger.info(f"Traducción guardada para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error al guardar traducción: {str(e)}")
        raise


def guardar_clasificacion(user_id: str, texto_original: str, etiqueta: str) -> None:
    """
    Save classification to database
    Args:
        user_id: User identifier
        texto_original: Original text
        etiqueta: Classification label
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO clasificaciones (user_id, texto_original, etiqueta, fecha)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, texto_original, etiqueta, datetime.utcnow()),
                )
                conn.commit()
                logger.info(f"Clasificación guardada para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error al guardar clasificación: {str(e)}")
        raise
