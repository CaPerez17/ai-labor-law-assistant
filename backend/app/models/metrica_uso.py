from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.base_class import Base

class MetricaUso(Base):
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    tipo_accion = Column(String(50))
    fecha = Column(DateTime, default=datetime.utcnow)
    detalles = Column(Text)
    
    # Relación con el usuario
    usuario = relationship("Usuario", back_populates="metricas_uso") 