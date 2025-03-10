"""
Servicio de Búsqueda
------------------
Este módulo implementa la funcionalidad de búsqueda utilizando BM25
para recuperar documentos legales relevantes.
"""

import re
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from ..models.legal_document import LegalDocument, DocumentType
from ..schemas.legal_document import SearchQuery, LegalDocumentSearchResult, LegalDocumentResponse


# Descargar recursos NLTK necesarios (ejecutar solo una vez)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')


class SearchService:
    """Servicio para realizar búsquedas en documentos legales utilizando BM25"""

    def __init__(self):
        self.stemmer = SnowballStemmer('spanish')
        self.stop_words = set(stopwords.words('spanish'))
        
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
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenizar
        tokens = word_tokenize(text, language='spanish')
        
        # Eliminar stopwords y aplicar stemming
        tokens = [self.stemmer.stem(token) for token in tokens if token not in self.stop_words and len(token) > 2]
        
        return tokens
        
    def search_documents(self, db: Session, search_query: SearchQuery) -> List[LegalDocumentSearchResult]:
        """
        Busca documentos relevantes utilizando BM25.
        
        Args:
            db: Sesión de base de datos
            search_query: Consulta de búsqueda
            
        Returns:
            Lista de documentos relevantes con puntuación
        """
        # Construir la consulta SQLAlchemy
        query = db.query(LegalDocument)
        
        # Aplicar filtros si están presentes
        if search_query.document_type:
            query = query.filter(LegalDocument.document_type == search_query.document_type)
        if search_query.category:
            query = query.filter(LegalDocument.category == search_query.category)
            
        # Obtener todos los documentos (para MVP, en producción habría que paginar)
        documents = query.all()
        
        if not documents:
            return []
            
        # Preprocesar el corpus
        corpus = [self.preprocess_text(doc.content) for doc in documents]
        
        # Crear el índice BM25
        bm25 = BM25Okapi(corpus)
        
        # Preprocesar la consulta
        tokenized_query = self.preprocess_text(search_query.query)
        
        # Obtener puntuaciones
        scores = bm25.get_scores(tokenized_query)
        
        # Crear pares (documento, puntuación) y ordenar por puntuación descendente
        doc_score_pairs = [(doc, score) for doc, score in zip(documents, scores)]
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Limitar los resultados y crear objetos de respuesta
        limit = search_query.limit or 10
        top_results = doc_score_pairs[:limit]
        
        return [
            LegalDocumentSearchResult(
                document=LegalDocumentResponse.from_orm(doc),
                score=score
            )
            for doc, score in top_results if score > 0
        ] 