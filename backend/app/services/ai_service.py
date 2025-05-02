"""
Servicio de IA para Generación de Respuestas
-----------------------------------------
Este módulo implementa la integración con modelos GPT para generar
respuestas a consultas sobre derecho laboral.

Mejoras implementadas en optimización de prompt:
1. Instrucciones más explícitas sobre usar SOLO información de documentos proporcionados
2. Estructura mejorada para las respuestas legales con secciones claramente definidas
3. Mejor formato para las referencias legales y citaciones
4. Manejo optimizado de casos con información insuficiente
5. Evaluación de confianza más precisa
6. Optimización radical de consumo de tokens y manejo de caché
"""

import os
import json
import re
import time
import logging
import hashlib
from functools import lru_cache
from typing import List, Dict, Any, Optional, Tuple, Union
from openai import OpenAI
from datetime import datetime

import sys
from pathlib import Path
# Asegurar que backend/ esté en sys.path para poder importar el módulo config
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from config import (
    OPENAI_API_KEY, GPT_MODEL, validate_config, 
    ECONOMY_MODE, MAX_TOKENS_OUTPUT, MAX_DOCUMENTS, 
    MAX_CHARS_PER_DOC, ENABLE_CACHE, CACHE_DIR
)
from app.schemas.legal_document import LegalDocumentResponse
from app.schemas.query import QueryResponse, QueryStatus

# Configurar logging
logger = logging.getLogger("ai_service")

# Cache en memoria para respuestas
@lru_cache(maxsize=50)
def get_cached_response(query_hash: str) -> Optional[Dict[str, Any]]:
    """
    Recupera una respuesta desde la caché basada en el hash de la consulta
    
    Args:
        query_hash: Hash MD5 de la consulta
        
    Returns:
        Datos de respuesta cacheados o None si no existe
    """
    try:
        cache_file = os.path.join(CACHE_DIR, f"{query_hash}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✅ Respuesta recuperada de caché: {cache_file}")
                return data
    except Exception as e:
        logger.error(f"❌ Error al leer caché: {str(e)}")
    
    return None

