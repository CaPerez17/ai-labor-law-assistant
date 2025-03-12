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
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import SnowballStemmer
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any, Tuple, Optional
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
        # Palabras adicionales específicas del dominio legal que no son relevantes para la búsqueda
        self.legal_stop_words = {
            'artículo', 'ley', 'decreto', 'sentencia', 'resolución', 'código', 'norma',
            'legal', 'jurídico', 'judicial', 'tribunal', 'corte', 'suprema', 'constitucional'
        }
        self.stop_words.update(self.legal_stop_words)
        
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
        
    def search_documents(self, db: Session, search_query: SearchQuery) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes utilizando BM25.
        
        Args:
            db: Sesión de base de datos
            search_query: Consulta de búsqueda
            
        Returns:
            Lista de documentos relevantes con puntuación y snippet
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
                    "snippet": snippet
                }
                formatted_results.append(result)
                
        return formatted_results 