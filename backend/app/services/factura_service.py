"""
Servicio de Facturación
-------------------
Implementa la lógica para la gestión de facturas y pagos.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.factura import Factura, EstadoFactura
from ..schemas.factura import FacturaCreate, FacturaUpdate, PagoInput
from ..models.usuario import Usuario

class FacturaService:
    """Servicio para manejar facturas y pagos"""

    @staticmethod
    def generar_numero_factura() -> str:
        """Genera un número único de factura"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"FACT-{timestamp}"

    @staticmethod
    def crear_factura(db: Session, factura_data: FacturaCreate, usuario_id: int) -> Factura:
        """Crea una nueva factura"""
        # Verificar que el usuario existe
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Crear la factura
        db_factura = Factura(
            usuario_id=usuario_id,
            servicio=factura_data.servicio,
            monto=factura_data.monto,
            descripcion=factura_data.descripcion,
            numero_factura=FacturaService.generar_numero_factura()
        )
        
        db.add(db_factura)
        db.commit()
        db.refresh(db_factura)
        return db_factura

    @staticmethod
    def obtener_facturas_usuario(
        db: Session,
        usuario_id: int,
        estado: Optional[EstadoFactura] = None
    ) -> List[Factura]:
        """Obtiene las facturas de un usuario"""
        query = db.query(Factura).filter(Factura.usuario_id == usuario_id)
        if estado:
            query = query.filter(Factura.estado == estado)
        return query.all()

    @staticmethod
    def obtener_factura(db: Session, factura_id: int) -> Factura:
        """Obtiene una factura específica"""
        factura = db.query(Factura).filter(Factura.id == factura_id).first()
        if not factura:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Factura no encontrada"
            )
        return factura

    @staticmethod
    def procesar_pago(db: Session, pago_data: PagoInput, usuario_id: int) -> Factura:
        """Procesa el pago de una factura"""
        factura = FacturaService.obtener_factura(db, pago_data.factura_id)
        
        # Verificar que la factura pertenece al usuario
        if factura.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para pagar esta factura"
            )
        
        # Verificar que la factura está pendiente
        if factura.estado != EstadoFactura.PENDIENTE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La factura ya ha sido pagada o anulada"
            )
        
        # Simular procesamiento de pago
        try:
            # Aquí iría la integración con la pasarela de pagos
            factura.estado = EstadoFactura.PAGADA
            factura.fecha_pago = datetime.now()
            factura.metodo_pago = pago_data.metodo_pago
            
            db.commit()
            db.refresh(factura)
            return factura
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al procesar el pago"
            )

    @staticmethod
    def obtener_todas_facturas(
        db: Session,
        estado: Optional[EstadoFactura] = None
    ) -> List[Factura]:
        """Obtiene todas las facturas (solo para administradores)"""
        query = db.query(Factura)
        if estado:
            query = query.filter(Factura.estado == estado)
        return query.all() 