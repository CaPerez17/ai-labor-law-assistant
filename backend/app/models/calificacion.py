"""
Modelo de Calificación
--------------------
Define la estructura de datos para las calificaciones en el sistema.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Calificacion(Base):
    """
    Modelo para representar una calificación.
    """
    __tablename__ = "calificaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    puntuacion = Column(Float, nullable=False)
    comentario = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="calificaciones")
    
    # Campos adicionales
    tipo = Column(String(50), nullable=False)  # servicio, abogado, app
    referencia_id = Column(Integer, nullable=True)  # ID del objeto calificado (caso, abogado, etc.)
    
    def __repr__(self):
        return f"<Calificacion {self.id}: {self.puntuacion}>" 