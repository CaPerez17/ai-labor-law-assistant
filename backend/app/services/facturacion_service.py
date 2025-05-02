"""
Servicio de Facturación
-----------------------
Implementa la lógica de negocio para el manejo de facturas.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.factura import Factura
from ..models.usuario import Usuario
from ..schemas.factura import FacturaCreate, FacturaUpdate

class FacturacionService:
    async def crear_factura(
        self,
        db: Session,
        factura_data: FacturaCreate,
        usuario_id: int
    ) -> Factura:
        """
        Crea una nueva factura.
        """
        factura = Factura(
            **factura_data.model_dump(),
            usuario_id=usuario_id,
            fecha_creacion=datetime.utcnow(),
            estado="pendiente"
        )
        db.add(factura)
        db.commit()
        db.refresh(factura)
        return factura

    async def obtener_factura(
        self,
        db: Session,
        factura_id: int
    ) -> Optional[Factura]:
        """
        Obtiene una factura por su ID.
        """
        return db.query(Factura).filter(Factura.id == factura_id).first()

    async def obtener_facturas_usuario(
        self,
        db: Session,
        usuario_id: int
    ) -> List[Factura]:
        """
        Obtiene todas las facturas de un usuario.
        """
        return db.query(Factura).filter(Factura.usuario_id == usuario_id).all()

    async def actualizar_factura(
        self,
        db: Session,
        factura_id: int,
        factura_data: FacturaUpdate
    ) -> Optional[Factura]:
        """
        Actualiza una factura existente.
        """
        factura = await self.obtener_factura(db, factura_id)
        if not factura:
            return None

        for key, value in factura_data.model_dump(exclude_unset=True).items():
            setattr(factura, key, value)

        db.commit()
        db.refresh(factura)
        return factura

    async def marcar_como_pagada(
        self,
        db: Session,
        factura_id: int,
        referencia_pago: str
    ) -> Optional[Factura]:
        """
        Marca una factura como pagada.
        """
        factura = await self.obtener_factura(db, factura_id)
        if not factura:
            return None

        factura.estado = "pagada"
        factura.referencia_pago = referencia_pago
        factura.fecha_pago = datetime.utcnow()

        db.commit()
        db.refresh(factura)
        return factura

    async def obtener_facturas_pendientes(
        self,
        db: Session
    ) -> List[Factura]:
        """
        Obtiene todas las facturas pendientes de pago.
        """
        return db.query(Factura).filter(Factura.estado == "pendiente").all()

    async def obtener_facturas_por_estado(
        self,
        db: Session,
        estado: str
    ) -> List[Factura]:
        """
        Obtiene todas las facturas por estado.
        """
        return db.query(Factura).filter(Factura.estado == estado).all() 