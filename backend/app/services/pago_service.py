import json
import hashlib
import hmac
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import mercadopago
import uuid

from app.models.factura import Factura, EstadoFactura
from app.core.config import settings

class PagoService:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    async def crear_preferencia_pago(self, factura_id: int, db: Session) -> dict:
        """Crea una preferencia de pago en MercadoPago"""
        try:
            # Obtener la factura
            factura = db.query(Factura).filter(Factura.id == factura_id).first()
            if not factura:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Factura no encontrada"
                )

            if factura.estado == EstadoFactura.PAGADA:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La factura ya ha sido pagada"
                )

            # Generar referencia externa única
            external_reference = f"factura_{factura.id}_{uuid.uuid4().hex[:8]}"
            
            # Crear preferencia de pago en MercadoPago
            preference_data = {
                "items": [
                    {
                        "title": f"Factura #{factura.numero_factura} - {factura.servicio}",
                        "description": factura.descripcion or "Servicio legal",
                        "quantity": 1,
                        "currency_id": "COP",
                        "unit_price": float(factura.monto)
                    }
                ],
                "back_urls": {
                    "success": f"{settings.FRONTEND_URL}/facturas/success",
                    "failure": f"{settings.FRONTEND_URL}/facturas/failure",
                    "pending": f"{settings.FRONTEND_URL}/facturas/pending"
                },
                "auto_return": "approved",
                "external_reference": external_reference,
                "notification_url": f"{settings.HOST}:{settings.PORT}{settings.API_V1_STR}/pagos/mercadopago/webhook"
            }
            
            preference_response = self.sdk.preference().create(preference_data)
            
            if preference_response["status"] != 201:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al crear preferencia de pago"
                )
                
            preference = preference_response["response"]
            
            # Actualizar factura con referencia de MercadoPago
            factura.estado = EstadoFactura.PENDIENTE_PAGO
            factura.mercadopago_id = preference["id"]
            factura.mercadopago_external_reference = external_reference
            db.commit()

            return {
                "id": preference["id"],
                "url": preference["init_point"],
                "external_reference": external_reference,
                "public_key": settings.MERCADOPAGO_PUBLIC_KEY
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear preferencia de pago: {str(e)}"
            )

    async def procesar_webhook(self, data: dict, db: Session):
        """Procesa los eventos del webhook de MercadoPago"""
        try:
            payment_data = None
            notification_type = data.get("type")
            
            # Obtener información del pago según el tipo de notificación
            if notification_type == "payment":
                payment_id = data.get("data", {}).get("id")
                if payment_id:
                    payment_info = self.sdk.payment().get(payment_id)
                    if payment_info["status"] == 200:
                        payment_data = payment_info["response"]
            
            if not payment_data:
                return {"status": "ignored"}
            
            # Buscar la factura por referencia externa
            external_reference = payment_data.get("external_reference")
            if not external_reference or not external_reference.startswith("factura_"):
                return {"status": "invalid_reference"}
            
            factura_id = external_reference.split("_")[1]
            factura = db.query(Factura).filter(Factura.id == factura_id).first()
            
            if not factura:
                return {"status": "factura_not_found"}
            
            # Actualizar el estado de la factura según el estado del pago
            status = payment_data.get("status")
            
            factura.mercadopago_status = status
            factura.mercadopago_payment_id = str(payment_data.get("id"))
            
            if status == "approved":
                factura.estado = EstadoFactura.PAGADA
                factura.fecha_pago = datetime.utcnow()
                factura.metodo_pago = "mercadopago"
            elif status == "rejected":
                factura.estado = EstadoFactura.RECHAZADA
            elif status in ["in_process", "pending"]:
                factura.estado = EstadoFactura.PENDIENTE_PAGO
            
            db.commit()
            
            return {"status": "success", "factura_id": factura.id, "payment_status": status}

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al procesar webhook: {str(e)}"
            )

    async def verificar_estado_pago(self, external_reference: str, db: Session) -> dict:
        """Verifica el estado de un pago por referencia externa"""
        try:
            # Buscar la factura por referencia externa
            factura = db.query(Factura).filter(
                Factura.mercadopago_external_reference == external_reference
            ).first()
            
            if not factura:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Factura no encontrada"
                )
            
            # Si hay un ID de pago en MercadoPago, consultar el estado
            if factura.mercadopago_payment_id:
                payment_info = self.sdk.payment().get(factura.mercadopago_payment_id)
                
                if payment_info["status"] == 200:
                    payment_data = payment_info["response"]
                    factura.mercadopago_status = payment_data["status"]
                    
                    # Actualizar el estado de la factura si es necesario
                    if payment_data["status"] == "approved" and factura.estado != EstadoFactura.PAGADA:
                        factura.estado = EstadoFactura.PAGADA
                        factura.fecha_pago = datetime.utcnow()
                    
                    db.commit()
            
            return {
                "estado": factura.estado,
                "monto": factura.monto,
                "fecha_pago": factura.fecha_pago.isoformat() if factura.fecha_pago else None,
                "mercadopago_status": factura.mercadopago_status
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al verificar estado de pago: {str(e)}"
            ) 