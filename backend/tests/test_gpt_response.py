#!/usr/bin/env python
"""
Script de prueba para el servicio de IA (generate_gpt_response y generate_legal_response)

Este script prueba la generación de respuestas legales utilizando OpenAI
con documentos simulados relacionados con derecho laboral.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_gpt")

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

# Documentos de prueba simulados para derecho laboral
def create_test_documents() -> List[Dict[str, Any]]:
    """Crea documentos de prueba relacionados con licencias de maternidad"""
    return [
        {
            "document_id": 1,
            "title": "Código Sustantivo del Trabajo - Artículo 236",
            "reference_number": "CST-Art.236",
            "document_type": "Código",
            "content": """
            ARTÍCULO 236. LICENCIA EN LA ÉPOCA DEL PARTO E INCENTIVOS PARA LA ADECUADA ATENCIÓN Y CUIDADO DEL RECIÉN NACIDO. 
            
            1. Toda trabajadora en estado de embarazo tiene derecho a una licencia de dieciocho (18) semanas en la época de parto, remunerada con el salario que devengue al momento de iniciar su licencia.
            
            2. Si se tratare de un salario que no sea fijo como en el caso del trabajo a destajo o por tarea, se tomará en cuenta el salario promedio devengado por la trabajadora en el último año de servicio, o en todo el tiempo si fuere menor.
            
            3. Para los efectos de la licencia de que trata este artículo, la trabajadora debe presentar al empleador un certificado médico, en el cual debe constar:
               a) El estado de embarazo de la trabajadora;
               b) La indicación del día probable del parto, y
               c) La indicación del día desde el cual debe empezar la licencia, teniendo en cuenta que, por lo menos, ha de iniciarse dos semanas antes del parto.
            
            Los beneficios incluidos en este artículo, y el artículo 239 de la presente ley, no excluyen a los trabajadores del sector público.
            """,
            "snippet": "ARTÍCULO 236. LICENCIA EN LA ÉPOCA DEL PARTO: Toda trabajadora en estado de embarazo tiene derecho a una licencia de dieciocho (18) semanas en la época de parto, remunerada con el salario que devengue al momento de iniciar su licencia.",
            "relevance_score": 0.95
        },
        {
            "document_id": 2,
            "title": "Ley 1822 de 2017",
            "reference_number": "Ley-1822/2017",
            "document_type": "Ley",
            "content": """
            Por medio de la cual se incentiva la adecuada atención y cuidado de la primera infancia, se modifican los artículos 236 y 239 del Código Sustantivo del Trabajo y se dictan otras disposiciones.
            
            Artículo 1°. El artículo 236 del Código Sustantivo del Trabajo quedará así:
            Artículo 236. Licencia en la época del parto e incentivos para la adecuada atención y cuidado del recién nacido.
            
            1. Toda trabajadora en estado de embarazo tiene derecho a una licencia de dieciocho (18) semanas en la época de parto, remunerada con el salario que devengue al momento de iniciar su licencia.
            
            2. Si se tratare de un salario que no sea fijo como en el caso del trabajo a destajo o por tarea, se tomará en cuenta el salario promedio devengado por la trabajadora en el último año de servicio, o en todo el tiempo si fuere menor.
            
            3. Para los efectos de la licencia de que trata este artículo, la trabajadora debe presentar al empleador un certificado médico, en el cual debe constar:
               a) El estado de embarazo de la trabajadora;
               b) La indicación del día probable del parto, y
               c) La indicación del día desde el cual debe empezar la licencia, teniendo en cuenta que, por lo menos, ha de iniciarse dos semanas antes del parto.
            """,
            "snippet": "Ley 1822 de 2017 - Por medio de la cual se incentiva la adecuada atención y cuidado de la primera infancia, se modifican los artículos 236 y 239 del CST. Toda trabajadora tiene derecho a una licencia de 18 semanas en la época del parto.",
            "relevance_score": 0.92
        },
        {
            "document_id": 3,
            "title": "Sentencia T-126 de 2012",
            "reference_number": "SentT-126/2012",
            "document_type": "Sentencia",
            "content": """
            LICENCIA DE MATERNIDAD-Naturaleza y finalidad
            
            La licencia de maternidad es una prestación social que consiste en el reconocimiento que la seguridad social le hace a la madre trabajadora cuando se encuentra frente a la maternidad. Esta prestación ha sido establecida y regulada legalmente por el poder legislativo, que ha previsto su otorgamiento como una forma de retribuir y equilibrar el aporte que los ciudadanos le hacen a la sociedad y al Estado, por medio de su trabajo, sus aportes tributarios y parafiscales, así como a través de las contribuciones que hacen al sistema de seguridad social.
            
            El objetivo principal de la licencia de maternidad es garantizar a la madre el descanso necesario para poder reponerse del parto y prodigarle al recién nacido las atenciones que requiere. El descanso se acompaña del pago del salario, pues se parte del supuesto de que si la madre no recibe remuneración no podría satisfacer las necesidades del menor, se afectaría su propia subsistencia, y ello implicaría una vulneración a su derecho a la dignidad humana.
            """,
            "snippet": "LICENCIA DE MATERNIDAD-Naturaleza y finalidad: La licencia de maternidad es una prestación social que consiste en el reconocimiento que la seguridad social le hace a la madre trabajadora. Su objetivo principal es garantizar a la madre el descanso necesario.",
            "relevance_score": 0.85
        },
        {
            "document_id": 4,
            "title": "Decreto 1072 de 2015",
            "reference_number": "Decreto-1072/2015",
            "document_type": "Decreto",
            "content": """
            ARTÍCULO 2.2.1.1.2.1. Acumulación de días de descanso obligatorio remunerado. Cuando las festividades indicadas en el artículo 1º de la Ley 51 de 1983 coincidan en día martes, miércoles o jueves, los trabajadores a los que se aplica esta norma, solo están obligados a laborar el sábado siguiente para compensar el descanso correspondiente a dicha festividad.
            
            ARTÍCULO 2.2.1.1.3. Término y modalidades del contrato de trabajo. Pueden celebrarse por tiempo determinado, por el tiempo que dure la realización de una obra o labor determinada, por tiempo indefinido o para ejecutar un trabajo ocasional, accidental o transitorio.
            
            ARTÍCULO 2.2.1.1.4. Renovación automática contratos a término fijo inferior a un año. Los contratos de trabajo cuya duración sea inferior a un (1) año y que sean renovados por tres (3) veces o más, se entenderán renovados, la última vez, por un (1) año.
            """,
            "snippet": "ARTÍCULO 2.2.1.1.2.1. Acumulación de días de descanso obligatorio remunerado. ARTÍCULO 2.2.1.1.3. Término y modalidades del contrato de trabajo. ARTÍCULO 2.2.1.1.4. Renovación automática contratos a término fijo inferior a un año.",
            "relevance_score": 0.45
        },
        {
            "document_id": 5,
            "title": "Ley 1468 de 2011",
            "reference_number": "Ley-1468/2011",
            "document_type": "Ley",
            "content": """
            Artículo 1°. El artículo 236 del Código Sustantivo del Trabajo quedará así:
            
            Artículo 236. Descanso remunerado en la época del parto:
            
            1. Toda trabajadora en estado de embarazo tiene derecho a una licencia de catorce (14) semanas en la época de parto, remunerada con el salario que devengue al entrar a disfrutar del descanso.
            
            2. Si se tratare de un salario que no sea fijo, como en el caso del trabajo a destajo o por tarea, se toma en cuenta el salario promedio devengado por la trabajadora en el último año de servicios, o en todo el tiempo si fuere menor.
            
            3. Para los efectos de la licencia de que trata este artículo, la trabajadora debe presentar al empleador un certificado médico, en el cual debe constar:
            
            a) El estado de embarazo de la trabajadora;
            b) La indicación del día probable del parto, y
            c) La indicación del día desde el cual debe empezar la licencia, teniendo en cuenta que, por lo menos, ha de iniciarse dos semanas antes del parto.
            """,
            "snippet": "Ley 1468 de 2011: Toda trabajadora en estado de embarazo tiene derecho a una licencia de catorce (14) semanas en la época de parto, remunerada con el salario que devengue al entrar a disfrutar del descanso.",
            "relevance_score": 0.78
        }
    ]

def test_simple_gpt_response():
    """Prueba la función generate_gpt_response con un prompt simple"""
    logger.info("🧪 Probando generate_gpt_response con prompt simple")
    
    # Verificar configuración
    if not validate_config():
        logger.error("❌ Configuración de OpenAI inválida. No se puede continuar.")
        return False
    
    # Inicializar el servicio
    ai_service = AIService()
    
    # Prompt de prueba simple
    system_message = "Eres un asistente legal especializado en derecho laboral colombiano."
    user_prompt = "Explica brevemente qué es una licencia de maternidad según la legislación colombiana."
    
    # Generar respuesta
    logger.info("📤 Enviando prompt a OpenAI...")
    response, error = ai_service.generate_gpt_response(
        prompt=user_prompt,
        system_message=system_message,
        max_tokens=300,
        temperature=0.3
    )
    
    if error:
        logger.error(f"❌ Error al generar respuesta: {error}")
        return False
    
    logger.info("✅ Respuesta generada correctamente:")
    logger.info("-" * 80)
    logger.info(response[:500] + "..." if len(response) > 500 else response)
    logger.info("-" * 80)
    
    return True

def test_legal_response():
    """Prueba la función generate_legal_response con documentos simulados"""
    logger.info("🧪 Probando generate_legal_response con documentos simulados")
    
    # Verificar configuración
    if not validate_config():
        logger.error("❌ Configuración de OpenAI inválida. No se puede continuar.")
        return False
    
    # Inicializar el servicio
    ai_service = AIService()
    
    # Crear documentos de prueba
    test_docs = create_test_documents()
    
    # Consulta de prueba
    query = "¿Cuántas semanas de licencia de maternidad me corresponden según la ley colombiana y qué requisitos debo cumplir?"
    
    # Generar respuesta legal
    logger.info(f"📤 Generando respuesta legal para: '{query}'")
    response, confidence, cited_docs, requires_review = ai_service.generate_legal_response(
        query_text=query,
        search_results=test_docs,
        max_documents=4
    )
    
    logger.info("✅ Respuesta legal generada correctamente:")
    logger.info("-" * 80)
    logger.info(response[:800] + "..." if len(response) > 800 else response)
    logger.info("-" * 80)
    logger.info(f"📊 Puntuación de confianza: {confidence:.2f}")
    
    logger.info("📚 Documentos citados:")
    for doc in cited_docs:
        logger.info(f"  - {doc.get('title', 'Sin título')} (Relevancia: {doc.get('relevance', 0):.2f})")
    
    logger.info(f"👁️ Requiere revisión humana: {requires_review}")
    
    return True

def run_all_tests():
    """Ejecuta todas las pruebas disponibles"""
    logger.info("🔍 Iniciando pruebas del servicio de IA")
    logger.info("=" * 80)
    
    tests = [
        ("Respuesta GPT simple", test_simple_gpt_response),
        ("Respuesta legal con documentos", test_legal_response)
    ]
    
    results = []
    
    for name, test_func in tests:
        logger.info(f"\n🧪 Ejecutando prueba: {name}")
        logger.info("-" * 80)
        
        success = test_func()
        results.append((name, success))
        
        if success:
            logger.info(f"✅ Prueba '{name}' completada con éxito")
        else:
            logger.error(f"❌ Prueba '{name}' falló")
    
    # Mostrar resumen
    logger.info("\n" + "=" * 80)
    logger.info("📋 RESUMEN DE PRUEBAS")
    logger.info("=" * 80)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        if not result:
            all_passed = False
        logger.info(f"{status} - {name}")
    
    logger.info("=" * 80)
    if all_passed:
        logger.info("🎉 Todas las pruebas pasaron correctamente")
    else:
        logger.error("⚠️ Algunas pruebas fallaron")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 