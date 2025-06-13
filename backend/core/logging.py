"""
Este módulo proporciona una configuración de registro (logger) para la aplicación.

Configura un logger con formato consistente para todos los módulos.

"""
import logging
import sys
from typing import Optional


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Configura y retorna un logger con formato consistente
    Args:
        name: Nombre del módulo para el logger
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name or __name__)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
