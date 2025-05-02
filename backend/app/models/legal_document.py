"""
Modelo de Documento Legal
------------------------
Este módulo define el modelo SQLAlchemy para documentos legales
almacenados en la base de datos.
"""

import sys
from pathlib import Path
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, ForeignKey
from sqlalchemy.sql import func
import enum

# Asegurar que backend/ esté en sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar configuración
from config import DATABASE_URL
from app.db.database import Base


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
    document_type = Column(String(50), nullable=False, index=True)  # Usando String para compatibilidad con SQLite
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
    
    # No incluimos índices PostgreSQL-específicos para SQLite
    # __table_args__ condicionado a la base de datos
    if not DATABASE_URL.startswith("sqlite"):
        __table_args__ = (
            Index('idx_content_fulltext', content, postgresql_using='gin'),
        )
    
    def __repr__(self):
        return f"<LegalDocument(id={self.id}, title='{self.title}', type='{self.document_type}')>" 