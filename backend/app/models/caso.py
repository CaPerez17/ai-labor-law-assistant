"""
Modelo de Caso para la base de datos
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base

class EstadoCaso(enum.Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    PENDIENTE_VERIFICACION = "pendiente_verificacion"
    VERIFICADO = "verificado"
    RESUELTO = "resuelto"
    CERRADO = "cerrado"

class NivelRiesgo(enum.Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"

class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(Enum(EstadoCaso), default=EstadoCaso.PENDIENTE, nullable=False)
    nivel_riesgo = Column(Enum(NivelRiesgo), default=NivelRiesgo.MEDIO, nullable=False)
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
        return f"<Caso(id={self.id}, titulo='{self.titulo}', estado='{self.estado.value}')>" 