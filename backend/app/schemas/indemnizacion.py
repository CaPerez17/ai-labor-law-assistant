"""
Esquemas para el cálculo de indemnización por despido
-------------------------------------------------
Define los modelos de datos para el cálculo de indemnización por despido sin justa causa.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum
from datetime import date

class TipoContrato(str, Enum):
    """Tipos de contrato posibles"""
    TERMINO_FIJO = "termino_fijo"
    TERMINO_INDEFINIDO = "termino_indefinido"
    OBRA_LABOR = "obra_labor"

class CausaDespido(str, Enum):
    """Causas de despido posibles"""
    SIN_JUSTA_CAUSA = "sin_justa_causa"
    JUSTA_CAUSA = "justa_causa"
    TERMINACION_CONTRATO = "terminacion_contrato"
    RENUNCIA = "renuncia"

class DespidoInput(BaseModel):
    """Modelo para los datos de entrada del cálculo de indemnización"""
    tipo_contrato: TipoContrato = Field(..., description="Tipo de contrato laboral")
    salario_mensual: float = Field(..., gt=0, description="Salario mensual base")
    tiempo_trabajado_meses: int = Field(..., gt=0, description="Tiempo trabajado en meses")
    causa_despido: CausaDespido = Field(..., description="Causa del despido")
    
    # Solo para contratos a término fijo
    meses_faltantes: Optional[int] = Field(None, ge=0, description="Meses faltantes para terminar el contrato")
    
    # Solo para contratos por obra labor
    obra_terminada: Optional[bool] = Field(None, description="Indica si la obra o labor fue terminada")
    
    # Campos adicionales opcionales
    auxilio_transporte: Optional[bool] = Field(False, description="Indica si recibía auxilio de transporte")
    comisiones_promedio: Optional[float] = Field(0, ge=0, description="Promedio mensual de comisiones")
    horas_extra_promedio: Optional[float] = Field(0, ge=0, description="Promedio mensual de horas extra")

    @validator('meses_faltantes')
    def validar_meses_faltantes(cls, v, values):
        """Valida que los meses faltantes se especifiquen para contratos a término fijo"""
        if values.get('tipo_contrato') == TipoContrato.TERMINO_FIJO and v is None:
            raise ValueError("Debe especificar los meses faltantes para contratos a término fijo")
        return v

    @validator('obra_terminada')
    def validar_obra_terminada(cls, v, values):
        """Valida que se especifique si la obra fue terminada para contratos por obra labor"""
        if values.get('tipo_contrato') == TipoContrato.OBRA_LABOR and v is None:
            raise ValueError("Debe especificar si la obra fue terminada para contratos por obra labor")
        return v

class DetalleCalculo(BaseModel):
    """Modelo para el detalle del cálculo de indemnización"""
    concepto: str = Field(..., description="Concepto del cálculo")
    base: float = Field(..., description="Base del cálculo")
    factor: float = Field(..., description="Factor multiplicador")
    subtotal: float = Field(..., description="Subtotal del concepto")
    explicacion: str = Field(..., description="Explicación del cálculo")

class IndemnizacionResponse(BaseModel):
    """Modelo para la respuesta del cálculo de indemnización"""
    indemnizacion_total: float = Field(..., description="Monto total de la indemnización")
    salario_base: float = Field(..., description="Salario base usado para el cálculo")
    detalle_calculo: List[DetalleCalculo] = Field(..., description="Detalle del cálculo realizado")
    recomendaciones: List[str] = Field(..., description="Recomendaciones legales")
    mensaje_resumen: str = Field(..., description="Resumen del cálculo")
    tiene_derecho: bool = Field(..., description="Indica si tiene derecho a indemnización")
    factores_considerados: List[str] = Field(..., description="Factores considerados en el cálculo") 