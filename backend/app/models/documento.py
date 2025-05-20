from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Documento(Base):
    __tablename__ = "documentos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=True)  # Cambio de nombre_archivo a nombre
    tipo = Column(String, nullable=True)  # Añadido
    contenido = Column(Text, nullable=True)  # Añadido
    fecha_subida = Column(DateTime, nullable=True)  # En lugar de fecha
    fecha_creacion = Column(DateTime, nullable=True)  # Añadido
    fecha_actualizacion = Column(DateTime, nullable=True)  # Añadido
    resultado_analisis = Column(Text, nullable=True)  # Añadido
    estado = Column(String, nullable=True)  # Añadido
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    caso_id = Column(Integer, ForeignKey("casos.id"), nullable=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="documentos")
    caso = relationship("Caso", back_populates="documentos") 