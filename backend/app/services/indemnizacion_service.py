"""
Servicio de Cálculo de Indemnización
---------------------------------
Este servicio implementa la lógica para calcular indemnizaciones por despido
según la legislación laboral colombiana.
"""

from typing import List, Tuple
from app.schemas.indemnizacion import (
    DespidoInput,
    IndemnizacionResponse,
    DetalleCalculo,
    TipoContrato,
    CausaDespido
)

class IndemnizacionService:
    """Servicio para cálculo de indemnización por despido"""
    
    def __init__(self):
        """Inicializa el servicio con valores constantes"""
        self.SMMLV_2024 = 1300000  # Salario Mínimo Legal Vigente 2024
        
    def calcular_indemnizacion(self, data: DespidoInput) -> IndemnizacionResponse:
        """
        Calcula la indemnización por despido según los datos proporcionados.
        
        Args:
            data: Datos del despido a evaluar
            
        Returns:
            Resultado del cálculo con detalles y recomendaciones
        """
        # 1. Verificar si tiene derecho a indemnización
        if not self._tiene_derecho_indemnizacion(data):
            return self._generar_respuesta_sin_derecho(data)
            
        # 2. Calcular salario base
        salario_base = self._calcular_salario_base(data)
        
        # 3. Calcular indemnización según tipo de contrato
        if data.tipo_contrato == TipoContrato.TERMINO_FIJO:
            indemnizacion, detalles = self._calcular_indemnizacion_fijo(data, salario_base)
        elif data.tipo_contrato == TipoContrato.OBRA_LABOR:
            indemnizacion, detalles = self._calcular_indemnizacion_obra_labor(data, salario_base)
        else:  # TERMINO_INDEFINIDO
            indemnizacion, detalles = self._calcular_indemnizacion_indefinido(data, salario_base)
            
        # 4. Generar recomendaciones
        recomendaciones = self._generar_recomendaciones(data, indemnizacion)
        
        # 5. Generar factores considerados
        factores = self._generar_factores_considerados(data)
        
        return IndemnizacionResponse(
            indemnizacion_total=indemnizacion,
            salario_base=salario_base,
            detalle_calculo=detalles,
            recomendaciones=recomendaciones,
            mensaje_resumen=self._generar_resumen(data, indemnizacion),
            tiene_derecho=True,
            factores_considerados=factores
        )
    
    def _tiene_derecho_indemnizacion(self, data: DespidoInput) -> bool:
        """Determina si el trabajador tiene derecho a indemnización"""
        if data.causa_despido in [CausaDespido.JUSTA_CAUSA, CausaDespido.RENUNCIA]:
            return False
        if data.tipo_contrato == TipoContrato.OBRA_LABOR and data.obra_terminada:
            return False
        return True
    
    def _calcular_salario_base(self, data: DespidoInput) -> float:
        """Calcula el salario base para la indemnización incluyendo factores salariales"""
        salario_base = data.salario_mensual
        
        # Agregar auxilio de transporte si aplica
        if data.auxilio_transporte and data.salario_mensual <= (2 * self.SMMLV_2024):
            salario_base += 162000  # Auxilio de transporte 2024
            
        # Agregar promedio de comisiones y horas extra
        salario_base += (data.comisiones_promedio or 0)
        salario_base += (data.horas_extra_promedio or 0)
        
        return salario_base
    
    def _calcular_indemnizacion_fijo(self, data: DespidoInput, salario_base: float) -> Tuple[float, List[DetalleCalculo]]:
        """Calcula la indemnización para contratos a término fijo"""
        detalles = []
        
        # Indemnización = salario por tiempo faltante
        indemnizacion = salario_base * data.meses_faltantes
        
        detalles.append(DetalleCalculo(
            concepto="Tiempo faltante",
            base=salario_base,
            factor=float(data.meses_faltantes),
            subtotal=indemnizacion,
            explicacion=f"Salario mensual × {data.meses_faltantes} meses faltantes"
        ))
        
        return indemnizacion, detalles
    
    def _calcular_indemnizacion_indefinido(self, data: DespidoInput, salario_base: float) -> Tuple[float, List[DetalleCalculo]]:
        """Calcula la indemnización para contratos a término indefinido"""
        detalles = []
        indemnizacion = 0
        
        # Primeros 12 meses: 30 días
        indemnizacion_base = salario_base
        detalles.append(DetalleCalculo(
            concepto="Indemnización base",
            base=salario_base,
            factor=1.0,
            subtotal=indemnizacion_base,
            explicacion="30 días de salario por el primer año"
        ))
        indemnizacion += indemnizacion_base
        
        # Por cada año adicional: 20 días
        if data.tiempo_trabajado_meses > 12:
            años_adicionales = (data.tiempo_trabajado_meses - 12) / 12
            dias_adicionales = años_adicionales * (20/30)  # 20 días por año en términos de salarios
            indemnizacion_adicional = salario_base * dias_adicionales
            
            detalles.append(DetalleCalculo(
                concepto="Años adicionales",
                base=salario_base,
                factor=dias_adicionales,
                subtotal=indemnizacion_adicional,
                explicacion=f"20 días de salario por {años_adicionales:.1f} años adicionales"
            ))
            indemnizacion += indemnizacion_adicional
        
        return indemnizacion, detalles
    
    def _calcular_indemnizacion_obra_labor(self, data: DespidoInput, salario_base: float) -> Tuple[float, List[DetalleCalculo]]:
        """Calcula la indemnización para contratos por obra labor"""
        detalles = []
        
        # Si la obra no ha terminado, se estima un tiempo promedio de 3 meses
        meses_estimados = 3
        indemnizacion = salario_base * meses_estimados
        
        detalles.append(DetalleCalculo(
            concepto="Tiempo estimado hasta fin de obra",
            base=salario_base,
            factor=float(meses_estimados),
            subtotal=indemnizacion,
            explicacion=f"Salario mensual × {meses_estimados} meses estimados para terminar la obra"
        ))
        
        return indemnizacion, detalles
    
    def _generar_recomendaciones(self, data: DespidoInput, indemnizacion: float) -> List[str]:
        """Genera recomendaciones basadas en el caso"""
        recomendaciones = []
        
        if indemnizacion > (4 * self.SMMLV_2024):
            recomendaciones.append(
                "Dado el monto de la indemnización, se recomienda consultar con un abogado laboral "
                "para asegurar la correcta liquidación y pago de sus prestaciones."
            )
        
        if data.tiempo_trabajado_meses > 24:
            recomendaciones.append(
                "Por su antigüedad, podría tener derecho a beneficios adicionales. "
                "Se recomienda verificar otros conceptos como primas y cesantías."
            )
            
        recomendaciones.append(
            "Recuerde que tiene 3 años para reclamar sus derechos laborales "
            "contados desde la fecha de terminación del contrato."
        )
        
        return recomendaciones
    
    def _generar_factores_considerados(self, data: DespidoInput) -> List[str]:
        """Genera lista de factores considerados en el cálculo"""
        factores = [
            f"Tipo de contrato: {data.tipo_contrato.value}",
            f"Tiempo trabajado: {data.tiempo_trabajado_meses} meses",
            f"Salario base: ${data.salario_mensual:,.0f}"
        ]
        
        if data.auxilio_transporte:
            factores.append("Auxilio de transporte incluido")
        if data.comisiones_promedio:
            factores.append(f"Promedio comisiones: ${data.comisiones_promedio:,.0f}")
        if data.horas_extra_promedio:
            factores.append(f"Promedio horas extra: ${data.horas_extra_promedio:,.0f}")
            
        return factores
    
    def _generar_resumen(self, data: DespidoInput, indemnizacion: float) -> str:
        """Genera un resumen del cálculo"""
        if not self._tiene_derecho_indemnizacion(data):
            return "No tiene derecho a indemnización por despido según la información proporcionada."
            
        return (
            f"De acuerdo al análisis realizado, la indemnización aproximada por despido "
            f"sin justa causa sería de ${indemnizacion:,.0f}. Este cálculo considera un "
            f"contrato a {data.tipo_contrato.value} con {data.tiempo_trabajado_meses} meses "
            f"de antigüedad."
        )
    
    def _generar_respuesta_sin_derecho(self, data: DespidoInput) -> IndemnizacionResponse:
        """Genera una respuesta cuando no hay derecho a indemnización"""
        mensaje = "No tiene derecho a indemnización por despido debido a: "
        
        if data.causa_despido == CausaDespido.JUSTA_CAUSA:
            mensaje += "el despido fue con justa causa."
        elif data.causa_despido == CausaDespido.RENUNCIA:
            mensaje += "la terminación del contrato fue por renuncia voluntaria."
        elif data.tipo_contrato == TipoContrato.OBRA_LABOR and data.obra_terminada:
            mensaje += "la obra o labor contratada fue terminada."
            
        return IndemnizacionResponse(
            indemnizacion_total=0,
            salario_base=self._calcular_salario_base(data),
            detalle_calculo=[],
            recomendaciones=[
                "Si considera que el motivo del despido no es justificado, "
                "puede consultar con un abogado laboral para evaluar su caso."
            ],
            mensaje_resumen=mensaje,
            tiene_derecho=False,
            factores_considerados=self._generar_factores_considerados(data)
        ) 