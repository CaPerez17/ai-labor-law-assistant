"""
Servicio de IA para Generación de Respuestas
-----------------------------------------
Este módulo implementa la integración con modelos GPT para generar
respuestas a consultas sobre derecho laboral.
"""

import os
import json
import re
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
        
    def format_bm25_context(self, query_text: str, search_results: List[Dict[str, Any]], 
                           max_documents: int = 5, max_chars_per_doc: int = 2000) -> Dict[str, Any]:
        """
        Formatea los resultados de BM25 en un contexto estructurado para GPT.
        
        Args:
            query_text: Texto de la consulta del usuario
            search_results: Lista de documentos relevantes recuperados con BM25
            max_documents: Número máximo de documentos a incluir
            max_chars_per_doc: Longitud máxima de contenido por documento
            
        Returns:
            Contexto estructurado como diccionario para enviar a GPT
        """
        # Limitar a los más relevantes
        top_results = search_results[:max_documents]
        
        # Crear contexto estructurado
        formatted_documents = []
        for i, doc in enumerate(top_results, 1):
            # Extraer identificadores para citas
            doc_id = f"[Doc{i}]"
            legal_reference = ""
            
            # Determinar tipo de referencia basado en document_type
            doc_type = str(doc.get("document_type", "")).lower()
            if "ley" in doc_type:
                legal_reference = f"Ley-{doc.get('reference_number', 'N/A')}"
            elif "decreto" in doc_type:
                legal_reference = f"Decreto-{doc.get('reference_number', 'N/A')}"
            elif "sentencia" in doc_type:
                legal_reference = f"Sentencia-{doc.get('reference_number', 'N/A')}"
            elif "código" in doc_type or "cst" in doc_type.lower():
                legal_reference = f"CST-{doc.get('reference_number', 'N/A')}"
            else:
                legal_reference = doc.get('reference_number', 'N/A')
            
            # Crear documento estructurado con snippet y contenido completo
            formatted_doc = {
                "id": doc_id,
                "titulo": doc.get("title", "Documento sin título"),
                "referencia": legal_reference,
                "tipo": doc.get("document_type", "No especificado"),
                "relevancia": round(float(doc.get("relevance_score", 0)), 3),
                "contenido": doc.get("snippet", "")[:max_chars_per_doc],
                "texto_completo_disponible": len(doc.get("content", "")) > len(doc.get("snippet", ""))
            }
            
            formatted_documents.append(formatted_doc)
        
        # Crear contexto completo
        context = {
            "consulta_usuario": query_text,
            "documentos_relevantes": formatted_documents,
            "timestamp": datetime.now().isoformat(),
            "total_documentos_encontrados": len(search_results),
            "documentos_incluidos": len(formatted_documents)
        }
        
        return context
        
    def generate_response(
        self, 
        query_text: str, 
        search_results: List[Dict[str, Any]],
        threshold: float = 0.7
    ) -> Tuple[str, float, bool, Optional[str]]:
        """
        Genera una respuesta a la consulta del usuario utilizando GPT.
        
        Args:
            query_text: Texto de la consulta del usuario
            search_results: Documentos relevantes recuperados con BM25
            threshold: Umbral de confianza para decidir si se necesita revisión humana
            
        Returns:
            Tupla con:
            - Texto de respuesta generada
            - Puntuación de confianza
            - Indicador de si necesita revisión humana
            - Razón de la revisión (opcional)
        """
        # Formatear el contexto de BM25 para GPT
        context = self.format_bm25_context(query_text, search_results)
        
        # Optimizar el prompt para GPT
        system_prompt = """
        Eres un asistente legal especializado en derecho laboral colombiano. Tu tarea es proporcionar
        información precisa y fundamentada basada ÚNICAMENTE en los documentos legales proporcionados.
        
        REGLAS ESTRICTAS:
        1. NUNCA inventes información o cites leyes que no estén en los documentos proporcionados.
        2. SIEMPRE incluye citas específicas a los documentos usando el formato [DocX], donde X es el número del documento.
        3. SIEMPRE incluye las referencias legales exactas (números de ley, artículos, etc.) tal como aparecen en los documentos.
        4. Si no puedes responder con la información disponible, indica claramente: "No tengo suficiente información en los documentos proporcionados para responder esta consulta de forma completa."
        5. Usa lenguaje claro, directo y comprensible para personas sin formación jurídica.
        6. SIEMPRE incluye un apartado "Referencias Legales" al final con la lista de documentos citados.
        
        ESTRUCTURA DE RESPUESTA:
        1. RESPUESTA DIRECTA: Comienza con una respuesta directa y concisa a la pregunta.
        2. EXPLICACIÓN DETALLADA: Desarrolla la respuesta citando documentos específicos.
        3. DETALLES ADICIONALES: Incluye condiciones, excepciones o aclaraciones si existen.
        4. REFERENCIAS LEGALES: Lista de documentos citados con sus referencias.
        5. CONFIANZA: Evalúa tu confianza en la respuesta en una escala de 0 a 1.
        
        Evalúa tu confianza en la respuesta en una escala de 0 a 1:
        - 0.0-0.3: Información insuficiente o documentos poco relevantes
        - 0.4-0.6: Información parcial con algunas lagunas
        - 0.7-0.9: Información suficiente con documentos relevantes
        - 1.0: Información completa y precisa con documentos altamente relevantes
        
        Al final, incluye tu evaluación de confianza en el siguiente formato exacto:
        "CONFIANZA: [puntuación]"
        """
        
        # Convertir contexto a formato JSON
        context_json = json.dumps(context, ensure_ascii=False, indent=2)
        
        user_prompt = f"""
        CONSULTA DEL USUARIO: {query_text}
        
        DOCUMENTOS LEGALES RELEVANTES:
        {context_json}
        
        Responde basándote EXCLUSIVAMENTE en los documentos proporcionados. Incluye citas específicas a los documentos [DocX] y referencia los artículos o leyes exactas mencionadas en ellos.
        """
        
        try:
            # Llamar a la API de OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Bajo para generar respuestas más consistentes y precisas
                max_tokens=1200
            )
            
            # Extraer la respuesta y la puntuación de confianza
            response_text = response.choices[0].message.content
            confidence_score = self._extract_confidence_score(response_text)
            
            # Determinar si necesita revisión humana
            needs_human_review = confidence_score < threshold
            review_reason = None
            
            if needs_human_review:
                if confidence_score < 0.4:
                    review_reason = "Información insuficiente en los documentos proporcionados"
                else:
                    review_reason = "Información parcial que requiere verificación"
                
            # Limpiar la respuesta para quitar la línea de confianza
            clean_response = self._clean_response(response_text)
            
            # Formatear las referencias para que sean más legibles
            clean_response = self._format_legal_references(clean_response)
            
            return clean_response, confidence_score, needs_human_review, review_reason
            
        except Exception as e:
            # En caso de error, devolver mensaje genérico y solicitar revisión humana
            return (
                "Lo siento, no pude procesar tu consulta en este momento. Un especialista revisará tu caso.",
                0.0,
                True,
                f"Error en la generación de respuesta: {str(e)}"
            )
    
    def _extract_confidence_score(self, response_text: str) -> float:
        """Extrae la puntuación de confianza de la respuesta"""
        try:
            # Buscar el patrón "CONFIANZA: [puntuación]"
            match = re.search(r"CONFIANZA:\s*(0\.\d+|1\.0|1)", response_text)
            if match:
                return float(match.group(1))
            return 0.5  # Valor por defecto si no se encuentra
        except:
            return 0.5  # Valor por defecto en caso de error
    
    def _clean_response(self, response_text: str) -> str:
        """Elimina la línea de confianza de la respuesta"""
        return re.sub(r"\n?CONFIANZA:\s*(0\.\d+|1\.0|1)\s*$", "", response_text).strip()
    
    def _format_legal_references(self, response_text: str) -> str:
        """Mejora el formato de las referencias legales"""
        # Destacar referencias a documentos
        formatted_text = re.sub(r'\[Doc(\d+)\]', r'[**Doc\1**]', response_text)
        
        # Destacar referencias a artículos
        formatted_text = re.sub(r'(artículo|art\.|art)\s+(\d+)', r'Artículo \2', formatted_text, flags=re.IGNORECASE)
        
        # Destacar referencias a leyes
        formatted_text = re.sub(r'(ley)\s+(\d+)(\s+de\s+\d{4})?', r'Ley \2\3', formatted_text, flags=re.IGNORECASE)
        
        return formatted_text
    
    def extract_document_citations(self, response_text: str) -> List[str]:
        """Extrae referencias a documentos de la respuesta"""
        citations = []
        matches = re.findall(r'\[Doc(\d+)\]', response_text)
        
        for match in matches:
            doc_num = match
            if f"Doc{doc_num}" not in citations:
                citations.append(f"Doc{doc_num}")
                
        return citations
    
    def format_response_with_sources(self, response_text: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Formatea la respuesta final incluyendo fuentes utilizadas
        
        Args:
            response_text: Texto de respuesta generado por GPT
            search_results: Resultados originales de la búsqueda
            
        Returns:
            Diccionario con respuesta y metadatos
        """
        # Extraer citas de documentos usadas en la respuesta
        citations = self.extract_document_citations(response_text)
        
        # Mapear documentos citados
        sources = []
        for i, doc in enumerate(search_results[:len(citations)], 1):
            if f"Doc{i}" in citations:
                sources.append({
                    "id": doc.get("document_id", i),
                    "title": doc.get("title", f"Documento {i}"),
                    "reference": doc.get("reference_number", "N/A"),
                    "relevance": doc.get("relevance_score", 0)
                })
        
        # Construir respuesta final
        formatted_response = {
            "response_text": response_text,
            "sources": sources,
            "metadata": {
                "total_documents": len(search_results),
                "documents_cited": len(sources),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return formatted_response 