from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Documento(Base):
    __tablename__ = "documentos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    tipo = Column(String(50))
    contenido = Column(Text, nullable=True)
    fecha_subida = Column(DateTime, default=datetime.utcnow)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    estado = Column(String(50), default="pendiente")
    resultado_analisis = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    caso_id = Column(Integer, ForeignKey("casos.id"), nullable=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="documentos")
    caso = relationship("Caso", back_populates="documentos") 