"""
Modelo de Documento Legal
------------------------
Este módulo define el modelo SQLAlchemy para documentos legales
almacenados en la base de datos.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Index
from sqlalchemy.sql import func
import enum

from ..db.database import Base


class DocumentType(str, enum.Enum):
    """Enum para los tipos de documentos legales"""
    SENTENCIA = "sentencia"
    LEY = "ley"
    DECRETO = "decreto"
    RESOLUCION = "resolucion"
    CIRCULAR = "circular"
    CONCEPTO = "concepto"
    OTRO = "otro"


class LegalDocument(Base):
    """
    Modelo para documentos legales en la base de datos.
    Incluye metadatos y el contenido completo del documento.
    """
    __tablename__ = "legal_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    document_type = Column(Enum(DocumentType), nullable=False, index=True)
    reference_number = Column(String(100), nullable=False, index=True)
    issue_date = Column(DateTime, nullable=True, index=True)
    source = Column(String(255), nullable=True)
    
    # Contenido del documento
    content = Column(Text, nullable=False)
    content_vector = Column(Text, nullable=True)  # Para almacenar vectores como JSON
    
    # Campos para categorización y búsqueda
    keywords = Column(Text, nullable=True)  # Palabras clave separadas por comas
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True, index=True)
    
    # Metadatos de sistema
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Índices adicionales para búsqueda eficiente
    __table_args__ = (
        Index('idx_content_fulltext', content, postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<LegalDocument(id={self.id}, title='{self.title}', type='{self.document_type}')>" 