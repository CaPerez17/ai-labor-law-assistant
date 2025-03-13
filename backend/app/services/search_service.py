"""
Servicio de Búsqueda
------------------
Este módulo implementa la funcionalidad de búsqueda utilizando BM25
para recuperar documentos legales relevantes.
"""

import re
import json
import nltk
import time
import os
import sqlite3
import hashlib
import random
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
from ..schemas.legal_document import SearchQuery, LegalDocumentSearchResult, LegalDocumentResponse


# Descargar recursos NLTK necesarios (ejecutar solo una vez)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')


class QueryCache:
    """Clase para implementar caché de consultas usando SQLite"""
    
    def __init__(self, cache_db_path="cache.db", expire_time=86400):
        """
        Inicializa el sistema de caché
        
        Args:
            cache_db_path: Ruta al archivo SQLite de caché
            expire_time: Tiempo de expiración en segundos (default: 24 horas)
        """
        self.cache_db_path = cache_db_path
        self.expire_time = expire_time
        self._initialize_db()
        
    def _initialize_db(self):
        """Inicializa la base de datos de caché si no existe"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        # Crear tabla para caché de consultas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_cache (
            query_hash TEXT PRIMARY KEY,
            query_text TEXT NOT NULL,
            results TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Crear índice
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_query_hash ON query_cache(query_hash)')
        
        conn.commit()
        conn.close()
        
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
        
    def get(self, search_query: SearchQuery) -> Optional[List[Dict[str, Any]]]:
        """Obtiene resultados en caché para una consulta"""
        query_hash = self._generate_query_hash(search_query)
        
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        # Buscar en caché y verificar si no ha expirado
        cursor.execute('''
        SELECT results, created_at FROM query_cache 
        WHERE query_hash = ?
        ''', (query_hash,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            results_json, created_at_str = result
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            
            # Verificar si el caché ha expirado
            if (datetime.now() - created_at).total_seconds() < self.expire_time:
                return json.loads(results_json)
                
        return None
        
    def set(self, search_query: SearchQuery, results: List[Dict[str, Any]]) -> None:
        """Almacena resultados en caché"""
        query_hash = self._generate_query_hash(search_query)
        query_text = search_query.query
        results_json = json.dumps(results)
        
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        # Almacenar en caché
        cursor.execute('''
        INSERT OR REPLACE INTO query_cache (query_hash, query_text, results, created_at)
        VALUES (?, ?, ?, ?)
        ''', (query_hash, query_text, results_json, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
    def clear_expired(self) -> int:
        """Elimina entradas expiradas del caché y retorna la cantidad eliminada"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        # Calcular tiempo de expiración
        expire_timestamp = (datetime.now() - timedelta(seconds=self.expire_time)).isoformat()
        
        # Eliminar entradas expiradas
        cursor.execute('''
        DELETE FROM query_cache WHERE created_at < ?
        ''', (expire_timestamp,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count


class SearchService:
    """Servicio para realizar búsquedas en documentos legales utilizando BM25"""

    def __init__(self, 
                 k1: float = 1.5, 
                 b: float = 0.75, 
                 use_cache: bool = True, 
                 cache_expire_time: int = 86400):
        """
        Inicializa el servicio de búsqueda
        
        Args:
            k1: Parámetro k1 de BM25 (control de saturación de término)
            b: Parámetro b de BM25 (normalización de longitud)
            use_cache: Si se debe usar el sistema de caché
            cache_expire_time: Tiempo de expiración del caché en segundos
        """
        self.stemmer = SnowballStemmer('spanish')
        self.stop_words = set(stopwords.words('spanish'))
        # Palabras adicionales específicas del dominio legal que no son relevantes para la búsqueda
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
        if use_cache:
            # Crear directorio para caché si no existe
            cache_dir = Path("cache")
            cache_dir.mkdir(exist_ok=True)
            
            # Inicializar sistema de caché
            self.cache = QueryCache(
                cache_db_path=str(cache_dir / "search_cache.db"),
                expire_time=cache_expire_time
            )
            
        # Mantener el índice BM25 en memoria
        self._bm25_index = None
        self._corpus = None
        self._corpus_documents = None
        self._last_index_update = None
        
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocesa el texto para la búsqueda:
        1. Convierte a minúsculas
        2. Elimina caracteres especiales
        3. Tokeniza
        4. Elimina stopwords
        5. Aplica stemming
        """
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
        # Si no hay índice, se necesita crear
        if self._bm25_index is None or self._corpus is None or self._corpus_documents is None:
            return True
            
        # Si no hay fecha de última actualización, se necesita reconstruir
        if self._last_index_update is None:
            return True
            
        # Verificar si ha habido cambios en la base de datos desde la última indexación
        latest_update = db.query(func.max(LegalDocument.updated_at)).scalar()
        
        if latest_update and latest_update > self._last_index_update:
            return True
            
        return False
        
    def _build_index(self, db: Session) -> None:
        """Construye o reconstruye el índice BM25"""
        # Obtener todos los documentos
        self._corpus_documents = db.query(LegalDocument).all()
        
        # Preprocesar el corpus
        self._corpus = [self.preprocess_text(doc.content) for doc in self._corpus_documents]
        
        # Crear el índice BM25 con los parámetros optimizados
        self._bm25_index = BM25Okapi(self._corpus, k1=self.k1, b=self.b)
        
        # Actualizar la fecha de última indexación
        self._last_index_update = datetime.now()
        
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
        
        # Intentar obtener resultados desde caché
        if self.use_cache:
            cached_results = self.cache.get(search_query)
            if cached_results:
                # Agregar flag para indicar que es un resultado cacheado
                for result in cached_results:
                    result["cached"] = True
                return cached_results
        
        # Construir la consulta SQLAlchemy
        query = db.query(LegalDocument)
        
        # Aplicar filtros si están presentes
        if search_query.document_type:
            query = query.filter(LegalDocument.document_type == search_query.document_type)
        if search_query.category:
            query = query.filter(LegalDocument.category == search_query.category)
            
        # Verificar si hay filtros específicos que requieren consulta directa a la base de datos
        use_filtered_query = search_query.document_type is not None or search_query.category is not None
        
        if use_filtered_query:
            # Obtener documentos filtrados de la base de datos
            documents = query.all()
            
            if not documents:
                return []
                
            # Preprocesar el corpus filtrado
            corpus = [self.preprocess_text(doc.content) for doc in documents]
            
            # Crear el índice BM25 específico para estos documentos
            bm25 = BM25Okapi(corpus, k1=self.k1, b=self.b)
            
            # Preprocesar la consulta
            tokenized_query = self.preprocess_text(search_query.query)
            
            # Obtener puntuaciones
            scores = bm25.get_scores(tokenized_query)
        else:
            # Usar el índice BM25 precompilado si está disponible y actualizado
            if self._need_reindex(db):
                self._build_index(db)
                
            # Usar documentos e índice en memoria
            documents = self._corpus_documents
            
            if not documents:
                return []
                
            # Preprocesar la consulta
            tokenized_query = self.preprocess_text(search_query.query)
            
            # Obtener puntuaciones usando el índice en memoria
            scores = self._bm25_index.get_scores(tokenized_query)
        
        # Crear pares (documento, puntuación) y ordenar por puntuación descendente
        doc_score_pairs = [(doc, score) for doc, score in zip(documents, scores)]
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Limitar los resultados y crear objetos de respuesta
        limit = search_query.limit or 10
        top_results = doc_score_pairs[:limit]
        
        # Formatear resultados con el formato requerido
        formatted_results = []
        for doc, score in top_results:
            if score > 0:  # Solo incluir resultados con alguna relevancia
                snippet = self.generate_snippet(doc.content, tokenized_query)
                result = {
                    "document_id": doc.id,
                    "title": doc.title,
                    "reference_number": doc.reference_number,
                    "document_type": doc.document_type,
                    "relevance_score": round(score, 3),
                    "snippet": snippet,
                    "cached": False  # Indicar que no es un resultado cacheado
                }
                formatted_results.append(result)
        
        # Almacenar en caché si está habilitado
        if self.use_cache and formatted_results:
            self.cache.set(search_query, formatted_results)
            
        # Limpiar entradas expiradas del caché de forma asíncrona 
        # (en una aplicación de producción, esto se haría en un worker separado)
        if self.use_cache and random.random() < 0.05:  # ~5% de las veces
            self.cache.clear_expired()
            
        # Calcular tiempo de procesamiento para optimización
        processing_time = time.time() - start_time
                
        return formatted_results