#!/usr/bin/env python
"""
Script simple para probar el prompt optimizado con una consulta específica.
"""

import os
import sys
import logging
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_prompt")

# Asegurar que el directorio backend esté en el path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar después de configurar el path
try:
    from config import validate_config
    from app.services.ai_service import AIService
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    logger.error("Asegúrate de estar ejecutando el script desde el directorio backend/")
    sys.exit(1)

def test_acoso_laboral():
    """Prueba una consulta sobre acoso laboral"""
    logger.info("Probando consulta sobre acoso laboral")
    
    # Verificar configuración de OpenAI
    if not validate_config():
        logger.error("❌ Configuración de OpenAI inválida. Revisa tu API key.")
        return False
    
    # Crear el servicio de IA
    service = AIService()
    
    # Documentos de prueba 
    test_docs = [
        {
            "document_id": 1,
            "title": "Ley 1010 de 2006 - Ley de Acoso Laboral",
            "reference_number": "1010/2006",
            "document_type": "Ley",
            "content": """
            Por medio de la cual se adoptan medidas para prevenir, corregir y sancionar el acoso laboral y otros hostigamientos en el marco de las relaciones de trabajo.
            
            Artículo 1°. Objeto de la ley y bienes protegidos por ella. La presente ley tiene por objeto definir, prevenir, corregir y sancionar las diversas formas de agresión, maltrato, vejámenes, trato desconsiderado y ofensivo y en general todo ultraje a la dignidad humana que se ejercen sobre quienes realizan sus actividades económicas en el contexto de una relación laboral privada o pública.
            
            Artículo 2°. Definición y modalidades de acoso laboral. Para efectos de la presente ley se entenderá por acoso laboral toda conducta persistente y demostrable, ejercida sobre un empleado, trabajador por parte de un empleador, un jefe o superior jerárquico inmediato o mediato, un compañero de trabajo o un subalterno, encaminada a infundir miedo, intimidación, terror y angustia, a causar perjuicio laboral, generar desmotivación en el trabajo, o inducir la renuncia del mismo.
            """,
            "snippet": "Ley 1010 de 2006: Define el acoso laboral como toda conducta persistente ejercida sobre un empleado para infundir miedo o causar perjuicio laboral.",
            "relevance_score": 0.95
        },
        {
            "document_id": 2,
            "title": "Ley 1010 de 2006 - Mecanismos de protección",
            "reference_number": "1010/2006",
            "document_type": "Ley",
            "content": """
            Artículo 9°. Medidas preventivas y correctivas del acoso laboral.
            1. Los reglamentos de trabajo de las empresas e instituciones deberán prever mecanismos de prevención de las conductas de acoso laboral y establecer un procedimiento interno, confidencial, conciliatorio y efectivo para superar las que ocurran en el lugar de trabajo.
            
            2. La víctima del acoso laboral podrá poner en conocimiento del Inspector de Trabajo con competencia en el lugar de los hechos, de los Inspectores Municipales de Policía, de los Personeros Municipales o de la Defensoría del Pueblo, a prevención, la ocurrencia de una situación continuada y ostensible de acoso laboral.
            """,
            "snippet": "La Ley 1010 establece medidas preventivas y correctivas del acoso laboral, incluyendo mecanismos internos en las empresas y la posibilidad de reportar casos a Inspectores de Trabajo.",
            "relevance_score": 0.92
        }
    ]
    
    # Consulta de prueba
    query = "¿Qué es el acoso laboral y cómo puedo denunciarlo?"
    
    # Generar respuesta
    logger.info(f"Generando respuesta para: '{query}'")
    response, confidence, cited_docs, needs_review = service.generate_legal_response(
        query_text=query,
        search_results=test_docs
    )
    
    # Mostrar resultados
    logger.info("\n" + "=" * 80)
    logger.info("RESPUESTA GENERADA")
    logger.info("=" * 80)
    print("\n" + response + "\n")
    
    logger.info("=" * 80)
    logger.info(f"Confianza: {confidence}")
    logger.info(f"Documentos citados: {len(cited_docs)}")
    logger.info(f"Requiere revisión: {needs_review}")
    
    return True

if __name__ == "__main__":
    if test_acoso_laboral():
        sys.exit(0)
    else:
        sys.exit(1) 