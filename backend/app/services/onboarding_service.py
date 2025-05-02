"""
Servicio de Onboarding Conversacional
---------------------------------
Este servicio implementa la lógica para analizar las necesidades del usuario
y recomendar el flujo más apropiado.
"""

from typing import List, Dict, Any
from ..schemas.onboarding import OnboardingResponse, TipoFlujo

class OnboardingService:
    """Servicio para el proceso de onboarding"""
    
    def __init__(self):
        """Inicializa el servicio con las reglas de clasificación"""
        self.palabras_clave = {
            TipoFlujo.CONTRATO_REALIDAD: [
                'contrato realidad', 'relación laboral', 'subordinación',
                'trabajo sin contrato', 'contrato verbal', 'contrato por prestación de servicios',
                'contrato de obra', 'contrato de servicios', 'contrato civil'
            ],
            TipoFlujo.INDEMNIZACION: [
                'indemnización', 'cesantías', 'prima de servicios', 'vacaciones',
                'liquidación', 'despido', 'terminación', 'renuncia', 'finiquito',
                'prestaciones sociales', 'cesantías', 'prima', 'vacaciones'
            ],
            TipoFlujo.CONTRATO: [
                'generar contrato', 'crear contrato', 'redactar contrato',
                'modelo de contrato', 'plantilla de contrato', 'contrato de trabajo',
                'nuevo contrato', 'contrato laboral'
            ],
            TipoFlujo.ANALISIS_DOCUMENTO: [
                'analizar contrato', 'revisar contrato', 'evaluar contrato',
                'revisar documento', 'analizar documento', 'evaluar documento',
                'cláusulas', 'riesgos', 'términos'
            ]
        }
        
        self.mensajes_bienvenida = {
            TipoFlujo.CONTRATO_REALIDAD: "Entiendo que necesitas evaluar si existe una relación laboral real. Te ayudaré a analizar tu caso.",
            TipoFlujo.INDEMNIZACION: "Veo que necesitas calcular prestaciones sociales o liquidación. Te guiaré en el proceso.",
            TipoFlujo.CONTRATO: "Comprendo que necesitas generar un contrato de trabajo. Te ayudaré a crear uno adecuado.",
            TipoFlujo.ANALISIS_DOCUMENTO: "Entiendo que quieres analizar un documento legal. Te ayudaré a identificar aspectos importantes.",
            TipoFlujo.CONSULTA_GENERAL: "Gracias por contactarnos. Te ayudaré con tu consulta laboral."
        }
        
        self.pasos_sugeridos = {
            TipoFlujo.CONTRATO_REALIDAD: [
                "Describe las funciones que realizas",
                "Indica si tienes un horario establecido",
                "Menciona si tienes un jefe inmediato",
                "Especifica cómo recibes el pago"
            ],
            TipoFlujo.INDEMNIZACION: [
                "Ingresa tu salario actual",
                "Indica tu fecha de ingreso",
                "Especifica si tienes auxilio de transporte",
                "Menciona si tienes otros ingresos adicionales"
            ],
            TipoFlujo.CONTRATO: [
                "Selecciona el tipo de contrato",
                "Ingresa los datos del empleador",
                "Ingresa los datos del trabajador",
                "Especifica las condiciones laborales"
            ],
            TipoFlujo.ANALISIS_DOCUMENTO: [
                "Sube el documento a analizar",
                "Espera el análisis automático",
                "Revisa las cláusulas destacadas",
                "Consulta las recomendaciones"
            ],
            TipoFlujo.CONSULTA_GENERAL: [
                "Describe tu situación en detalle",
                "Menciona las fechas relevantes",
                "Especifica qué tipo de ayuda necesitas",
                "Indica si tienes documentos relacionados"
            ]
        }
    
    def analizar_necesidad(self, texto: str) -> OnboardingResponse:
        """
        Analiza el texto del usuario y recomienda el flujo más apropiado.
        
        Args:
            texto: Texto con la consulta del usuario
            
        Returns:
            Respuesta con el flujo recomendado y pasos a seguir
        """
        if not texto or len(texto.strip()) < 5:
            return OnboardingResponse(
                flujo_recomendado=TipoFlujo.CONSULTA_GENERAL,
                mensaje_bienvenida="Por favor, describe tu situación para poder ayudarte mejor.",
                pasos_sugeridos=["Explica tu caso en detalle"],
                necesita_abogado=False
            )
        
        texto = texto.lower()
        
        # Analizar el texto para cada tipo de flujo
        puntuaciones = {}
        razones = {}
        
        for tipo_flujo, palabras in self.palabras_clave.items():
            puntuacion = 0
            razones_encontradas = []
            
            for palabra in palabras:
                if palabra in texto:
                    puntuacion += 1
                    razones_encontradas.append(f"mencionaste '{palabra}'")
            
            if puntuacion > 0:
                puntuaciones[tipo_flujo] = puntuacion
                razones[tipo_flujo] = razones_encontradas
        
        # Si no se encontró ninguna coincidencia clara
        if not puntuaciones:
            return OnboardingResponse(
                flujo_recomendado=TipoFlujo.CONSULTA_GENERAL,
                mensaje_bienvenida="Tu consulta parece ser general. Te ayudaré a entender mejor tu situación.",
                pasos_sugeridos=self.pasos_sugeridos[TipoFlujo.CONSULTA_GENERAL],
                razon_recomendacion="No pude identificar un flujo específico para tu consulta.",
                necesita_abogado=True
            )
        
        # Seleccionar el flujo con mayor puntuación
        flujo_recomendado = max(puntuaciones.items(), key=lambda x: x[1])[0]
        
        # Determinar si se necesita un abogado
        necesita_abogado = (
            "complejo" in texto or
            "demanda" in texto or
            "demandar" in texto or
            "juicio" in texto or
            "proceso" in texto or
            "tribunal" in texto
        )
        
        return OnboardingResponse(
            flujo_recomendado=flujo_recomendado,
            mensaje_bienvenida=self.mensajes_bienvenida[flujo_recomendado],
            pasos_sugeridos=self.pasos_sugeridos[flujo_recomendado],
            razon_recomendacion=", ".join(razones[flujo_recomendado]),
            necesita_abogado=necesita_abogado
        ) 