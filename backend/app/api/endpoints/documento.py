"""
API de Análisis de Documentos
--------------------------
Este módulo implementa los endpoints para analizar documentos legales
y extraer información relevante.
"""

import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.db.database import get_db
from app.schemas.documento import DocumentoResponse, DocumentoCreate, AnalisisResponse
from app.services.documento_service import DocumentoService
from app.services.auth_service import AuthService
from app.models.usuario import Usuario
from app.models.documento import Documento
from app.services.demo_service import DemoService

router = APIRouter()
documento_service = DocumentoService()

@router.post("/upload", response_model=DocumentoResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Sube un documento para análisis legal.
    """
    try:
        # Verificar si estamos en modo demo
        demo_mode = os.environ.get("LEGALASSISTA_DEMO", "").lower() == "true"
        
        # Obtener contenido del archivo
        contenido = await file.read()
        
        # Restaurar el puntero del archivo para futuros usos
        await file.seek(0)
        
        # Crear documento en la base de datos
        documento = await DocumentoService.create_document(
            db=db,
            usuario_id=current_user.id,
            file=file,
            content=contenido.decode('utf-8', errors='replace')
        )
        
        # Iniciar análisis asincrónico (en modo demo o normal)
        if demo_mode:
            print(f"[DEMO MODE] Usando servicio demo para análisis de documento {documento.id}")
            # En modo demo, realizamos un análisis inmediato simulado
            analisis_result = await DemoService.analyze_document(
                content=contenido.decode('utf-8', errors='replace'),
                document_name=file.filename
            )
            
            # Actualizar el documento con el resultado del análisis
            documento.estado = "analizado"
            documento.resultado_analisis = analisis_result
            db.commit()
            
        else:
            # En modo normal, iniciamos el análisis asincrónico real
            await DocumentoService.start_analysis(db, documento.id)
        
        return DocumentoResponse(
            id=documento.id,
            nombre=documento.nombre,
            tipo=documento.tipo,
            fecha_subida=documento.fecha_subida,
            estado=documento.estado,
            usuario_id=documento.usuario_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando el documento: {str(e)}"
        )

@router.get("/{documento_id}", response_model=DocumentoResponse)
async def get_document(
    documento_id: int,
    current_user: Usuario = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un documento por su ID.
    """
    documento = await DocumentoService.get_document(db, documento_id)
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permiso de acceso
    if documento.usuario_id != current_user.id and current_user.rol not in ["admin", "abogado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para acceder a este documento"
        )
    
    return documento

@router.get("/{documento_id}/analisis", response_model=AnalisisResponse)
async def get_document_analysis(
    documento_id: int,
    current_user: Usuario = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el análisis de un documento por su ID.
    """
    documento = await DocumentoService.get_document(db, documento_id)
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permiso de acceso
    if documento.usuario_id != current_user.id and current_user.rol not in ["admin", "abogado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para acceder a este análisis"
        )
    
    if documento.estado != "analizado" or not documento.resultado_analisis:
        # Verificar si estamos en modo demo
        demo_mode = os.environ.get("LEGALASSISTA_DEMO", "").lower() == "true"
        
        if demo_mode:
            # En modo demo, generar un análisis simulado inmediato
            analisis_result = await DemoService.analyze_document(
                content=documento.contenido,
                document_name=documento.nombre
            )
            
            # Actualizar el documento con el resultado del análisis
            documento.estado = "analizado"
            documento.resultado_analisis = analisis_result
            db.commit()
        else:
            # En modo normal
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El documento aún no ha sido analizado"
            )
    
    return AnalisisResponse(
        documento_id=documento.id,
        resultado=documento.resultado_analisis,
        fecha_analisis=documento.fecha_actualizacion
    )

@router.get("/usuario/mis-documentos", response_model=List[DocumentoResponse])
async def get_user_documents(
    current_user: Usuario = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene los documentos del usuario actual.
    """
    documentos = await DocumentoService.get_user_documents(db, current_user.id)
    return documentos 