def save_to_cache(query_hash: str, response_data: Dict[str, Any]) -> bool:
    """
    Guarda una respuesta en la caché
    
    Args:
        query_hash: Hash MD5 de la consulta
        response_data: Datos a guardar
        
    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        cache_file = os.path.join(CACHE_DIR, f"{query_hash}.json")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Respuesta guardada en caché: {cache_file}")
        return True
    except Exception as e:
        logger.error(f"❌ Error al guardar en caché: {str(e)}")
        return False

def create_query_hash(query_text: str, search_results: List[Dict[str, Any]]) -> str:
    """
    Crea un hash único para una consulta y sus resultados de búsqueda
    
    Args:
        query_text: Texto de la consulta
        search_results: Resultados de búsqueda (se usa solo IDs y relevancia)
        
    Returns:
        Hash MD5 como string
    """
    # Crear una representación simplificada de los resultados que capture
    # lo esencial pero ignore detalles que no afectan la respuesta
    simplified_results = []
    for doc in search_results[:MAX_DOCUMENTS]:
        simplified_results.append({
            "id": doc.get("id", ""),
            "relevance": doc.get("relevance_score", 0)
        })
    
    # Crear string para hash
    hash_input = f"{query_text}|{json.dumps(simplified_results)}"
    
    # Generar hash
    return hashlib.md5(hash_input.encode('utf-8')).hexdigest()

class AIService:
    """Servicio para generación de respuestas basadas en IA"""

    def __init__(self):
        """Inicializa el cliente de OpenAI y configura el modelo"""
        self.api_key = OPENAI_API_KEY
        self.model = GPT_MODEL
        self.client = None
        self.max_retries = 3
        self.retry_delay = 2  # segundos
        
        # Intentar inicializar el cliente
        self._initialize_client()
        
    def _initialize_client(self) -> bool:
        """
        Inicializa el cliente de OpenAI.
        
        Returns:
            bool: True si la inicialización fue exitosa, False si hubo un error
        """
        if not self.api_key or self.api_key in ["your_openai_api_key_here", "sk-your-actual-openai-api-key"]:
            logger.error("❌ OPENAI_API_KEY no configurada o inválida")
            return False
            
        try:
            self.client = OpenAI(api_key=self.api_key)
            return True
        except Exception as e:
            logger.error(f"❌ Error al inicializar el cliente de OpenAI: {str(e)}")
            return False
    
    def is_api_key_valid(self) -> bool:
        """
        Verifica si la API key es válida haciendo una petición mínima.
        
        Returns:
            bool: True si la API key es válida, False si no lo es
        """
        if not self.client:
            return False
            
        try:
            # Hacer una petición mínima para verificar la API key
            response = self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"❌ Error al verificar la API key: {str(e)}")
            return False
        
    def format_bm25_context(self, query_text: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Formatea los resultados de BM25 en un contexto estructurado y optimizado para GPT.
        
        Args:
            query_text: Texto de la consulta del usuario
            search_results: Lista de documentos relevantes recuperados con BM25
            
        Returns:
            Contexto estructurado como diccionario para enviar a GPT
        """
        # Usar configuración optimizada para ahorrar tokens
        max_docs = MAX_DOCUMENTS
        max_chars = MAX_CHARS_PER_DOC
        
        # Limitar a los más relevantes
        top_results = search_results[:max_docs]
        
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
            
            # Crear documento estructurado con snippet y contenido reducido
            content = doc.get("snippet", "")[:max_chars]
            
            formatted_doc = {
                "id": doc_id,
                "titulo": doc.get("title", "Documento sin título"),
                "referencia": legal_reference,
                "contenido": content
            }
            
            formatted_documents.append(formatted_doc)
        
        # Crear contexto optimizado
        context = {
            "consulta": query_text,
            "documentos": formatted_documents
        }
        
        return context
        
    def generate_gpt_response(
        self, 
        prompt: str, 
        system_message: str, 
        max_tokens: int = MAX_TOKENS_OUTPUT,
        temperature: float = 0.1,  # Reducido para respuestas más concisas
        model: str = None,
        timeout: int = 30  # Reducido a 30 segundos
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Genera una respuesta utilizando la API de OpenAI con manejo de errores y reintentos.
        Optimizado para reducir consumo de tokens.
        
        Args:
            prompt: Prompt para enviar a GPT
            system_message: Mensaje del sistema para establecer el rol
            max_tokens: Número máximo de tokens en la respuesta
            temperature: Temperatura para controlar la creatividad (0-1)
            model: Modelo a utilizar (si es None, se usa el predeterminado)
            timeout: Tiempo máximo de espera para la respuesta en segundos
            
        Returns:
            Tupla con (respuesta, error)
            - Si hay éxito: (respuesta, None)
            - Si hay error: (None, mensaje_error)
        """
        if not self.client:
            if not self._initialize_client():
                return None, "No se pudo inicializar el cliente de OpenAI. Verifica tu API key."
        
        # Usar el modelo especificado o el predeterminado
        model_to_use = model or self.model
        
        # Limpiar y truncar prompts si son muy largos
        if len(prompt) > 4000:  # Reducción drástica de contexto
            logger.warning(f"⚠️ Prompt demasiado largo ({len(prompt)} caracteres). Truncando...")
            prompt = prompt[:4000]
        
        attempts = 0
        while attempts < self.max_retries:
            try:
                logger.info(f"🔄 Enviando solicitud a OpenAI (intento {attempts+1}/{self.max_retries})")
                start_time = time.time()
                
                response = self.client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout
                )
                
                execution_time = time.time() - start_time
                logger.info(f"✅ Respuesta generada en {execution_time:.2f} segundos")
                
                return response.choices[0].message.content.strip(), None
                
            except Exception as e:
                error_str = str(e)
                logger.error(f"❌ Error al generar respuesta: {error_str}")
                
                # Analizar tipo de error
                if "maximum context length" in error_str.lower():
                    # Reducir longitud del prompt aún más
                    prompt = prompt[:len(prompt)//2]
                    logger.warning("⚠️ Reduciendo longitud del prompt para evitar exceder máximo de tokens")
                elif "rate limit" in error_str.lower():
                    # Esperar más tiempo en caso de límite de tasa
                    wait_time = (2 ** attempts) * self.retry_delay
                    logger.warning(f"⚠️ Límite de tasa excedido. Esperando {wait_time} segundos...")
                    time.sleep(wait_time)
                elif "billing hard limit" in error_str.lower() or "quota" in error_str.lower():
                    logger.error("❌ Has excedido tu cuota de API. Verifica tu saldo y límites.")
                    return None, "Cuota de API excedida. Verifica tu saldo y límites en OpenAI."
                else:
                    logger.error(f"❌ Error desconocido: {error_str}")
                    return None, f"Error inesperado: {error_str}"
                
            attempts += 1
            
        return None, f"No se pudo completar la solicitud después de {self.max_retries} intentos."
        
    def generate_response(
        self, 
        query_text: str, 
        search_results: List[Dict[str, Any]],
        threshold: float = 0.7
    ) -> Tuple[str, float, bool, Optional[str]]:
        """
        Genera una respuesta a la consulta del usuario utilizando GPT.
        Versión optimizada para reducir consumo de tokens.
        
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
        # Verificar que la API key es válida
        if not validate_config():
            return (
                "Lo siento, hay un problema con la configuración del sistema. Un especialista revisará tu caso.",
                0.0,
                True,
                "Error de configuración de OpenAI API"
            )
        
        # Verificar caché si está habilitado
        if ENABLE_CACHE:
            query_hash = create_query_hash(query_text, search_results)
            cached_data = get_cached_response(query_hash)
            
            if cached_data:
                return (
                    cached_data["response"],
                    cached_data["confidence"],
                    cached_data["needs_review"],
                    cached_data["review_reason"]
                )
        
        # Si no hay suficientes resultados relevantes, devolver respuesta estándar
        if not search_results or len(search_results) == 0:
            default_response = (
                "No tengo suficiente información en los documentos proporcionados para responder esta consulta de forma completa.\n\n"
                "**REFERENCIAS LEGALES:**\n"
                "- No se encontraron documentos relevantes a tu consulta.\n\n"
                "**CONFIANZA: 0.0**"
            )
            
            if ENABLE_CACHE:
                save_to_cache(query_hash, {
                    "response": default_response,
                    "confidence": 0.0,
                    "needs_review": True,
                    "review_reason": "Sin documentos relevantes"
                })
                
            return default_response, 0.0, True, "Sin documentos relevantes"
            
        # Formatear el contexto de BM25 para GPT (versión optimizada)
        context = self.format_bm25_context(query_text, search_results)
        
        # Optimizar el prompt para GPT (versión ultra concisa)
        system_prompt = """
        Asistente legal colombiano. Responde basándote SOLO en los documentos proporcionados.
        REGLAS: No inventes información. Sé breve y directo. Cita fuentes como [DocX].
        Si no tienes suficiente información, indica: "No tengo suficiente información en los documentos proporcionados".
        ESTRUCTURA: 1) Respuesta directa, 2) Referencias legales.
        Al final evalúa tu confianza (0-1): "CONFIANZA: [puntuación]"
        """
        
        # Convertir contexto a formato JSON simplificado
        context_json = json.dumps(context, ensure_ascii=False)
        
        user_prompt = f"""
        CONSULTA: {query_text}
        
        DOCUMENTOS:
        {context_json}
        
        Responde usando solo estos documentos. Incluye citas [DocX].
        """
        
        # Generar respuesta usando el método con manejo de errores
        response_text, error = self.generate_gpt_response(
            prompt=user_prompt,
            system_message=system_prompt,
            max_tokens=MAX_TOKENS_OUTPUT,
            temperature=0.1
        )
        
        # Si hubo un error, devolver mensaje de error
        if error:
            logger.error(f"❌ Error al generar respuesta: {error}")
            
            error_response = (
                "Lo siento, no pude procesar tu consulta en este momento debido a limitaciones técnicas.\n\n"
                "**CONFIANZA: 0.0**"
            )
            
            return (
                error_response,
                0.0,
                True,
                f"Error en la generación de respuesta: {error}"
            )
        
        # Extraer la puntuación de confianza
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
        
        # Guardar en caché si está habilitado
        if ENABLE_CACHE:
            save_to_cache(query_hash, {
                "response": clean_response,
                "confidence": confidence_score,
                "needs_review": needs_human_review,
                "review_reason": review_reason
            })
        
        return clean_response, confidence_score, needs_human_review, review_reason
    
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
        formatted_text = re.sub(r'\[Doc(\d+)\]', r'[📄 Doc\1]', response_text)
        
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

    def optimize_document_context(self, search_results: List[Dict[str, Any]], 
                                max_documents: int = 5, 
                                max_chars_per_doc: int = 2000) -> List[Dict[str, Any]]:
        """
        Optimiza los documentos para prepararlos para GPT, priorizando la información
        más relevante y eliminando contenido redundante.
        
        Args:
            search_results: Resultados de búsqueda BM25
            max_documents: Número máximo de documentos a incluir
            max_chars_per_doc: Longitud máxima de contenido por documento
            
        Returns:
            Lista de documentos optimizados para enviar a GPT
        """
        if not search_results:
            return []
        
        # Priorizar documentos más relevantes
        top_results = sorted(search_results[:max_documents*2], key=lambda x: float(x.get("relevance_score", 0)), reverse=True)[:max_documents]
        
        # Eliminar documentos duplicados o con contenido muy similar
        seen_content = set()
        unique_docs = []
        
        for doc in top_results:
            # Crear una representación simplificada del contenido para comparación
            content_sample = doc.get("content", "")[:300].lower() if doc.get("content") else ""
            if not content_sample or hash(content_sample) not in seen_content:
                if content_sample:
                    seen_content.add(hash(content_sample))
                unique_docs.append(doc)
        
        # Crear contexto estructurado
        optimized_documents = []
        
        for i, doc in enumerate(unique_docs, 1):
            # Extraer identificadores para citas
            doc_id = f"[Doc{i}]"
            legal_reference = ""
            
            # Determinar tipo de referencia específica basado en document_type
            doc_type = str(doc.get("document_type", "")).lower()
            ref_number = doc.get('reference_number', 'N/A')
            
            if "ley" in doc_type:
                legal_reference = f"Ley {ref_number}"
            elif "decreto" in doc_type:
                legal_reference = f"Decreto {ref_number}"
            elif "sentencia" in doc_type:
                legal_reference = f"Sentencia {ref_number}"
            elif "código" in doc_type or "cst" in doc_type.lower():
                if "art" in ref_number.lower():
                    legal_reference = f"Código Sustantivo del Trabajo, {ref_number}"
                else:
                    legal_reference = f"Código Sustantivo del Trabajo, Artículo {ref_number}"
            elif "resolución" in doc_type:
                legal_reference = f"Resolución {ref_number}"
            elif "circular" in doc_type:
                legal_reference = f"Circular {ref_number}"
            else:
                legal_reference = ref_number
            
            # Limpiar y formatear el contenido
            content = doc.get("content", "").strip()
            if not content:
                content = doc.get("snippet", "").strip()
            
            # Extraer las partes más relevantes del contenido
            if len(content) > max_chars_per_doc:
                # Dividir en párrafos
                paragraphs = [p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]
                
                # Priorizar párrafos con palabras clave relacionadas con la consulta
                # (Esta es una simplificación - en una implementación más completa
                # se podría usar embeddings o similaridad semántica)
                selected_content = []
                chars_count = 0
                
                # Asegurar que el primer párrafo siempre se incluya (a menudo contiene definiciones)
                if paragraphs:
                    first_para = paragraphs[0]
                    selected_content.append(first_para)
                    chars_count += len(first_para)
                
                # Añadir párrafos restantes hasta alcanzar el límite
                for para in paragraphs[1:]:
                    if chars_count + len(para) + 1 <= max_chars_per_doc:
                        selected_content.append(para)
                        chars_count += len(para) + 1  # +1 por el separador
                    else:
                        break
                
                content = "\n\n".join(selected_content)
                if len(content) < len(doc.get("content", "")):
                    content += "..."
            
            # Crear documento estructurado
            optimized_doc = {
                "id": doc_id,
                "titulo": doc.get("title", "Documento sin título"),
                "referencia_legal": legal_reference,
                "tipo_documento": doc.get("document_type", "No especificado"),
                "relevancia": round(float(doc.get("relevance_score", 0)), 3),
                "contenido": content,
                "fuente_completa": doc.get("source", "No especificada"),
                "fecha_documento": doc.get("date", "No especificada")
            }
            
            optimized_documents.append(optimized_doc)
        
        return optimized_documents

    def generate_legal_response(
        self,
        query_text: str,
        search_results: List[Dict[str, Any]],
        max_documents: int = 5,
        max_tokens: int = 1500,
        confidence_threshold: float = 0.7,
        model: str = None,
        timeout: int = 60
    ) -> Tuple[str, float, List[Dict[str, Any]], bool]:
        """
        Genera una respuesta legal detallada a partir de una consulta y resultados de búsqueda BM25.
        
        Este método está optimizado para consultas legales que requieren citación precisa
        de fuentes y alto nivel de precisión.
        
        Args:
            query_text: Consulta del usuario
            search_results: Resultados de búsqueda BM25
            max_documents: Número máximo de documentos a incluir
            max_tokens: Tokens máximos para la respuesta
            confidence_threshold: Umbral para determinar si una respuesta es confiable
            model: Modelo específico a utilizar (si es None, usa el predeterminado)
            timeout: Tiempo máximo de espera para la respuesta en segundos
            
        Returns:
            Tupla con:
            - respuesta_formateada: Texto de la respuesta 
            - puntuación_confianza: Nivel de confianza (0-1)
            - documentos_citados: Lista de documentos usados en la respuesta
            - requiere_revision: Indicador de si la respuesta necesita revisión humana
        """
        if not search_results:
            return "No se encontraron documentos legales relevantes para tu consulta. Por favor, reformula tu pregunta o consulta a un especialista en derecho laboral.", 0.0, [], True
        
        # Verificar cliente OpenAI
        if not self.client and not self._initialize_client():
            logger.error("❌ No se pudo inicializar el cliente de OpenAI")
            return "Lo siento, hay un problema técnico con nuestro servicio. Por favor, intenta más tarde o contacta a un especialista en derecho laboral para tu consulta.", 0.0, [], True
        
        # Optimizar documentos para GPT
        optimized_docs = self.optimize_document_context(
            search_results=search_results,
            max_documents=max_documents
        )
        
        # Formatear documentos para JSON
        formatted_context = {
            "consulta_legal": query_text,
            "documentos_relevantes": optimized_docs,
            "total_documentos": len(search_results),
            "documentos_incluidos": len(optimized_docs),
            "timestamp": datetime.now().isoformat()
        }
        
        # Sistema de prompt optimizado para respuestas legales
        system_prompt = """
        Eres un asistente legal especializado en derecho laboral colombiano con amplia experiencia jurídica.
        Tu ÚNICA función es proporcionar respuestas precisas basadas EXCLUSIVAMENTE en los documentos legales proporcionados.
        
        ## REGLAS FUNDAMENTALES (CRÍTICAS - DEBES SEGUIRLAS SIN EXCEPCIÓN):
        
        1. NUNCA inventes información, leyes, artículos o interpretaciones que NO aparezcan explícitamente en los documentos proporcionados.
        2. NUNCA utilices tu conocimiento general sobre leyes - SOLO puedes usar la información que aparece en los documentos.
        3. Si los documentos proporcionados no contienen información suficiente, DEBES indicarlo claramente.
        4. SIEMPRE cita las fuentes específicas usando el formato [DocX] después de cada afirmación legal importante.
        5. SIEMPRE incluye referencias legales exactas (números de ley, artículos específicos) tal como aparecen en los documentos.
        
        ## ESTRUCTURA OBLIGATORIA DE LA RESPUESTA:
        
        **RESPUESTA DIRECTA**:
        Comienza con una respuesta concisa y directa a la consulta legal.
        
        **FUNDAMENTO LEGAL**:
        Explica detalladamente el fundamento legal citando documentos específicos.
        
        **REQUISITOS Y CONDICIONES** (si aplica):
        Enumera requisitos, plazos o condiciones especiales.
        
        **REFERENCIAS LEGALES**:
        Lista completa de documentos citados con sus referencias legales exactas.
        Ejemplo:
        • [Doc1] Ley 1010 de 2006, Artículo 2 - Definición de acoso laboral
        • [Doc2] Código Sustantivo del Trabajo, Artículo 62 - Terminación del contrato
        
        ## CUANDO NO HAY INFORMACIÓN SUFICIENTE:
        
        Si la información proporcionada es insuficiente para responder adecuadamente:
        1. Indica específicamente qué información falta para responder completamente
        2. Proporciona la información parcial que SÍ está disponible en los documentos
        3. Asigna una puntuación de confianza baja (0.0-0.3)
        4. Incluye este texto exacto al inicio: "ADVERTENCIA: La información disponible es limitada para responder completamente a esta consulta."
        
        ## EVALUACIÓN DE CONFIANZA:
        
        Al final de tu respuesta, evalúa tu confianza en una escala de 0 a 1:
        - 0.0-0.3: Información muy insuficiente o no relevante
        - 0.4-0.6: Información parcial con algunas lagunas importantes
        - 0.7-0.9: Información suficiente con documentos relevantes
        - 1.0: Información completa y precisa con documentos altamente relevantes
        
        Al final, DEBES incluir tu evaluación en el siguiente formato exacto:
        "CONFIANZA: [puntuación]"
        """
        
        # Convertir contexto a formato JSON con indentación para mejor legibilidad
        context_json = json.dumps(formatted_context, ensure_ascii=False, indent=2)
        
        # Crear prompt con instrucciones detalladas
        user_prompt = f"""
        ## CONSULTA LEGAL
        
        {query_text}
        
        ## DOCUMENTOS LEGALES RELEVANTES
        
        {context_json}
        
        ## INSTRUCCIONES ESPECÍFICAS
        
        IMPORTANTE:
        - Responde basándote ÚNICAMENTE en los documentos proporcionados.
        - Si no encuentras información suficiente, indícalo claramente.
        - Cita las fuentes exactas para cada afirmación legal.
        - Utiliza un lenguaje claro y accesible para personas sin formación jurídica.
        - Estructura tu respuesta según el formato requerido.
        - Incluye la sección "REFERENCIAS LEGALES" con todas las fuentes utilizadas.
        
        Recuerda evaluar la confianza de tu respuesta al final.
        """
        
        # Generar respuesta usando el método con manejo de errores
        model_to_use = model or self.model
        response_text, error = self.generate_gpt_response(
            prompt=user_prompt,
            system_message=system_prompt,
            max_tokens=max_tokens,
            temperature=0.1,  # Temperatura más baja para respuestas más deterministas
            model=model_to_use,
            timeout=timeout
        )
        
        # Si hubo un error, devolver mensaje de error
        if error:
            logger.error(f"❌ Error al generar respuesta legal: {error}")
            return (
                f"Lo siento, no pude procesar tu consulta legal en este momento debido a un error técnico. Por favor, intenta nuevamente más tarde o consulta a un especialista en derecho laboral.",
                0.0,
                [],
                True
            )
        
        # Extraer la puntuación de confianza
        confidence_score = self._extract_confidence_score(response_text)
        
        # Limpiar la respuesta y formatear referencias
        clean_response = self._clean_response(response_text)
        formatted_response = self._format_enhanced_legal_references(clean_response)
        
        # Determinar si requiere revisión humana
        requires_human_review = confidence_score < confidence_threshold
        
        # Extraer documentos citados
        citations = self.extract_document_citations(formatted_response)
        cited_documents = []
        
        for i, doc in enumerate(optimized_docs, 1):
            doc_id = f"Doc{i}"
            if doc_id in citations:
                cite_index = next((idx for idx, res in enumerate(search_results) 
                                if res.get("title") == doc.get("titulo")), None)
                
                if cite_index is not None:
                    original_doc = search_results[cite_index]
                    cited_documents.append({
                        "id": original_doc.get("document_id", i),
                        "title": original_doc.get("title", f"Documento {i}"),
                        "reference": original_doc.get("reference_number", "N/A"),
                        "relevance": original_doc.get("relevance_score", 0)
                    })
        
        # Si la confianza es muy baja, agregar disclaimer
        if confidence_score < 0.4:
            formatted_response = self._add_low_confidence_disclaimer(formatted_response)
        
        return formatted_response, confidence_score, cited_documents, requires_human_review

    def _format_enhanced_legal_references(self, response_text: str) -> str:
        """
        Mejora el formato de las referencias legales para mayor claridad y consistencia.
        
        Args:
            response_text: Texto de la respuesta generada
            
        Returns:
            Texto con referencias legales reformateadas
        """
        # Destacar referencias a documentos
        formatted_text = re.sub(r'\[Doc(\d+)\]', r'[📄 Doc\1]', response_text)
        
        # Destacar referencias a artículos
        formatted_text = re.sub(
            r'(?i)(artículo|art\.|art)\s+(\d+[a-z]?)(\s+del\s+(?:código|cst|ley|decreto))?', 
            r'**Artículo \2\3**', 
            formatted_text
        )
        
        # Destacar referencias a leyes
        formatted_text = re.sub(
            r'(?i)(ley)\s+(\d+)(\s+de\s+\d{4})?', 
            r'**Ley \2\3**', 
            formatted_text
        )
        
        # Destacar referencias a decretos
        formatted_text = re.sub(
            r'(?i)(decreto)\s+(\d+)(\s+de\s+\d{4})?', 
            r'**Decreto \2\3**', 
            formatted_text
        )
        
        # Destacar referencias a sentencias
        formatted_text = re.sub(
            r'(?i)(sentencia)\s+([a-z]-\d+)(\s+de\s+\d{4})?', 
            r'**Sentencia \2\3**', 
            formatted_text
        )
        
        # Formatear sección de referencias legales
        if "REFERENCIAS LEGALES" in formatted_text or "Referencias Legales" in formatted_text:
            # Buscar la sección de referencias legales usando regex
            pattern = r'(?:REFERENCIAS LEGALES|Referencias Legales)[:\s]*\n((?:.+\n)+)'
            match = re.search(pattern, formatted_text)
            
            if match:
                ref_section = match.group(0)
                formatted_ref_section = ref_section
                
                # Reformatear cada línea de la sección
                lines = ref_section.split('\n')
                formatted_lines = ["## " + lines[0].strip()]  # Destacar el título
                
                for line in lines[1:]:
                    if line.strip():
                        # Mejorar el formato de cada referencia
                        formatted_line = re.sub(r'^\s*-?\s*', '• ', line)
                        formatted_line = re.sub(r'\[Doc(\d+)\]', r'[📄 Doc\1]', formatted_line)
                        formatted_lines.append(formatted_line)
                
                formatted_ref_section = '\n'.join(formatted_lines)
                formatted_text = formatted_text.replace(ref_section, formatted_ref_section)
        
        return formatted_text

    def _add_low_confidence_disclaimer(self, response_text: str) -> str:
        """
        Agrega un disclaimer a respuestas con baja confianza.
        
        Args:
            response_text: Texto de la respuesta generada
            
        Returns:
            Texto con disclaimer agregado
        """
        disclaimer = """
⚠️ **ADVERTENCIA IMPORTANTE**: Esta respuesta se basa en información limitada o parcial encontrada en los documentos disponibles. 
Es posible que no represente una orientación legal completa. Para obtener asesoramiento legal preciso y adaptado a su situación específica, 
se recomienda consultar a un profesional especializado en derecho laboral.
"""
        
        return disclaimer + "\n\n" + response_text 