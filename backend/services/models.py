from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.sql import func

Base = declarative_base()


# Modelo de consulta de IA
class ConsultaIA(Base):
    __tablename__ = "consultas_ia"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    tipo_tarea = Column(
        String(50), nullable=False, index=True
    )  # 'resumir', 'clasificar', etc.
    texto_original = Column(Text, nullable=False)
    resultado = Column(Text)
    idioma = Column(String(20), nullable=True)  # Solo para traducciones
    fecha = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Representación de la consulta
    def __repr__(self):
        return f"<ConsultaIA(chat_id={self.chat_id}, tipo_tarea={self.tipo_tarea})>"


# Modelo de estado de usuario
class EstadoUsuario(Base):
    __tablename__ = "estado_usuario"

    chat_id = Column(BigInteger, primary_key=True)
    modo_actual = Column(String(50), nullable=True)  # '/resumir', '/clasificar', etc.
    fecha = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return (
            f"<EstadoUsuario(chat_id={self.chat_id}, modo_actual={self.modo_actual})>"
        )


# Exporta los modelos
__all__ = [
    "Base",
    "ConsultaIA",
    "EstadoUsuario",
]
