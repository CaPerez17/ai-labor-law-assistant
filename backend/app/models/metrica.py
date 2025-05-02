"""
Modelo de Métricas de Uso
----------------------
Define la estructura de datos para las métricas de uso en la base de datos.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class MetricaUso(Base):
    __tablename__ = "metricas_uso"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo_accion = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    duracion = Column(Float, nullable=True)  # en segundos
    detalles = Column(String, nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="metricas") 