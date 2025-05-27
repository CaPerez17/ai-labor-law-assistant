from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    remitente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    receptor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    caso_id = Column(Integer, ForeignKey("casos.id"), nullable=True)  # Permitir NULL para mensajes generales
    contenido = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    leido = Column(Boolean, default=False, nullable=False)

    # Relaciones
    remitente = relationship("Usuario", foreign_keys=[remitente_id], back_populates="mensajes_enviados")
    receptor = relationship("Usuario", foreign_keys=[receptor_id], back_populates="mensajes_recibidos")
    caso = relationship("Caso", back_populates="mensajes") 