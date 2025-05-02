"""
Esquemas para la generación de contratos laborales
--------------------------------------------
Define los modelos de datos para la generación automática de contratos laborales.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from datetime import date
import datetime

class TipoContrato(str, Enum):
    """Tipos de contrato disponibles"""
    TERMINO_FIJO = "termino_fijo"
    TERMINO_INDEFINIDO = "termino_indefinido"
    OBRA_LABOR = "obra_labor"
    DOMESTICO = "domestico"

class ModalidadTrabajo(str, Enum):
    """Modalidades de trabajo disponibles"""
    PRESENCIAL = "presencial"
    REMOTO = "remoto"
    HIBRIDO = "hibrido"

class ContratoInput(BaseModel):
    """Modelo para los datos de entrada de generación de contrato"""
    tipo_contrato: TipoContrato = Field(..., description="Tipo de contrato a generar")
    nombre_empleador: str = Field(..., min_length=3, description="Nombre completo del empleador")
    nit_empleador: str = Field(..., description="NIT o documento del empleador")
    direccion_empleador: str = Field(..., description="Dirección del empleador")
    nombre_empleado: str = Field(..., min_length=3, description="Nombre completo del empleado")
    documento_empleado: str = Field(..., description="Número de documento del empleado")
    cargo: str = Field(..., min_length=3, description="Cargo o posición a desempeñar")
    salario: float = Field(..., gt=0, description="Salario mensual en pesos colombianos")
    duracion_meses: Optional[int] = Field(None, gt=0, description="Duración del contrato en meses (solo para término fijo)")
    modalidad_trabajo: ModalidadTrabajo = Field(..., description="Modalidad de trabajo")
    fecha_inicio: date = Field(..., description="Fecha de inicio del contrato")
    lugar_trabajo: Optional[str] = Field(None, description="Ciudad o municipio donde se desarrollará el trabajo")
    funciones_principales: Optional[str] = Field(None, description="Descripción de las funciones principales")
    horario_trabajo: Optional[str] = Field(None, description="Horario de trabajo acordado")

    @validator('salario')
    def validar_salario_minimo(cls, v):
        """Valida que el salario sea al menos el mínimo legal vigente"""
        SMMLV_2024 = 1300000
        if v < SMMLV_2024:
            raise ValueError(f"El salario debe ser al menos el mínimo legal vigente (${SMMLV_2024:,})")
        return v

    @validator('fecha_inicio')
    def validar_fecha_inicio(cls, v):
        """Valida que la fecha de inicio no sea anterior a hoy"""
        if v < datetime.date.today():
            raise ValueError("La fecha de inicio no puede ser anterior a hoy")
        return v

    @validator('duracion_meses')
    def validar_duracion(cls, v, values):
        """Valida que se especifique duración para contratos a término fijo"""
        if values.get('tipo_contrato') == TipoContrato.TERMINO_FIJO:
            if v is None:
                raise ValueError("Debe especificar la duración para contratos a término fijo")
            if v < 1:
                raise ValueError("La duración debe ser de al menos 1 mes")
            if v > 36:
                raise ValueError("La duración no puede exceder 36 meses")
        return v

class ContratoResponse(BaseModel):
    """Modelo para la respuesta de generación de contrato"""
    contrato_generado: str = Field(..., description="Texto del contrato generado")
    tipo_contrato: TipoContrato = Field(..., description="Tipo de contrato generado")
    nombre_archivo: str = Field(..., description="Nombre sugerido para el archivo")
    fecha_generacion: date = Field(default_factory=date.today, description="Fecha de generación del contrato")
    advertencia: Optional[str] = Field(None, description="Advertencias o notas importantes sobre el contrato generado") 