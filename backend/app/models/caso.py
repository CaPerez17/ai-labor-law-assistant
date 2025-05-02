"""
Modelo de Caso
-------------
Define la estructura de datos para los casos en la base de datos.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base

class EstadoCaso(str, enum.Enum):
    ABIERTO = "abierto"
    EN_PROCESO = "en_proceso"
    CERRADO = "cerrado"

class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    estado = Column(Enum(EstadoCaso), default=EstadoCaso.ABIERTO)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="casos")
    documentos = relationship("Documento", back_populates="caso")

    def __repr__(self):
        return f"<Caso {self.id}: {self.titulo}>" 