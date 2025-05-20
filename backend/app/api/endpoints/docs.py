from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
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
        
        # Crear registro en BD
        documento = Documento(
            nombre_archivo=file.filename,
            ruta=str(file_path),
            fecha=fecha,
            numero_ley=numero_ley,
            categoria=categoria,
            subcategoria=subcategoria,
            usuario_id=usuario.id
        )
        db.add(documento)
        db.commit()
        db.refresh(documento)
        
        # Procesar documento en segundo plano
        try:
            texto_procesado = procesar_documento(str(file_path))
            # TODO: Guardar texto_procesado en BD
        except Exception as e:
            print(f"Error procesando documento {file.filename}: {str(e)}")
        
        return {
            "id": documento.id,
            "filename": documento.nombre_archivo,
            "message": "Documento subido exitosamente"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir el documento: {str(e)}"
        )
    finally:
        file.file.close() 