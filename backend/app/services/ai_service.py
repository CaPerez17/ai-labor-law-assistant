"""
Servicio de IA para Generación de Respuestas
-----------------------------------------
Este módulo implementa la integración con modelos GPT para generar
respuestas a consultas sobre derecho laboral.
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from datetime import datetime

from ..schemas.legal_document import LegalDocumentResponse
from ..schemas.query import QueryResponse, QueryStatus


class AIService:
    """Servicio para generación de respuestas basadas en IA"""

    def __init__(self):
        """Inicializa el cliente de OpenAI y configura el modelo"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurada en las variables de entorno")
            
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("GPT_MODEL", "gpt-4o")
        
    def generate_response(
        self, 
        query_text: str, 
        relevant_documents: List[LegalDocumentResponse],
        threshold: float = 0.7
    ) -> Tuple[str, float, bool, Optional[str]]:
        """
        Genera una respuesta a la consulta del usuario utilizando GPT.
        
        Args:
            query_text: Texto de la consulta del usuario
            relevant_documents: Documentos relevantes recuperados
            threshold: Umbral de confianza para decidir si se necesita revisión humana
            
        Returns:
            Tupla con:
            - Texto de respuesta generada
            - Puntuación de confianza
            - Indicador de si necesita revisión humana
            - Razón de la revisión (opcional)
        """
        # Construir el contexto con los documentos relevantes
        context = self._build_context(relevant_documents)
        
        # Construir el prompt para GPT
        system_prompt = """
        Eres un asistente legal especializado en derecho laboral colombiano. Tu tarea es proporcionar
        información precisa y útil basada únicamente en los documentos legales proporcionados.
        
        Reglas importantes:
        1. Basa tus respuestas ÚNICAMENTE en la información de los documentos proporcionados.
        2. Si no puedes responder con la información disponible, indica claramente que no tienes suficiente información.
        3. No inventes información ni cites leyes o regulaciones que no estén en los documentos proporcionados.
        4. Proporciona respuestas claras, concisas y en un lenguaje accesible.
        5. Incluye referencias específicas a los documentos legales relevantes.
        6. Si la consulta es ambigua o requiere más información, indícalo.
        7. Si la consulta es compleja y requiere asesoría profesional, indícalo.
        
        Evalúa tu confianza en la respuesta en una escala de 0 a 1, donde:
        - 0.0-0.3: Información insuficiente
        - 0.4-0.6: Información parcial pero requiere más contexto
        - 0.7-0.9: Información suficiente pero con algunas limitaciones
        - 1.0: Información completa y precisa
        
        Formato de respuesta:
        1. Responde la consulta de forma clara y precisa.
        2. Cita las fuentes relevantes.
        3. Al final, incluye tu evaluación de confianza en el siguiente formato exacto:
        "CONFIANZA: [puntuación]"
        """
        
        user_prompt = f"""
        Consulta del usuario: {query_text}
        
        Documentos legales relevantes:
        {context}
        
        Basándote únicamente en estos documentos, responde a la consulta del usuario.
        """
        
        try:
            # Llamar a la API de OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Bajo para generar respuestas más consistentes
                max_tokens=1000
            )
            
            # Extraer la respuesta y la puntuación de confianza
            response_text = response.choices[0].message.content
            confidence_score = self._extract_confidence_score(response_text)
            
            # Determinar si necesita revisión humana
            needs_human_review = confidence_score < threshold
            review_reason = None
            
            if needs_human_review:
                review_reason = "Baja confianza en la respuesta generada"
                
            # Limpiar la respuesta para quitar la línea de confianza
            clean_response = self._clean_response(response_text)
            
            return clean_response, confidence_score, needs_human_review, review_reason
            
        except Exception as e:
            # En caso de error, devolver mensaje genérico y solicitar revisión humana
            return (
                "Lo siento, no pude procesar tu consulta en este momento. Un especialista revisará tu caso.",
                0.0,
                True,
                f"Error en la generación de respuesta: {str(e)}"
            )
    
    def _build_context(self, documents: List[LegalDocumentResponse]) -> str:
        """Construye el contexto a partir de los documentos relevantes"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            context_part = f"""
            Documento {i}:
            Título: {doc.title}
            Tipo: {doc.document_type}
            Referencia: {doc.reference_number}
            Fecha: {doc.issue_date.strftime('%d/%m/%Y') if doc.issue_date else 'No especificada'}
            
            Contenido:
            {doc.content[:1000]}...
            
            """
            context_parts.append(context_part)
            
        return "\n".join(context_parts)
    
    def _extract_confidence_score(self, response_text: str) -> float:
        """Extrae la puntuación de confianza de la respuesta"""
        try:
            # Buscar el patrón "CONFIANZA: [puntuación]"
            import re
            match = re.search(r"CONFIANZA:\s*(0\.\d+|1\.0|1)", response_text)
            if match:
                return float(match.group(1))
            return 0.5  # Valor por defecto si no se encuentra
        except:
            return 0.5  # Valor por defecto en caso de error
    
    def _clean_response(self, response_text: str) -> str:
        """Elimina la línea de confianza de la respuesta"""
        import re
        return re.sub(r"\n?CONFIANZA:\s*(0\.\d+|1\.0|1)\s*$", "", response_text).strip() 