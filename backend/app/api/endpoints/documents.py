"""
API de Documentos Legales
----------------------
Este módulo define las rutas API para gestionar documentos legales en la base de datos.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.legal_document import LegalDocument, DocumentType
from app.schemas.legal_document import (
    LegalDocumentCreate, 
    LegalDocumentUpdate, 
    LegalDocumentResponse,
    LegalDocumentSearchResult,
    SearchQuery
)
from app.services.search_service import SearchService

router = APIRouter()
search_service = SearchService()


@router.post("/", response_model=LegalDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(document: LegalDocumentCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo documento legal en la base de datos.
    
    Args:
        document: Datos del documento a crear
        db: Sesión de base de datos
    
    Returns:
        El documento creado
    """
    db_document = LegalDocument(
        title=document.title,
        document_type=document.document_type,
        reference_number=document.reference_number,
        issue_date=document.issue_date,
        source=document.source,
        content=document.content,
        keywords=document.keywords,
        category=document.category,
        subcategory=document.subcategory
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document


@router.get("/", response_model=List[LegalDocumentResponse])
def get_documents(
    skip: int = 0, 
    limit: int = 100, 
    document_type: Optional[DocumentType] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista de documentos legales con filtros opcionales.
    
    Args:
        skip: Número de registros a omitir (paginación)
        limit: Número máximo de registros a devolver
        document_type: Filtrar por tipo de documento
        category: Filtrar por categoría
        db: Sesión de base de datos
    
    Returns:
        Lista de documentos legales
    """
    query = db.query(LegalDocument)
    
    if document_type:
        query = query.filter(LegalDocument.document_type == document_type)
    if category:
        query = query.filter(LegalDocument.category == category)
        
    documents = query.offset(skip).limit(limit).all()
    
    return documents


@router.get("/{document_id}", response_model=LegalDocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un documento legal por su ID.
    
    Args:
        document_id: ID del documento
        db: Sesión de base de datos
    
    Returns:
        El documento legal solicitado
    
    Raises:
        HTTPException: Si el documento no existe
    """
    document = db.query(LegalDocument).filter(LegalDocument.id == document_id).first()
    
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
        
    return document


@router.put("/{document_id}", response_model=LegalDocumentResponse)
def update_document(
    document_id: int, 
    document: LegalDocumentUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualiza un documento legal existente.
    
    Args:
        document_id: ID del documento a actualizar
        document: Datos actualizados del documento
        db: Sesión de base de datos
    
    Returns:
        El documento actualizado
    
    Raises:
        HTTPException: Si el documento no existe
    """
    db_document = db.query(LegalDocument).filter(LegalDocument.id == document_id).first()
    
    if db_document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Actualizar solo los campos proporcionados
    for key, value in document.dict(exclude_unset=True).items():
        setattr(db_document, key, value)
    
    db.commit()
    db.refresh(db_document)
    
    return db_document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    Elimina un documento legal por su ID.
    
    Args:
        document_id: ID del documento a eliminar
        db: Sesión de base de datos
    
    Raises:
        HTTPException: Si el documento no existe
    """
    db_document = db.query(LegalDocument).filter(LegalDocument.id == document_id).first()
    
    if db_document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
        
    db.delete(db_document)
    db.commit()
    
    return None


@router.post("/search", response_model=List[LegalDocumentSearchResult])
def search_documents(search_query: SearchQuery, db: Session = Depends(get_db)):
    """
    Busca documentos legales utilizando BM25.
    
    Args:
        search_query: Parámetros de búsqueda
        db: Sesión de base de datos
    
    Returns:
        Lista de documentos relevantes con puntuación
    """
    results = search_service.search_documents(db, search_query)
    return results 