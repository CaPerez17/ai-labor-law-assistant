"""
Esquemas para el análisis de contrato realidad
--------------------------------------------
Define los modelos de datos para el análisis de contrato realidad.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class TipoContrato(str, Enum):
    """Tipos de contrato posibles"""
    PRESTACION_SERVICIOS = "prestacion_servicios"
    OBRA_LABOR = "obra_labor"
    TERMINO_FIJO = "termino_fijo"
    TERMINO_INDEFINIDO = "termino_indefinido"
    VERBAL = "verbal"
    OTRO = "otro"

class TipoSalario(str, Enum):
    """Tipos de remuneración"""
    FIJO = "fijo"
    POR_TAREA = "por_tarea"
    MIXTO = "mixto"
    OTRO = "otro"

class ContratoRealidadInput(BaseModel):
    """Modelo para los datos de entrada del análisis de contrato realidad"""
    tipo_contrato: TipoContrato = Field(..., description="Tipo de contrato actual")
    funciones: str = Field(..., min_length=10, description="Descripción de las funciones realizadas")
    tipo_salario: TipoSalario = Field(..., description="Tipo de remuneración recibida")
    salario_aproximado: float = Field(..., gt=0, description="Monto aproximado de remuneración mensual")
    tiene_supervisor: bool = Field(..., description="Indica si recibe órdenes de un supervisor")
    supervisor_cargo: Optional[str] = Field(None, description="Cargo del supervisor si aplica")
    tiempo_trabajado_meses: int = Field(..., gt=0, description="Tiempo trabajado en meses")
    horario_fijo: bool = Field(..., description="Indica si tiene un horario fijo")
    herramientas_propias: bool = Field(..., description="Indica si usa herramientas propias")
    exclusividad: bool = Field(..., description="Indica si tiene exclusividad con el empleador")

class RiesgoNivel(str, Enum):
    """Niveles de riesgo para contrato realidad"""
    ALTO = "alto"
    MEDIO = "medio"
    BAJO = "bajo"

class ContratoRealidadResponse(BaseModel):
    """Modelo para la respuesta del análisis de contrato realidad"""
    existe_riesgo: bool = Field(..., description="Indica si existe riesgo de contrato realidad")
    nivel_riesgo: RiesgoNivel = Field(..., description="Nivel de riesgo identificado")
    factores_riesgo: list[str] = Field(default_factory=list, description="Factores que contribuyen al riesgo")
    recomendaciones: list[str] = Field(default_factory=list, description="Recomendaciones legales")
    mensaje_resumen: str = Field(..., description="Resumen del análisis")
    puntaje_riesgo: float = Field(..., ge=0, le=1, description="Puntaje numérico de riesgo (0-1)") 