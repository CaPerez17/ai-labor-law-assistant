"""
Esquemas de Documentos Legales
----------------------------
Este módulo define los esquemas Pydantic para la validación y serialización
de documentos legales en la API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from ..models.legal_document import DocumentType


class LegalDocumentBase(BaseModel):
    """Esquema base para documentos legales"""
    title: str = Field(..., description="Título del documento legal")
    document_type: DocumentType = Field(..., description="Tipo de documento")
    reference_number: str = Field(..., description="Número de referencia del documento")
    issue_date: Optional[datetime] = Field(None, description="Fecha de emisión")
    source: Optional[str] = Field(None, description="Fuente o entidad emisora")
    content: str = Field(..., description="Contenido completo del documento")
    keywords: Optional[str] = Field(None, description="Palabras clave separadas por comas")
    category: Optional[str] = Field(None, description="Categoría principal del documento")
    subcategory: Optional[str] = Field(None, description="Subcategoría del documento")


class LegalDocumentCreate(LegalDocumentBase):
    """Esquema para crear documentos legales"""
    pass


class LegalDocumentUpdate(BaseModel):
    """Esquema para actualizar documentos legales"""
    title: Optional[str] = None
    document_type: Optional[DocumentType] = None
    reference_number: Optional[str] = None
    issue_date: Optional[datetime] = None
    source: Optional[str] = None
    content: Optional[str] = None
    keywords: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None


class LegalDocumentInDB(LegalDocumentBase):
    """Esquema para documentos legales en la base de datos"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LegalDocumentResponse(LegalDocumentInDB):
    """Esquema para respuestas de documentos legales"""
    pass


class LegalDocumentSearchResult(BaseModel):
    """Esquema para resultados de búsqueda de documentos legales"""
    document: LegalDocumentResponse
    score: float = Field(..., description="Puntuación de relevancia")
    
    class Config:
        orm_mode = True


class SearchQuery(BaseModel):
    """Esquema para consultas de búsqueda"""
    query: str = Field(..., min_length=3, description="Consulta de búsqueda")
    document_type: Optional[DocumentType] = Field(None, description="Filtrar por tipo de documento")
    category: Optional[str] = Field(None, description="Filtrar por categoría")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Número máximo de resultados") 