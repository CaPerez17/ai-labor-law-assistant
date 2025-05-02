"""
Modelo de Factura
--------------
Define el modelo de Factura y sus estados para el sistema de facturación.
"""

from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..db.base_class import Base
import enum

class EstadoFactura(str, enum.Enum):
    """Estados posibles de una factura"""
    PENDIENTE = "pendiente"
    PAGADA = "pagada"
    ANULADA = "anulada"
    PENDIENTE_PAGO = "pendiente_pago"  # Estado cuando se inicia un proceso de pago
    RECHAZADA = "rechazada"  # Estado cuando un pago es rechazado

class Factura(Base):
    """Modelo de Factura"""
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    servicio = Column(String(255), nullable=False)
    monto = Column(Float, nullable=False)
    estado = Column(Enum(EstadoFactura), nullable=False, default=EstadoFactura.PENDIENTE)
    fecha_emision = Column(DateTime(timezone=True), server_default=func.now())
    fecha_pago = Column(DateTime(timezone=True), nullable=True)
    numero_factura = Column(String(20), unique=True, nullable=False)
    descripcion = Column(String(500), nullable=True)
    metodo_pago = Column(String(50), nullable=True)
    
    # Campos para integración con MercadoPago
    mercadopago_id = Column(String(100), nullable=True)  # ID de la preferencia de pago de MercadoPago
    mercadopago_status = Column(String(50), nullable=True)  # Estado del pago en MercadoPago
    mercadopago_external_reference = Column(String(100), nullable=True)  # Referencia externa para identificación
    mercadopago_payment_id = Column(String(100), nullable=True)  # ID del pago procesado

    # Relaciones
    usuario = relationship("Usuario", back_populates="facturas")

    def __repr__(self):
        return f"<Factura {self.numero_factura}>" 