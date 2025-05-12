from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class MetricaUso(Base):
    __tablename__ = "metricas_uso"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo_accion = Column(String(50), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    detalles = Column(Text, nullable=True)
    
    # Relación con el usuario
    usuario = relationship("Usuario", back_populates="metricas_uso") 