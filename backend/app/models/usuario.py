"""
Modelo de Usuario
--------------
Define la estructura de datos para los usuarios en la base de datos.
"""

from sqlalchemy import Column, Integer, String, Enum, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from datetime import datetime

class RolUsuario(str, enum.Enum):
    """Roles disponibles en el sistema"""
    ADMIN = "admin"
    ABOGADO = "abogado"
    CLIENTE = "cliente"

class Usuario(Base):
    """Modelo de Usuario"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False, default=RolUsuario.CLIENTE)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    activo = Column(Boolean, default=True)
    recibir_emails = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # Relaciones con casos
    casos_como_cliente = relationship("Caso", foreign_keys="[Caso.cliente_id]", back_populates="cliente")
    casos_como_abogado = relationship("Caso", foreign_keys="[Caso.abogado_id]", back_populates="abogado")
    
    # Otras relaciones
    documentos = relationship("Documento", back_populates="usuario")
    metricas_uso = relationship("MetricaUso", back_populates="usuario")
    feedback = relationship("FeedbackUsuario", back_populates="usuario")
    notificaciones = relationship("Notificacion", back_populates="usuario")
    calificaciones = relationship("Calificacion", back_populates="usuario")
    facturas = relationship("Factura", back_populates="usuario")
    mensajes_enviados = relationship("Mensaje", foreign_keys="[Mensaje.remitente_id]", back_populates="remitente")
    mensajes_recibidos = relationship("Mensaje", foreign_keys="[Mensaje.receptor_id]", back_populates="receptor") 