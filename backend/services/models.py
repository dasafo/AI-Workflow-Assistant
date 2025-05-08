from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

Base = declarative_base()


class Resumen(Base):
    __tablename__ = "resumenes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    texto_original = Column(Text, nullable=False)
    resumen = Column(Text, nullable=False)
    fecha = Column(DateTime, default=func.now())


class Traduccion(Base):
    __tablename__ = "traducciones"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    texto_original = Column(Text, nullable=False)
    traduccion = Column(Text, nullable=False)
    idioma = Column(String, default="en")
    fecha = Column(DateTime, default=func.now())


class Clasificacion(Base):
    __tablename__ = "clasificaciones"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    texto = Column(Text, nullable=False)
    clasificacion = Column(
        String(100), nullable=False
    )  # Changed from 'tipo' to 'clasificacion'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Clasificacion(user_id={self.user_id}, clasificacion={self.clasificacion})>"


__all__ = ["Base", "Resumen", "Traduccion", "Clasificacion"]
