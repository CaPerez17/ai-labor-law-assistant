"""
Modelo de Caso para la base de datos
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String(30), default="PENDIENTE", nullable=False)
    nivel_riesgo = Column(String(20), default="MEDIO", nullable=False)
    comentarios = Column(Text, nullable=True)
    
    # Relaciones con usuarios
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    abogado_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    fecha_cierre = Column(DateTime, nullable=True)
    
    # Relaciones
    cliente = relationship("Usuario", foreign_keys=[cliente_id], back_populates="casos_como_cliente")
    abogado = relationship("Usuario", foreign_keys=[abogado_id], back_populates="casos_como_abogado")
    documentos = relationship("Documento", back_populates="caso")
    mensajes = relationship("Mensaje", back_populates="caso", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Caso(id={self.id}, titulo='{self.titulo}', estado='{self.estado}')>" 