"""
Modelo de Feedback de Usuario
-------------------------
Define la estructura de datos para el feedback de los usuarios en la base de datos.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db.base_class import Base

class FeedbackUsuario(Base):
    __tablename__ = "feedback_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    calificacion = Column(Float, nullable=False)
    comentario = Column(String, nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="feedback") 