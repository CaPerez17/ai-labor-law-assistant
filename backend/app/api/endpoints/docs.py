"""
Endpoints para gestión de documentos de casos
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import os
import uuid
from pathlib import Path

from app.db.session import get_db
from app.models.usuario import Usuario
from app.models.documento import Documento
from app.core.security import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Directorio para almacenar archivos subidos
UPLOAD_DIRECTORY = "uploads/documentos"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@router.post("/upload")
async def subir_documento(
    file: UploadFile = File(...),
    caso_id: Optional[int] = Form(None),
    categoria: str = Form(...),
    subcategoria: Optional[str] = Form(None),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Sube un documento asociado a un caso
    """
    try:
        # Verificar que el usuario es abogado
        if current_user.rol.value != "abogado":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo abogados pueden subir documentos"
            )
        
        # Validar archivo
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de archivo requerido"
            )
        
        # Generar nombre único para el archivo
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
        
        # Guardar archivo
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Crear registro en base de datos
        documento = Documento(
            nombre=file.filename,
            ruta_archivo=file_path,
            tipo=file.content_type or "application/octet-stream",
            tamaño=len(content),
            categoria=categoria,
            subcategoria=subcategoria,
            caso_id=caso_id,
            usuario_id=current_user.id
        )
        
        db.add(documento)
        db.commit()
        db.refresh(documento)
        
        logger.info(f"Documento {file.filename} subido por abogado {current_user.email}")
        
        return {
            "id": documento.id,
            "filename": file.filename,
            "size": len(content),
            "message": "Documento subido exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo documento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/caso/{caso_id}")
async def obtener_documentos_caso(
    caso_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los documentos de un caso específico
    """
    try:
        # Verificar que el usuario es abogado
        if current_user.rol.value != "abogado":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado"
            )
        
        # Buscar documentos del caso
        documentos = db.query(Documento).filter(Documento.caso_id == caso_id).all()
        
        return [
            {
                "id": doc.id,
                "nombre": doc.nombre,
                "tipo": doc.tipo,
                "tamaño": doc.tamaño,
                "categoria": doc.categoria,
                "subcategoria": doc.subcategoria,
                "fecha_subida": doc.fecha_creacion
            }
            for doc in documentos
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo documentos del caso {caso_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        ) 