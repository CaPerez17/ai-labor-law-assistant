from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.base_class import Base

class Documento(Base):
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255))
    tipo = Column(String(50))
    contenido = Column(Text)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    caso_id = Column(Integer, ForeignKey("casos.id"))
    
    # Relación con el caso
    caso = relationship("Caso", back_populates="documentos") 