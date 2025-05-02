from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base

class TipoNotificacion(str, enum.Enum):
    ESCALAMIENTO = "escalamiento"
    MENSAJE = "mensaje"
    FACTURA = "factura"
    PAGO = "pago"
    SISTEMA = "sistema"

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo = Column(Enum(TipoNotificacion), nullable=False)
    titulo = Column(String, nullable=False)
    mensaje = Column(String, nullable=False)
    leido = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_lectura = Column(DateTime, nullable=True)
    datos_adicionales = Column(String, nullable=True)  # JSON string para datos adicionales

    # Relaciones
    usuario = relationship("Usuario", back_populates="notificaciones") 