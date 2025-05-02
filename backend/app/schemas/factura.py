"""
Schemas de Facturación
------------------
Define los modelos Pydantic para la facturación.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.models.factura import EstadoFactura

class FacturaBase(BaseModel):
    """Modelo base para facturas"""
    servicio: str = Field(..., min_length=3, max_length=255)
    monto: float = Field(..., gt=0)
    descripcion: Optional[str] = Field(None, max_length=500)

    @validator('monto')
    def validar_monto(cls, v):
        """Valida que el monto sea positivo y tenga máximo 2 decimales"""
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        if round(v, 2) != v:
            raise ValueError('El monto debe tener máximo 2 decimales')
        return v

class FacturaCreate(FacturaBase):
    """Modelo para crear una factura"""
    pass

class FacturaUpdate(BaseModel):
    """Modelo para actualizar una factura"""
    estado: EstadoFactura
    metodo_pago: Optional[str] = Field(None, max_length=50)

class FacturaResponse(FacturaBase):
    """Modelo para respuesta de factura"""
    id: int
    usuario_id: int
    estado: EstadoFactura
    fecha_emision: datetime
    fecha_pago: Optional[datetime] = None
    numero_factura: str
    metodo_pago: Optional[str] = None

    class Config:
        orm_mode = True

class PagoInput(BaseModel):
    """Modelo para procesar un pago"""
    factura_id: int
    metodo_pago: str = Field(..., max_length=50) 