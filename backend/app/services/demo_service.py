"""
Servicio para modo demo
----------------------
Proporciona versiones simuladas de servicios para el modo demo de LegalAssista.
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

class DemoService:
    """Servicio que proporciona funcionalidades simuladas para el modo demo"""
    
    @staticmethod
    def is_demo_mode() -> bool:
        """Verifica si el sistema está en modo demo"""
        return os.environ.get("LEGALASSISTA_DEMO", "").lower() == "true"
    
    @staticmethod
    async def analyze_document(content: str, document_name: str) -> Dict[str, Any]:
        """
        Simula el análisis de un documento con resultados predefinidos según el tipo de documento
        """
        content_lower = content.lower()
        
        # Identificar el tipo de documento
        if "contrato" in content_lower:
            return DemoService._contract_analysis(content, document_name)
        elif "renuncia" in content_lower:
            return DemoService._resignation_analysis(content, document_name)
        elif "despido" in content_lower:
            return DemoService._termination_analysis(content, document_name)
        else:
            return DemoService._generic_analysis(content, document_name)
    
    @staticmethod
    def _contract_analysis(content: str, document_name: str) -> Dict[str, Any]:
        """Simula el análisis de un contrato laboral"""
        content_lower = content.lower()
        
        # Detectar tipo de contrato
        tipo_contrato = "indefinido" if "indefinido" in content_lower else "fijo"
        if "obra" in content_lower or "labor" in content_lower:
            tipo_contrato = "obra o labor"
        
        # Detectar posibles problemas
        problemas = []
        if "prueba" in content_lower and "seis" in content_lower:
            problemas.append("El período de prueba excede los límites legales (máximo 2 meses).")
        
        if "jornada" in content_lower and ("12" in content_lower or "catorce" in content_lower):
            problemas.append("La jornada laboral excede el límite legal (máximo 8 horas ordinarias, posible extensión a 10).")
        
        if "salario" in content_lower and ("mínimo" not in content_lower and 
                              "$1.000.000" not in content_lower and 
                              "1.000.000" not in content_lower):
            problemas.append("Verifique que el salario cumpla con el mínimo legal vigente en Colombia.")
        
        return {
            "tipo_documento": "Contrato Laboral",
            "subtipo": f"Contrato a término {tipo_contrato}",
            "analisis": f"Este documento es un contrato de trabajo a término {tipo_contrato}. " + 
                      ("Se detectaron posibles problemas que requieren revisión." if problemas else 
                       "No se detectaron problemas evidentes en los términos principales."),
            "elementos_clave": {
                "tipo_contrato": tipo_contrato,
                "salario": "Se menciona en el documento" if "salario" in content_lower else "No especificado",
                "jornada": "Se menciona en el documento" if "jornada" in content_lower else "No especificada",
                "obligaciones": "Se detallan en el documento" if "obligaciones" in content_lower else "No especificadas",
            },
            "hallazgos": problemas,
            "recomendaciones": [
                "Consulte con un abogado especialista antes de firmar el contrato.",
                "Asegúrese de que todas las condiciones importantes estén por escrito.",
                "Verifique los términos de causales de terminación y preaviso."
            ] + (["Solicite la corrección de los problemas identificados."] if problemas else []),
            "riesgo": "Alto" if problemas else "Bajo",
            "fecha_analisis": datetime.now().isoformat(),
            "modo": "demo"
        }
    
    @staticmethod
    def _resignation_analysis(content: str, document_name: str) -> Dict[str, Any]:
        """Simula el análisis de una carta de renuncia"""
        content_lower = content.lower()
        
        # Detectar si hay preaviso
        preaviso = "con preaviso" if "preaviso" in content_lower else "sin preaviso"
        
        # Detectar problemas potenciales
        problemas = []
        if "inmediata" in content_lower and "preaviso" not in content_lower:
            problemas.append("La renuncia no contiene preaviso, lo cual podría generar inconvenientes.")
        
        if "presión" in content_lower or "obligado" in content_lower or "forzado" in content_lower:
            problemas.append("El documento sugiere que la renuncia podría no ser voluntaria.")
        
        return {
            "tipo_documento": "Carta de Renuncia",
            "subtipo": f"Renuncia {preaviso}",
            "analisis": f"Este documento es una carta de renuncia {preaviso}. " + 
                      ("Se detectaron posibles problemas que requieren revisión." if problemas else 
                       "No se detectaron problemas evidentes en los términos principales."),
            "elementos_clave": {
                "tipo_renuncia": preaviso,
                "fecha_efectiva": "Se especifica en el documento" if "efecto" in content_lower or "efectiva" in content_lower else "No especificada",
                "motivo": "Se menciona en el documento" if "motivo" in content_lower or "razón" in content_lower else "No especificado",
            },
            "hallazgos": problemas,
            "recomendaciones": [
                "Asegúrese de recibir una copia de la carta con sello de recibido.",
                "Solicite su liquidación detallada de prestaciones sociales.",
                "Verifique que se respeten sus derechos durante el proceso de desvinculación."
            ] + (["Consulte con un abogado antes de presentar esta renuncia."] if problemas else []),
            "riesgo": "Medio" if problemas else "Bajo",
            "fecha_analisis": datetime.now().isoformat(),
            "modo": "demo"
        }
    
    @staticmethod
    def _termination_analysis(content: str, document_name: str) -> Dict[str, Any]:
        """Simula el análisis de una carta de despido"""
        content_lower = content.lower()
        
        # Detectar tipo de despido
        tipo_despido = "con justa causa" if "justa causa" in content_lower else "sin justa causa"
        
        # Detectar problemas potenciales
        problemas = []
        if tipo_despido == "con justa causa" and "artículo 62" not in content_lower:
            problemas.append("No se cita el artículo del CST que sustenta la justa causa.")
        
        if "inmediato" in content_lower and "indemnización" not in content_lower and tipo_despido == "sin justa causa":
            problemas.append("No se menciona la indemnización correspondiente por despido sin justa causa.")
        
        return {
            "tipo_documento": "Carta de Despido",
            "subtipo": f"Despido {tipo_despido}",
            "analisis": f"Este documento es una carta de despido {tipo_despido}. " + 
                      ("Se detectaron posibles problemas que requieren revisión." if problemas else 
                       "No se detectaron problemas evidentes en los términos principales."),
            "elementos_clave": {
                "tipo_despido": tipo_despido,
                "fecha_efectiva": "Se especifica en el documento" if "efecto" in content_lower or "efectiva" in content_lower else "No especificada",
                "motivo": "Se menciona claramente" if ("motivo" in content_lower or "razón" in content_lower) and tipo_despido == "con justa causa" else "No especificado adecuadamente",
                "indemnización": "Se menciona" if "indemnización" in content_lower and tipo_despido == "sin justa causa" else "No se menciona"
            },
            "hallazgos": problemas,
            "recomendaciones": [
                "Consulte con un abogado para verificar la legalidad del despido.",
                "Solicite por escrito su liquidación detallada de prestaciones sociales.",
                "Verifique los cálculos de su liquidación e indemnización si corresponde."
            ] + (["Considere acciones legales si el despido no cumple los requisitos legales."] if problemas else []),
            "riesgo": "Alto" if problemas else "Medio",
            "fecha_analisis": datetime.now().isoformat(),
            "modo": "demo"
        }
    
    @staticmethod
    def _generic_analysis(content: str, document_name: str) -> Dict[str, Any]:
        """Proporciona un análisis genérico para documentos no identificados específicamente"""
        return {
            "tipo_documento": "Documento Legal",
            "subtipo": "Documento no clasificado específicamente",
            "analisis": "Este documento contiene texto relacionado con términos legales laborales. Para un análisis más preciso, recomendamos utilizar nuestra versión completa o consultar con uno de nuestros abogados.",
            "elementos_clave": {
                "longitud": f"{len(content)} caracteres",
                "complejidad": random.choice(["Alta", "Media", "Baja"])
            },
            "hallazgos": [
                "Documento pendiente de clasificación especializada.",
                "Se requiere revisión manual por un experto."
            ],
            "recomendaciones": [
                "Consulte con un abogado especializado para una revisión detallada.",
                "Utilice nuestro servicio completo para un análisis más preciso y personalizado.",
                "Considere categorizar el documento para un mejor análisis automático."
            ],
            "riesgo": "No determinado",
            "fecha_analisis": datetime.now().isoformat(),
            "modo": "demo"
        }
    
    @staticmethod
    async def send_email(to_email: str, subject: str, content: str) -> Dict[str, Any]:
        """Simula el envío de un email en modo demo"""
        print(f"[DEMO MODE] Email no enviado realmente a: {to_email}")
        print(f"[DEMO MODE] Asunto: {subject}")
        print(f"[DEMO MODE] Contenido: {content[:100]}...")
        
        return {
            "success": True,
            "message": "Email simulado en modo demo (no enviado realmente)",
            "to": to_email,
            "subject": subject,
            "date": datetime.now().isoformat(),
            "modo": "demo"
        }
    
    @staticmethod
    async def answer_legal_question(question: str) -> Dict[str, Any]:
        """Proporciona respuestas predefinidas a preguntas legales comunes en modo demo"""
        question_lower = question.lower()
        
        # Preguntas y respuestas predefinidas
        responses = {
            "derecho a prima": {
                "respuesta": "Sí, todos los trabajadores tienen derecho a la prima de servicios. Es una prestación social que equivale a un mes de salario por año, pagadero en dos cuotas: 15 días en junio y 15 días en diciembre.",
                "fuente": "Código Sustantivo del Trabajo, artículos 306 al 308."
            },
            "periodo de prueba": {
                "respuesta": "El período de prueba es la etapa inicial del contrato de trabajo, con duración máxima de 2 meses, durante el cual ambas partes pueden terminar el contrato sin indemnización.",
                "fuente": "Código Sustantivo del Trabajo, artículo 78."
            },
            "cesantías": {
                "respuesta": "Las cesantías equivalen a un mes de salario por cada año de servicio. Deben ser consignadas anualmente al fondo elegido por el trabajador, antes del 14 de febrero.",
                "fuente": "Ley 50 de 1990, artículo 99."
            },
            "vacaciones": {
                "respuesta": "Todo trabajador tiene derecho a 15 días hábiles consecutivos de vacaciones remuneradas por cada año de servicio.",
                "fuente": "Código Sustantivo del Trabajo, artículo 186."
            },
            "despido sin justa causa": {
                "respuesta": "El empleador que despida sin justa causa debe pagar una indemnización. El monto varía según el tipo de contrato y el salario del trabajador.",
                "fuente": "Código Sustantivo del Trabajo, artículo 64."
            }
        }
        
        # Buscar coincidencias en las preguntas predefinidas
        respuesta = None
        for key, value in responses.items():
            if key in question_lower:
                respuesta = value
                break
        
        # Respuesta predeterminada si no hay coincidencias
        if not respuesta:
            respuesta = {
                "respuesta": "Esta pregunta requiere un análisis más detallado. En una versión no demo, nuestro sistema de IA analizaría su consulta específica y proporcionaría una respuesta basada en la legislación laboral colombiana vigente.",
                "fuente": "Para obtener respuestas más precisas, utilice la versión completa del sistema o consulte con uno de nuestros abogados especialistas."
            }
        
        return {
            "pregunta": question,
            "respuesta": respuesta["respuesta"],
            "fuente_legal": respuesta["fuente"],
            "análisis_adicional": "Para un análisis completo y personalizado, utilice nuestra versión completa o solicite una consulta con un abogado especializado.",
            "fecha_respuesta": datetime.now().isoformat(),
            "modo": "demo"
        } 