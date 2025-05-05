from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from services.database import Base  # o from db import Base, si estás en el mismo nivel


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
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    texto = Column(Text, nullable=False)
    etiqueta = Column(String, nullable=False)
    fecha = Column(DateTime, default=func.now())
