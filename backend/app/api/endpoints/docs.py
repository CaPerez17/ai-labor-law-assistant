from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
import os
import shutil
from pathlib import Path

from app.api.deps import get_current_user, get_db
from app.models.usuario import Usuario
from app.models.documento import Documento
from app.services.preprocessor import procesar_documento

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload", status_code=201)
async def upload_document(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    fecha: date = Form(...),
    numero_ley: str = Form(...),
    categoria: str = Form(...),
    subcategoria: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Crear directorio para el usuario si no existe
        user_dir = UPLOAD_DIR / str(usuario.id)
        user_dir.mkdir(exist_ok=True)
        
        # Guardar archivo
        file_path = user_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Procesar documento
        try:
            texto_procesado = procesar_documento(str(file_path))
        except Exception as e:
            print(f"Error procesando documento {file.filename}: {str(e)}")
            texto_procesado = None
        
        # Crear registro en BD con estructura actualizada
        now = datetime.now()
        documento = Documento(
            nombre=file.filename,  # nombre en lugar de nombre_archivo
            tipo=f"{categoria}/{subcategoria}",  # Combinamos categoría y subcategoría
            contenido=texto_procesado,  # Guardamos el texto procesado
            fecha_subida=now,
            fecha_creacion=now,
            resultado_analisis=f"Número de ley: {numero_ley}, Fecha: {fecha}",  # Guardamos metadatos como resultado
            estado="procesado",
            usuario_id=usuario.id
        )
        db.add(documento)
        db.commit()
        db.refresh(documento)
        
        return {
            "id": documento.id,
            "filename": documento.nombre,  # nombre en lugar de nombre_archivo
            "message": "Documento subido exitosamente"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir el documento: {str(e)}"
        )
    finally:
        file.file.close() 