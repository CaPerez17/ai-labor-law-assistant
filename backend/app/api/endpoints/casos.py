"""
Endpoints para la gestión de casos
---------------------------------
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_current_active_user
from app.models.usuario import Usuario
from app.schemas.caso import CasoCreate, CasoUpdate, CasoResponse
from app.services.caso_service import CasoService
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=CasoResponse)
def create_caso(
    caso: CasoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return CasoService(db).create_caso(caso, current_user)

@router.get("/", response_model=List[CasoResponse])
def get_casos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return CasoService(db).get_casos(current_user, skip, limit)

@router.get("/{caso_id}", response_model=CasoResponse)
def get_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    caso = CasoService(db).get_caso(caso_id, current_user)
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return caso

@router.put("/{caso_id}", response_model=CasoResponse)
def update_caso(
    caso_id: int,
    caso: CasoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    updated_caso = CasoService(db).update_caso(caso_id, caso, current_user)
    if not updated_caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return updated_caso

@router.delete("/{caso_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    if not CasoService(db).delete_caso(caso_id, current_user):
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return None 