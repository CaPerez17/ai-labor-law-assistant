"""
Endpoints de Facturación
--------------------
Implementa los endpoints para la gestión de facturas y pagos.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.factura import (
    FacturaCreate,
    FacturaResponse,
    PagoInput
)
from app.services.factura_service import FacturaService
from app.services.auth_service import AuthService
from app.models.factura import EstadoFactura
from app.db.session import get_db

router = APIRouter()

@router.post("/crear", response_model=FacturaResponse)
async def crear_factura(
    factura_data: FacturaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(AuthService.get_current_active_user)
):
    """
    Crea una nueva factura para el usuario actual.
    
    Args:
        factura_data: Datos de la factura a crear
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
    Returns:
        FacturaResponse: Factura creada
    """
    return FacturaService.crear_factura(db, factura_data, current_user.id)

@router.post("/pagar", response_model=FacturaResponse)
async def pagar_factura(
    pago_data: PagoInput,
    db: Session = Depends(get_db),
    current_user = Depends(AuthService.get_current_active_user)
):
    """
    Procesa el pago de una factura.
    
    Args:
        pago_data: Datos del pago
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
    Returns:
        FacturaResponse: Factura actualizada
    """
    return FacturaService.procesar_pago(db, pago_data, current_user.id)

@router.get("/usuario/{usuario_id}", response_model=List[FacturaResponse])
async def listar_facturas_usuario(
    usuario_id: int,
    estado: Optional[EstadoFactura] = None,
    db: Session = Depends(get_db),
    current_user = Depends(AuthService.get_current_active_user)
):
    """
    Lista las facturas de un usuario específico.
    Solo el usuario dueño o un administrador pueden ver las facturas.
    
    Args:
        usuario_id: ID del usuario
        estado: Estado de las facturas a filtrar
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
    Returns:
        List[FacturaResponse]: Lista de facturas
    """
    # Verificar permisos
    if current_user.rol != "admin" and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver estas facturas"
        )
    
    return FacturaService.obtener_facturas_usuario(db, usuario_id, estado)

@router.get("/todas", response_model=List[FacturaResponse])
async def listar_todas_facturas(
    estado: Optional[EstadoFactura] = None,
    db: Session = Depends(get_db),
    current_user = Depends(AuthService.check_admin_role)
):
    """
    Lista todas las facturas del sistema.
    Solo los administradores pueden acceder a este endpoint.
    
    Args:
        estado: Estado de las facturas a filtrar
        db: Sesión de base de datos
        current_user: Usuario administrador
        
    Returns:
        List[FacturaResponse]: Lista de todas las facturas
    """
    return FacturaService.obtener_todas_facturas(db, estado) 