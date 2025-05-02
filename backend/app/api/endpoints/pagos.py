from fastapi import APIRouter, Depends, HTTPException, status, Request, Header, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.usuario import Usuario
from app.services.pago_service import PagoService

router = APIRouter()
pago_service = PagoService()

@router.post("/crear-preferencia/{factura_id}")
async def crear_preferencia_pago(
    factura_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea una preferencia de pago en MercadoPago para una factura específica.
    
    Args:
        factura_id: ID de la factura a pagar
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        dict: Datos de la preferencia de pago de MercadoPago
        
    Raises:
        HTTPException: Si la factura no existe o ya está pagada
    """
    return await pago_service.crear_preferencia_pago(factura_id, db)

@router.post("/mercadopago/webhook")
async def mercadopago_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint para recibir webhooks de MercadoPago.
    
    Args:
        request: Request de FastAPI
        db: Sesión de base de datos
        
    Returns:
        dict: Resultado del procesamiento del webhook
        
    Raises:
        HTTPException: Si hay errores en el procesamiento
    """
    try:
        # MercadoPago puede enviar notificaciones como JSON o como application/x-www-form-urlencoded
        content_type = request.headers.get("Content-Type", "")
        
        if "application/json" in content_type:
            payload = await request.json()
        else:
            form_data = await request.form()
            # Convertir form data a dict
            payload = dict(form_data)
            
        # Procesar el evento
        result = await pago_service.procesar_webhook(payload, db)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar webhook: {str(e)}"
        )

@router.get("/verificar/{external_reference}")
async def verificar_estado_pago(
    external_reference: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verifica el estado de un pago por su referencia externa.
    
    Args:
        external_reference: Referencia externa del pago
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        dict: Estado del pago, monto y fecha de pago
        
    Raises:
        HTTPException: Si la referencia no existe o hay un error
    """
    return await pago_service.verificar_estado_pago(external_reference, db) 