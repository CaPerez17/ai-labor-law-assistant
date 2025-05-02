from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class FeedbackUsuario(Base):
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    calificacion = Column(Integer)
    comentario = Column(Text)
    
    # Relación con el usuario
    usuario = relationship("Usuario", back_populates="feedback") 