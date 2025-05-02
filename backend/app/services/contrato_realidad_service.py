"""
Servicio de Análisis de Contrato Realidad
---------------------------------------
Este servicio implementa la lógica para evaluar si existe un contrato realidad
basado en los elementos esenciales del contrato de trabajo según el CST:
1. Actividad personal
2. Subordinación o dependencia
3. Remuneración
"""

from typing import Dict, List, Tuple
from ..schemas.contrato_realidad import (
    ContratoRealidadInput,
    ContratoRealidadResponse,
    RiesgoNivel,
    TipoContrato,
    TipoSalario
)

class ContratoRealidadService:
    """Servicio para análisis de contrato realidad"""
    
    def __init__(self):
        """Inicializa el servicio con los umbrales de riesgo"""
        self.UMBRAL_RIESGO_ALTO = 0.7
        self.UMBRAL_RIESGO_MEDIO = 0.4
        
    def evaluar_contrato_realidad(self, data: ContratoRealidadInput) -> ContratoRealidadResponse:
        """
        Evalúa si existe riesgo de contrato realidad basado en los datos proporcionados.
        
        Args:
            data: Datos del contrato a evaluar
            
        Returns:
            Resultado del análisis con nivel de riesgo y recomendaciones
        """
        # 1. Evaluar cada elemento esencial
        factores_riesgo = []
        puntajes: Dict[str, float] = {}
        
        # 1.1 Actividad Personal
        puntaje_actividad, factores_actividad = self._evaluar_actividad_personal(data)
        puntajes["actividad_personal"] = puntaje_actividad
        factores_riesgo.extend(factores_actividad)
        
        # 1.2 Subordinación
        puntaje_subordinacion, factores_subordinacion = self._evaluar_subordinacion(data)
        puntajes["subordinacion"] = puntaje_subordinacion
        factores_riesgo.extend(factores_subordinacion)
        
        # 1.3 Remuneración
        puntaje_remuneracion, factores_remuneracion = self._evaluar_remuneracion(data)
        puntajes["remuneracion"] = puntaje_remuneracion
        factores_riesgo.extend(factores_remuneracion)
        
        # 2. Calcular puntaje final
        puntaje_final = self._calcular_puntaje_final(puntajes)
        
        # 3. Determinar nivel de riesgo
        nivel_riesgo = self._determinar_nivel_riesgo(puntaje_final)
        
        # 4. Generar recomendaciones
        recomendaciones = self._generar_recomendaciones(nivel_riesgo, data)
        
        # 5. Generar mensaje resumen
        mensaje_resumen = self._generar_resumen(nivel_riesgo, factores_riesgo, data)
        
        return ContratoRealidadResponse(
            existe_riesgo=puntaje_final >= self.UMBRAL_RIESGO_MEDIO,
            nivel_riesgo=nivel_riesgo,
            factores_riesgo=factores_riesgo,
            recomendaciones=recomendaciones,
            mensaje_resumen=mensaje_resumen,
            puntaje_riesgo=puntaje_final
        )
    
    def _evaluar_actividad_personal(self, data: ContratoRealidadInput) -> Tuple[float, List[str]]:
        """Evalúa el elemento de actividad personal"""
        factores = []
        puntaje = 0.0
        
        # La exclusividad es un fuerte indicador de actividad personal
        if data.exclusividad:
            puntaje += 0.4
            factores.append("Existe un requisito de exclusividad")
            
        # El uso de herramientas propias del empleador sugiere actividad personal
        if not data.herramientas_propias:
            puntaje += 0.3
            factores.append("Se utilizan herramientas proporcionadas por el empleador")
            
        # Tiempo trabajado extenso sugiere actividad personal continua
        if data.tiempo_trabajado_meses > 12:
            puntaje += 0.3
            factores.append(f"La relación laboral se ha extendido por {data.tiempo_trabajado_meses} meses")
            
        return min(1.0, puntaje), factores
    
    def _evaluar_subordinacion(self, data: ContratoRealidadInput) -> Tuple[float, List[str]]:
        """Evalúa el elemento de subordinación"""
        factores = []
        puntaje = 0.0
        
        # Supervisión directa
        if data.tiene_supervisor:
            puntaje += 0.4
            factores.append(f"Existe supervisión directa por parte de {data.supervisor_cargo or 'un superior'}")
        
        # Horario fijo
        if data.horario_fijo:
            puntaje += 0.3
            factores.append("Se debe cumplir un horario fijo")
        
        # Tipo de contrato que sugiere subordinación
        if data.tipo_contrato in [TipoContrato.VERBAL, TipoContrato.PRESTACION_SERVICIOS]:
            puntaje += 0.3
            factores.append(f"El tipo de contrato ({data.tipo_contrato.value}) puede ocultar una relación laboral")
            
        return min(1.0, puntaje), factores
    
    def _evaluar_remuneracion(self, data: ContratoRealidadInput) -> Tuple[float, List[str]]:
        """Evalúa el elemento de remuneración"""
        factores = []
        puntaje = 0.0
        
        # Salario fijo sugiere relación laboral
        if data.tipo_salario == TipoSalario.FIJO:
            puntaje += 0.4
            factores.append("La remuneración es fija y periódica")
        
        # Salario mixto también puede indicar relación laboral
        elif data.tipo_salario == TipoSalario.MIXTO:
            puntaje += 0.3
            factores.append("La remuneración combina elementos fijos y variables")
            
        # Verificar si el salario es cercano al mínimo
        if data.salario_aproximado <= 1160000:  # Aproximadamente un SMLV 2024
            puntaje += 0.3
            factores.append("La remuneración es cercana al salario mínimo legal")
            
        return min(1.0, puntaje), factores
    
    def _calcular_puntaje_final(self, puntajes: Dict[str, float]) -> float:
        """Calcula el puntaje final ponderado"""
        pesos = {
            "subordinacion": 0.4,
            "remuneracion": 0.3,
            "actividad_personal": 0.3
        }
        return sum(puntaje * pesos[factor] for factor, puntaje in puntajes.items())
    
    def _determinar_nivel_riesgo(self, puntaje: float) -> RiesgoNivel:
        """Determina el nivel de riesgo basado en el puntaje"""
        if puntaje >= self.UMBRAL_RIESGO_ALTO:
            return RiesgoNivel.ALTO
        elif puntaje >= self.UMBRAL_RIESGO_MEDIO:
            return RiesgoNivel.MEDIO
        return RiesgoNivel.BAJO
    
    def _generar_recomendaciones(self, nivel_riesgo: RiesgoNivel, data: ContratoRealidadInput) -> List[str]:
        """Genera recomendaciones basadas en el nivel de riesgo"""
        recomendaciones = []
        
        if nivel_riesgo == RiesgoNivel.ALTO:
            recomendaciones.extend([
                "Consulte con un abogado laboral para evaluar su caso específico",
                "Recopile evidencia de la relación laboral (correos, mensajes, testigos)",
                "Documente sus funciones y horarios diarios",
                "Considere presentar una reclamación ante el Ministerio del Trabajo"
            ])
        elif nivel_riesgo == RiesgoNivel.MEDIO:
            recomendaciones.extend([
                "Solicite una clarificación por escrito de su relación contractual",
                "Mantenga un registro detallado de sus actividades y pagos",
                "Considere buscar asesoría legal preventiva"
            ])
        else:
            recomendaciones.extend([
                "Mantenga registros de cualquier cambio en sus condiciones laborales",
                "Revise periódicamente los términos de su contrato"
            ])
            
        return recomendaciones
    
    def _generar_resumen(self, nivel_riesgo: RiesgoNivel, factores: List[str], data: ContratoRealidadInput) -> str:
        """Genera un resumen del análisis"""
        if nivel_riesgo == RiesgoNivel.ALTO:
            base = "Existe un alto riesgo de que su relación contractual sea considerada un contrato realidad"
        elif nivel_riesgo == RiesgoNivel.MEDIO:
            base = "Existen elementos que podrían indicar la existencia de un contrato realidad"
        else:
            base = "La relación contractual actual presenta bajo riesgo de ser considerada un contrato realidad"
            
        if factores:
            base += ". Los principales factores identificados son: " + "; ".join(factores[:3])
            
        return base 