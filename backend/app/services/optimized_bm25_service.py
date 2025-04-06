"""
Servicio Optimizado de Búsqueda BM25
----------------------------------
Este módulo proporciona una implementación optimizada del servicio de búsqueda
BM25 que funciona correctamente con documentos almacenados en la base de datos.
"""

import re
import json
import nltk
import time
import os
import sqlite3
import hashlib
import logging
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import SnowballStemmer
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any, Tuple, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from ..models.legal_document import LegalDocument, DocumentType
from ..schemas.legal_document import SearchQuery, LegalDocumentSearchResult

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bm25_service")

# Descargar recursos NLTK necesarios si no existen
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')


class OptimizedBM25Service:
    """Servicio optimizado para realizar búsquedas BM25 en documentos legales de la base de datos"""

    def __init__(self, 
                 k1: float = 1.5, 
                 b: float = 0.75, 
                 use_cache: bool = True, 
                 cache_expire_time: int = 86400,
                 force_rebuild: bool = False):
        """
        Inicializa el servicio de búsqueda optimizado
        
        Args:
            k1: Parámetro k1 de BM25 (control de saturación de término)
            b: Parámetro b de BM25 (normalización de longitud)
            use_cache: Si se debe usar el sistema de caché
            cache_expire_time: Tiempo de expiración del caché en segundos
            force_rebuild: Forzar la reconstrucción del índice al iniciar
        """
        self.stemmer = SnowballStemmer('spanish')
        self.stop_words = set(stopwords.words('spanish'))
        
        # Palabras adicionales específicas del dominio legal
        self.legal_stop_words = {
            'artículo', 'ley', 'decreto', 'sentencia', 'resolución', 'código', 'norma',
            'legal', 'jurídico', 'judicial', 'tribunal', 'corte', 'suprema', 'constitucional'
        }
        self.stop_words.update(self.legal_stop_words)
        
        # Parámetros de BM25
        self.k1 = k1
        self.b = b
        
        # Sistema de caché
        self.use_cache = use_cache
        self.cache_expire_time = cache_expire_time
        
        if use_cache:
            # Crear directorio para caché si no existe
            cache_dir = Path("cache")
            cache_dir.mkdir(exist_ok=True)
            
            # Inicializar sistema de caché
            self.cache_db_path = str(cache_dir / "bm25_search_cache.db")
            self._initialize_cache_db()
            
        # Estado del índice BM25
        self._bm25_index = None
        self._document_ids = None  # Almacenar IDs de documentos para mapear resultados
        self._corpus = None
        self._last_index_update = None
        self._is_building_index = False
        self._force_rebuild = force_rebuild
        
        logger.info(f"Servicio BM25 optimizado inicializado - Parámetros: k1={k1}, b={b}")
        
    def _initialize_cache_db(self):
        """Inicializa la base de datos de caché si no existe"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        # Crear tabla para caché de consultas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bm25_query_cache (
            query_hash TEXT PRIMARY KEY,
            query_text TEXT NOT NULL,
            results TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Crear índice
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bm25_query_hash ON bm25_query_cache(query_hash)')
        
        conn.commit()
        conn.close()
        
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocesa el texto para la búsqueda:
        1. Convierte a minúsculas
        2. Elimina caracteres especiales
        3. Tokeniza
        4. Elimina stopwords
        5. Aplica stemming
        """
        if not text or not isinstance(text, str):
            return []
            
        # Convertir a minúsculas y eliminar caracteres especiales
        text = text.lower()
        text = re.sub(r'[^\w\sáéíóúüñ]', ' ', text)  # Mantener caracteres acentuados español
        
        # Tokenizar
        tokens = word_tokenize(text, language='spanish')
        
        # Eliminar stopwords y aplicar stemming
        tokens = [self.stemmer.stem(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return tokens
        
    def generate_snippet(self, text: str, query_tokens: List[str], max_length: int = 250) -> str:
        """
        Genera un snippet relevante del texto basado en la consulta.
        
        Args:
            text: Texto completo del documento
            query_tokens: Tokens de la consulta preprocesados
            max_length: Longitud máxima del snippet
            
        Returns:
            Snippet relevante del texto
        """
        if not text or not query_tokens:
            return ""
            
        # Dividir el texto en oraciones
        sentences = sent_tokenize(text, language='spanish')
        
        # Preparar tokens de consulta (sin stemming para buscar coincidencias exactas)
        raw_query_tokens = [token.lower() for token in ' '.join(query_tokens).split()]
        
        # Función para puntuar relevancia de una oración
        def score_sentence(sentence):
            sentence_lower = sentence.lower()
            # Puntuación basada en presencia de tokens de consulta
            score = sum(1 for token in raw_query_tokens if token in sentence_lower)
            # Bonus para oraciones más cortas (más específicas)
            score = score * (1 / (len(sentence.split()) + 1))
            return score
        
        # Puntuar y ordenar oraciones
        scored_sentences = [(sentence, score_sentence(sentence)) for sentence in sentences]
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Seleccionar las mejores oraciones hasta alcanzar la longitud máxima
        snippet = ""
        for sentence, _ in scored_sentences:
            if len(snippet) + len(sentence) + 3 <= max_length:  # 3 por los puntos suspensivos
                if snippet:
                    snippet += " "
                snippet += sentence
            else:
                if not snippet:
                    # Si no hay snippet aún, tomar una parte de la primera oración
                    snippet = sentence[:max_length - 3] + "..."
                break
                
        return snippet if snippet else text[:max_length - 3] + "..."
    
    def _need_reindex(self, db: Session) -> bool:
        """Verifica si es necesario reconstruir el índice BM25"""
        # Si está forzado a reconstruir, siempre reconstruir
        if self._force_rebuild:
            logger.info("Forzando reconstrucción del índice BM25")
            self._force_rebuild = False  # Reset para futuras llamadas
            return True
            
        # Si no hay índice, se necesita crear
        if self._bm25_index is None or self._corpus is None or self._document_ids is None:
            logger.info("El índice BM25 no existe, creando nuevo índice")
            return True
            
        # Si no hay fecha de última actualización, se necesita reconstruir
        if self._last_index_update is None:
            logger.info("No hay fecha de última actualización del índice")
            return True
            
        # Verificar si ha habido cambios en la base de datos desde la última indexación
        try:
            latest_update = db.query(func.max(LegalDocument.updated_at)).scalar()
            
            if latest_update and latest_update > self._last_index_update:
                logger.info(f"Se detectaron cambios en la base de datos: {latest_update} > {self._last_index_update}")
                return True
                
            # Verificar también el número de documentos
            current_count = db.query(func.count(LegalDocument.id)).scalar()
            if current_count != len(self._document_ids):
                logger.info(f"Cambio en el número de documentos: {current_count} ≠ {len(self._document_ids)}")
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error al verificar cambios en la base de datos: {str(e)}")
            return True
        
    def _build_index(self, db: Session) -> bool:
        """
        Construye o reconstruye el índice BM25.
        Retorna True si el índice se construyó correctamente, False en caso contrario.
        """
        if self._is_building_index:
            logger.warning("Ya se está construyendo el índice BM25")
            return False
            
        try:
            self._is_building_index = True
            start_time = time.time()
            logger.info("Construyendo índice BM25...")
            
            # Obtener todos los documentos
            documents = db.query(LegalDocument).all()
            
            if not documents:
                logger.warning("No hay documentos en la base de datos para indexar")
                self._is_building_index = False
                return False
                
            # Almacenar IDs para mapear resultados
            self._document_ids = [doc.id for doc in documents]
            
            # Preprocesar el corpus
            logger.info(f"Preprocesando {len(documents)} documentos para BM25...")
            self._corpus = []
            for doc in documents:
                tokens = self.preprocess_text(doc.content)
                if tokens:  # Ignorar documentos sin contenido válido
                    self._corpus.append(tokens)
                else:
                    logger.warning(f"Documento ID={doc.id} no tiene tokens válidos")
            
            # Verificar que hay documentos válidos
            if not self._corpus:
                logger.error("No hay documentos con contenido válido para indexar")
                self._is_building_index = False
                return False
                
            # Crear el índice BM25 con los parámetros optimizados
            logger.info(f"Creando índice BM25 con {len(self._corpus)} documentos...")
            self._bm25_index = BM25Okapi(self._corpus, k1=self.k1, b=self.b)
            
            # Actualizar la fecha de última indexación
            self._last_index_update = datetime.now()
            
            elapsed_time = time.time() - start_time
            logger.info(f"Índice BM25 construido correctamente en {elapsed_time:.2f} segundos")
            return True
            
        except Exception as e:
            logger.error(f"Error al construir índice BM25: {str(e)}")
            # Reiniciar el estado del índice
            self._bm25_index = None
            self._document_ids = None
            self._corpus = None
            self._last_index_update = None
            return False
            
        finally:
            self._is_building_index = False
            
    def _generate_query_hash(self, search_query: SearchQuery) -> str:
        """Genera un hash único para la consulta"""
        # Convertir la consulta a un string serializable
        query_dict = {
            "query": search_query.query,
            "document_type": search_query.document_type.value if search_query.document_type else None,
            "category": search_query.category,
            "limit": search_query.limit
        }
        
        # Generar hash
        query_str = json.dumps(query_dict, sort_keys=True)
        return hashlib.md5(query_str.encode()).hexdigest()
        
    def _get_from_cache(self, search_query: SearchQuery) -> Optional[List[Dict[str, Any]]]:
        """Obtiene resultados en caché para una consulta"""
        if not self.use_cache:
            return None
            
        query_hash = self._generate_query_hash(search_query)
        
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Buscar en caché y verificar si no ha expirado
            cursor.execute('''
            SELECT results, created_at FROM bm25_query_cache 
            WHERE query_hash = ?
            ''', (query_hash,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                results_json, created_at_str = result
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                
                # Verificar si el caché ha expirado
                if (datetime.now() - created_at).total_seconds() < self.cache_expire_time:
                    logger.info(f"Resultados obtenidos de caché: {search_query.query}")
                    return json.loads(results_json)
                else:
                    logger.info(f"Caché expirado para: {search_query.query}")
        except Exception as e:
            logger.error(f"Error al consultar caché: {str(e)}")
                
        return None
        
    def _save_to_cache(self, search_query: SearchQuery, results: List[Dict[str, Any]]) -> None:
        """Almacena resultados en caché"""
        if not self.use_cache:
            return
            
        try:
            query_hash = self._generate_query_hash(search_query)
            query_text = search_query.query
            results_json = json.dumps(results)
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Almacenar en caché
            cursor.execute('''
            INSERT OR REPLACE INTO bm25_query_cache (query_hash, query_text, results, created_at)
            VALUES (?, ?, ?, ?)
            ''', (query_hash, query_text, results_json, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            logger.info(f"Resultados guardados en caché: {search_query.query}")
        except Exception as e:
            logger.error(f"Error al guardar en caché: {str(e)}")
    
    def search_documents(self, db: Session, search_query: SearchQuery) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes utilizando BM25.
        
        Args:
            db: Sesión de base de datos
            search_query: Consulta de búsqueda
            
        Returns:
            Lista de documentos relevantes con puntuación y snippet
        """
        start_time = time.time()
        
        # Validar la consulta
        if not search_query.query or len(search_query.query.strip()) < 3:
            logger.warning("Consulta demasiado corta")
            return []
        
        # Intentar obtener resultados desde caché
        cached_results = self._get_from_cache(search_query)
        if cached_results:
            # Agregar flag para indicar que es un resultado cacheado
            for result in cached_results:
                result["cached"] = True
            return cached_results
        
        # Verificar e inicializar BM25 si es necesario
        if self._need_reindex(db):
            if not self._build_index(db):
                logger.error("Error al construir índice BM25, no se puede realizar la búsqueda")
                return []
        
        # Preprocesar la consulta
        tokenized_query = self.preprocess_text(search_query.query)
        if not tokenized_query:
            logger.warning(f"La consulta no tiene tokens válidos: {search_query.query}")
            return []
        
        # Lista para almacenar resultados finales
        final_results = []
        
        try:
            # Aplicar filtros
            if search_query.document_type or search_query.category:
                # Buscar IDs de documentos que cumplen los filtros
                query = db.query(LegalDocument.id)
                
                if search_query.document_type:
                    query = query.filter(LegalDocument.document_type == search_query.document_type)
                if search_query.category:
                    query = query.filter(LegalDocument.category == search_query.category)
                
                filtered_ids = set(row[0] for row in query.all())
                
                if not filtered_ids:
                    logger.info("No hay documentos que cumplan los filtros")
                    return []
                
                # Obtener índices y puntuaciones filtradas
                filtered_indices = []
                for idx, doc_id in enumerate(self._document_ids):
                    if doc_id in filtered_ids:
                        filtered_indices.append(idx)
                
                # Si no hay documentos que cumplan los filtros
                if not filtered_indices:
                    logger.info("No hay documentos indexados que cumplan los filtros")
                    return []
                
                # Obtener puntuaciones solo para documentos filtrados
                scores = self._bm25_index.get_scores(tokenized_query)
                
                # Aplicar filtro a puntuaciones
                doc_score_pairs = []
                for idx in filtered_indices:
                    try:
                        doc_score_pairs.append((self._document_ids[idx], scores[idx]))
                    except IndexError:
                        logger.error(f"Error de índice: idx={idx}, len(scores)={len(scores)}, len(doc_ids)={len(self._document_ids)}")
            else:
                # Sin filtros, buscar en todos los documentos
                scores = self._bm25_index.get_scores(tokenized_query)
                
                # Crear pares (documento_id, puntuación)
                doc_score_pairs = [(doc_id, score) for doc_id, score in zip(self._document_ids, scores)]
            
            # Ordenar por puntuación descendente
            doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
            
            # Limitar los resultados
            limit = search_query.limit or 10
            top_pairs = doc_score_pairs[:limit]
            
            # Filtrar resultados sin relevancia
            relevant_pairs = [(doc_id, score) for doc_id, score in top_pairs if score > 0]
            
            if not relevant_pairs:
                logger.info("No se encontraron documentos relevantes")
                return []
            
            # Obtener documentos completos de la base de datos (en una sola consulta)
            doc_ids = [doc_id for doc_id, _ in relevant_pairs]
            documents = {
                doc.id: doc for doc in db.query(LegalDocument).filter(LegalDocument.id.in_(doc_ids)).all()
            }
            
            # Formatear resultados
            for doc_id, score in relevant_pairs:
                if doc_id in documents:
                    doc = documents[doc_id]
                    snippet = self.generate_snippet(doc.content, tokenized_query)
                    
                    result = {
                        "document_id": doc.id,
                        "title": doc.title,
                        "reference_number": doc.reference_number,
                        "document_type": doc.document_type,
                        "relevance_score": round(score, 3),
                        "snippet": snippet,
                        "cached": False
                    }
                    
                    final_results.append(result)
            
            # Almacenar en caché si está habilitado
            if self.use_cache and final_results:
                self._save_to_cache(search_query, final_results)
            
        except Exception as e:
            logger.error(f"Error en búsqueda BM25: {str(e)}")
        
        # Calcular tiempo de procesamiento
        processing_time = time.time() - start_time
        logger.info(f"Búsqueda completada en {processing_time:.2f}s - {len(final_results)} resultados para: {search_query.query}")
        
        return final_results
        
    def index_status(self) -> Dict[str, Any]:
        """Devuelve información sobre el estado del índice BM25"""
        status = {
            "initialized": self._bm25_index is not None,
            "document_count": len(self._document_ids) if self._document_ids else 0,
            "last_update": self._last_index_update.isoformat() if self._last_index_update else None,
            "building_index": self._is_building_index,
            "cache_enabled": self.use_cache,
            "bm25_params": {
                "k1": self.k1,
                "b": self.b
            }
        }
        return status
        
    def force_reindex(self, db: Session) -> bool:
        """Fuerza la reconstrucción del índice"""
        self._force_rebuild = True
        return self._build_index(db) 