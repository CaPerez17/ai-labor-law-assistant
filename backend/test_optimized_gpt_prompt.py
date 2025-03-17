#!/usr/bin/env python
"""
Script para probar las optimizaciones del prompt y respuestas legales

Este script prueba las mejoras implementadas en el prompt de GPT-4 para
generar respuestas legales precisas, estructuradas y con referencias completas.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import time

# Configurar logging
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

# Documentos de prueba para casos laborales
def create_test_documents() -> List[Dict[str, Any]]:
    """Crea documentos de prueba sobre acoso laboral"""
    return [
        {
            "document_id": 1,
            "title": "Ley 1010 de 2006 - Ley de Acoso Laboral",
            "reference_number": "Ley-1010/2006",
            "document_type": "Ley",
            "content": """
            Por medio de la cual se adoptan medidas para prevenir, corregir y sancionar el acoso laboral y otros hostigamientos en el marco de las relaciones de trabajo.
            
            Artículo 1°. Objeto de la ley y bienes protegidos por ella. La presente ley tiene por objeto definir, prevenir, corregir y sancionar las diversas formas de agresión, maltrato, vejámenes, trato desconsiderado y ofensivo y en general todo ultraje a la dignidad humana que se ejercen sobre quienes realizan sus actividades económicas en el contexto de una relación laboral privada o pública.
            
            Artículo 2°. Definición y modalidades de acoso laboral. Para efectos de la presente ley se entenderá por acoso laboral toda conducta persistente y demostrable, ejercida sobre un empleado, trabajador por parte de un empleador, un jefe o superior jerárquico inmediato o mediato, un compañero de trabajo o un subalterno, encaminada a infundir miedo, intimidación, terror y angustia, a causar perjuicio laboral, generar desmotivación en el trabajo, o inducir la renuncia del mismo.
            
            Artículo 7°. Conductas que constituyen acoso laboral. Se presumirá que hay acoso laboral si se acredita la ocurrencia repetida y pública de cualquiera de las siguientes conductas:
            a) Los actos de agresión física, independientemente de sus consecuencias;
            b) Las expresiones injuriosas o ultrajantes sobre la persona, con utilización de palabras soeces o con alusión a la raza, el género, el origen familiar o nacional, la preferencia política o el estatus social;
            c) Los comentarios hostiles y humillantes de descalificación profesional expresados en presencia de los compañeros de trabajo;
            d) Las injustificadas amenazas de despido expresadas en presencia de los compañeros de trabajo;
            e) Las múltiples denuncias disciplinarias de cualquiera de los sujetos activos del acoso, cuya temeridad quede demostrada por el resultado de los respectivos procesos disciplinarios;
            f) La descalificación humillante y en presencia de los compañeros de trabajo de las propuestas u opiniones de trabajo;
            g) Las burlas sobre la apariencia física o la forma de vestir, formuladas en público;
            h) La alusión pública a hechos pertenecientes a la intimidad de la persona;
            """,
            "snippet": "Ley 1010 de 2006: Define, previene y sanciona el acoso laboral. Artículo 2°: Acoso laboral es toda conducta persistente ejercida sobre un empleado, encaminada a infundir miedo, causar perjuicio laboral o inducir la renuncia.",
            "relevance_score": 0.95
        },
        {
            "document_id": 2,
            "title": "Ley 1010 de 2006 - Mecanismos de protección",
            "reference_number": "Ley-1010/2006",
            "document_type": "Ley",
            "content": """
            Artículo 9°. Medidas preventivas y correctivas del acoso laboral.
            1. Los reglamentos de trabajo de las empresas e instituciones deberán prever mecanismos de prevención de las conductas de acoso laboral y establecer un procedimiento interno, confidencial, conciliatorio y efectivo para superar las que ocurran en el lugar de trabajo.
            
            2. La víctima del acoso laboral podrá poner en conocimiento del Inspector de Trabajo con competencia en el lugar de los hechos, de los Inspectores Municipales de Policía, de los Personeros Municipales o de la Defensoría del Pueblo, a prevención, la ocurrencia de una situación continuada y ostensible de acoso laboral.
            
            Artículo 10. Tratamiento sancionatorio al acoso laboral. El acoso laboral, cuando estuviere debidamente acreditado, se sancionará así:
            1. Como terminación del contrato de trabajo sin justa causa, cuando haya dado lugar a la renuncia o el abandono del trabajo por parte del trabajador regido por el Código Sustantivo del Trabajo. En tal caso procede la indemnización en los términos del artículo 64 del Código Sustantivo del Trabajo.
            2. Con sanción de multa entre dos (2) y diez (10) salarios mínimos legales mensuales para la persona que lo realice y para el empleador que lo tolere.
            3. Con la obligación de pagar a las EPS y las ARP el cincuenta por ciento (50%) del costo del tratamiento de enfermedades profesionales, alteraciones de salud y demás secuelas originadas en el acoso laboral.
            
            Artículo 11. Garantías contra actitudes retaliatorias. A fin de evitar actos de represalia contra quienes han formulado peticiones, quejas y denuncias de acoso laboral o sirvan de testigos en tales procedimientos, establézcanse las siguientes garantías:
            1. La terminación unilateral del contrato de trabajo o la destitución de la víctima del acoso laboral que haya ejercido los procedimientos preventivos, correctivos y sancionatorios consagrados en la presente Ley, carecerán de todo efecto cuando se profieran dentro de los seis (6) meses siguientes a la petición o queja.
            """,
            "snippet": "Ley 1010 de 2006: Art. 9 - Medidas preventivas y correctivas. Art. 10 - Sanciones que incluyen indemnización, multas y pago de tratamientos médicos. Art 11 - Garantías contra represalias para quienes denuncien acoso laboral.",
            "relevance_score": 0.92
        },
        {
            "document_id": 3,
            "title": "Sentencia T-882 de 2006",
            "reference_number": "SentT-882/2006",
            "document_type": "Sentencia",
            "content": """
            ACOSO LABORAL-Protección por vía de tutela

            La Corte ha indicado que la acción de tutela es procedente para proteger los derechos fundamentales de los trabajadores que son víctimas de acoso laboral, siempre y cuando se cumplan los requisitos generales de procedibilidad de la acción de tutela contra particulares. En tales casos, la protección por vía de tutela procede como mecanismo transitorio para evitar un perjuicio irremediable.
            
            ACOSO LABORAL Y CALIDAD DE SUJETO DE ESPECIAL PROTECCIÓN CONSTITUCIONAL
            
            En el presente caso, la accionante es una persona de 51 años, madre cabeza de familia, sin otra fuente de ingresos distinta a su salario, con dos hijos, uno de ellos desempleado y el otro en universidad. En ese sentido, la Sala considera que la accionante es un sujeto de especial protección, que merece la protección de sus derechos fundamentales a través de la acción de tutela, aún en casos en que la misma no procede usualmente.
            
            DERECHO AL TRABAJO EN CONDICIONES DIGNAS Y JUSTAS-Alcance
            La Corte considera que la conducta continuada ejercida en el presente caso por el jefe inmediato de la accionante vulneró el derecho de ésta a gozar de un trabajo en condiciones dignas y justas, pues se expresa en (i) la negativa de suministrar elementos básicos de trabajo; (ii) la obstaculización del desempeño de funciones la accionante; (iii) la asignación de funciones que no corresponden al cargo; (iv) el trato desconsiderado e irrespetuoso hacia la accionante; y (v) el cambio de actitud en respuesta a la solicitud formal de mejoras en el ambiente de trabajo. Como resultado de estas conductas la accionante experimenta temor y desánimo, y no puede ejercer sus funciones a cabalidad, todo lo cual configura una violación del artículo 25 constitucional.
            """,
            "snippet": "Sentencia T-882 de 2006: La acción de tutela es procedente para proteger a trabajadores víctimas de acoso laboral, especialmente para sujetos de especial protección constitucional como madres cabeza de familia.",
            "relevance_score": 0.85
        },
        {
            "document_id": 4,
            "title": "Código Sustantivo del Trabajo - Artículo 62",
            "reference_number": "CST-Art.62",
            "document_type": "Código",
            "content": """
            ARTÍCULO 62. TERMINACIÓN DEL CONTRATO POR JUSTA CAUSA. Son justas causas para dar por terminado unilateralmente el contrato de trabajo:

            A) Por parte del empleador:
            
            1. El haber sufrido engaño por parte del trabajador, mediante la presentación de certificados falsos para su admisión o tendientes a obtener un provecho indebido.
            
            2. Todo acto de violencia, injuria, malos tratamientos o grave indisciplina en que incurra el trabajador en sus labores, contra el empleador, los miembros de su familia, el personal directivo o los compañeros de trabajo.
            
            3. Todo acto grave de violencia, injuria o malos tratamientos en que incurra el trabajador fuera del servicio, en contra del empleador, de los miembros de su familia o de sus representantes y socios, jefes de taller, vigilantes o celadores.
            
            4. Todo daño material causado intencionalmente a los edificios, obras, maquinarias y materias primas, instrumentos y demás objetos relacionados con el trabajo, y toda grave negligencia que ponga en peligro la seguridad de las personas o de las cosas.
            
            5. Todo acto inmoral o delictuoso que el trabajador cometa en el taller, establecimiento o lugar de trabajo o en el desempeño de sus labores.
            
            B) Por parte del trabajador:
            
            1. El haber sufrido engaño por parte del empleador, respecto de las condiciones de trabajo.
            
            2. Todo acto de violencia, malos tratamientos o amenazas graves inferidas por el empleador contra el trabajador o los miembros de su familia, dentro o fuera del servicio, o inferidas dentro del servicio por los parientes, representantes o dependientes del empleador con el consentimiento o la tolerancia de éste.
            
            3. Cualquier acto del empleador o de sus representantes que induzca al trabajador a cometer un acto ilícito o contrario a sus convicciones políticas o religiosas.
            """,
            "snippet": "CST Art. 62: Terminación del contrato por justa causa. Por parte del empleador: engaño, violencia, indisciplina grave. Por parte del trabajador: engaño sobre condiciones laborales, violencia o malos tratos del empleador.",
            "relevance_score": 0.65
        },
        {
            "document_id": 5,
            "title": "Resolución 2646 de 2008 - Riesgo Psicosocial",
            "reference_number": "Res-2646/2008",
            "document_type": "Resolución",
            "content": """
            Por la cual se establecen disposiciones y se definen responsabilidades para la identificación, evaluación, prevención, intervención y monitoreo permanente de la exposición a factores de riesgo psicosocial en el trabajo y para la determinación del origen de las patologías causadas por el estrés ocupacional.
            
            Artículo 3°. Definiciones. Para efectos de la presente resolución se adoptan las siguientes definiciones:
            
            a) Acoso laboral: Toda conducta persistente y demostrable, ejercida sobre un empleado, trabajador por parte de un empleador, un jefe o superior jerárquico inmediato o mediato, un compañero de trabajo o un subalterno, encaminada a infundir miedo, intimidación, terror y angustia, a causar perjuicio laboral, generar desmotivación en el trabajo, o inducir la renuncia del mismo, conforme lo establece la Ley 1010 de 2006.
            
            Artículo 14. Medidas preventivas y correctivas del acoso laboral. Son medidas preventivas y correctivas de acoso laboral las siguientes:
            
            1. Formular una política clara dirigida a prevenir el acoso laboral que incluya el compromiso, por parte del empleador y de los trabajadores, de promover un ambiente de convivencia laboral.
            
            2. Elaborar códigos o manuales de convivencia, en los que se identifiquen los tipos de comportamiento aceptables en la empresa.
            
            3. Realizar actividades de sensibilización sobre acoso laboral y sus consecuencias, dirigidos al nivel directivo y a los trabajadores, con el fin de que se rechacen estas prácticas y se respalde la dignidad e integridad de las personas en el trabajo.
            """,
            "snippet": "Resolución 2646 de 2008: Establece responsabilidades para prevenir riesgos psicosociales en el trabajo. Define acoso laboral según Ley 1010 y establece medidas preventivas incluyendo políticas, manuales de convivencia y actividades de sensibilización.",
            "relevance_score": 0.78
        }
    ]

def test_old_vs_new_prompt():
    """Compara el método original con el prompt optimizado usando la misma consulta"""
    logger.info("🔄 Comparando respuestas con prompts original vs optimizado")
    
    # Verificar configuración
    if not validate_config():
        logger.error("❌ Configuración de OpenAI inválida. No se puede continuar.")
        return False
    
    # Inicializar el servicio
    ai_service = AIService()
    
    # Crear documentos de prueba
    test_docs = create_test_documents()
    
    # Consulta de prueba
    query = "¿Qué es el acoso laboral según la ley colombiana y qué medidas puedo tomar si soy víctima?"
    
    # 1. Generar respuesta con el método original
    logger.info("🔍 Generando respuesta con el método original (generate_response)")
    start_time = time.time()
    
    response, confidence, needs_review, reason = ai_service.generate_response(
        query_text=query,
        search_results=test_docs
    )
    
    original_time = time.time() - start_time
    
    # 2. Generar respuesta con el método optimizado
    logger.info("🔍 Generando respuesta con el método optimizado (generate_legal_response)")
    start_time = time.time()
    
    optimized_response, optimized_confidence, cited_docs, requires_review = ai_service.generate_legal_response(
        query_text=query,
        search_results=test_docs
    )
    
    optimized_time = time.time() - start_time
    
    # Mostrar resultados
    logger.info("\n" + "=" * 80)
    logger.info("COMPARACIÓN DE RESULTADOS")
    logger.info("=" * 80)
    
    logger.info(f"⏱️ Tiempo con prompt original: {original_time:.2f} segundos")
    logger.info(f"⏱️ Tiempo con prompt optimizado: {optimized_time:.2f} segundos")
    logger.info(f"⏱️ Diferencia: {abs(original_time - optimized_time):.2f} segundos")
    
    logger.info(f"📊 Confianza con prompt original: {confidence:.2f}")
    logger.info(f"📊 Confianza con prompt optimizado: {optimized_confidence:.2f}")
    
    logger.info(f"🔍 Documentos citados con prompt optimizado: {len(cited_docs)}")
    
    # Mostrar respuestas en archivos de texto para comparación
    with open("respuesta_original.txt", "w") as f:
        f.write(response)
    
    with open("respuesta_optimizada.txt", "w") as f:
        f.write(optimized_response)
    
    logger.info("✅ Respuestas guardadas en archivos 'respuesta_original.txt' y 'respuesta_optimizada.txt'")
    
    return True

def test_insufficient_info_response():
    """Prueba la respuesta del sistema cuando la información es insuficiente"""
    logger.info("🧪 Probando respuesta con información insuficiente")
    
    # Verificar configuración
    if not validate_config():
        logger.error("❌ Configuración de OpenAI inválida. No se puede continuar.")
        return False
    
    # Inicializar el servicio
    ai_service = AIService()
    
    # Crear conjunto limitado de documentos
    limited_docs = create_test_documents()[3:4]  # Solo usar el documento CST
    
    # Consulta que requiere información no presente en los documentos
    query = "¿Cuáles son los pasos específicos para presentar una denuncia por acoso laboral ante el Ministerio de Trabajo?"
    
    # Generar respuesta con el método optimizado
    logger.info(f"🔍 Generando respuesta para: '{query}'")
    
    response, confidence, cited_docs, requires_review = ai_service.generate_legal_response(
        query_text=query,
        search_results=limited_docs
    )
    
    # Mostrar resultados
    logger.info("\n" + "=" * 80)
    logger.info("RESPUESTA CON INFORMACIÓN INSUFICIENTE")
    logger.info("=" * 80)
    
    logger.info(f"📊 Confianza: {confidence:.2f}")
    logger.info(f"🚩 Requiere revisión: {requires_review}")
    
    # Guardar respuesta en archivo
    with open("respuesta_insuficiente.txt", "w") as f:
        f.write(response)
    
    logger.info("✅ Respuesta guardada en 'respuesta_insuficiente.txt'")
    
    return confidence < 0.4  # Deberíamos obtener baja confianza

def test_structured_formatting():
    """Prueba el formato estructurado de las respuestas y referencias legales"""
    logger.info("🧪 Probando formato estructurado de respuestas")
    
    # Verificar configuración
    if not validate_config():
        logger.error("❌ Configuración de OpenAI inválida. No se puede continuar.")
        return False
    
    # Inicializar el servicio
    ai_service = AIService()
    
    # Crear documentos de prueba
    test_docs = create_test_documents()
    
    # Consulta específica que debería generar respuesta estructurada
    query = "¿Cuáles son las sanciones para el acoso laboral según la ley colombiana?"
    
    # Generar respuesta con el método optimizado
    logger.info(f"🔍 Generando respuesta para: '{query}'")
    
    response, confidence, cited_docs, requires_review = ai_service.generate_legal_response(
        query_text=query,
        search_results=test_docs
    )
    
    # Mostrar resultados
    logger.info("\n" + "=" * 80)
    logger.info("RESPUESTA CON FORMATO ESTRUCTURADO")
    logger.info("=" * 80)
    
    logger.info(f"📊 Confianza: {confidence:.2f}")
    logger.info(f"📚 Documentos citados: {len(cited_docs)}")
    
    # Verificar si la respuesta contiene secciones estructuradas
    has_direct_answer = "RESPUESTA DIRECTA" in response or "respuesta directa" in response.lower()
    has_legal_basis = "FUNDAMENTO LEGAL" in response or "fundamento legal" in response.lower()
    has_references = "REFERENCIAS LEGALES" in response or "referencias legales" in response.lower()
    
    logger.info(f"✓ Contiene sección de respuesta directa: {has_direct_answer}")
    logger.info(f"✓ Contiene sección de fundamento legal: {has_legal_basis}")
    logger.info(f"✓ Contiene sección de referencias legales: {has_references}")
    
    # Guardar respuesta en archivo
    with open("respuesta_estructurada.txt", "w") as f:
        f.write(response)
    
    logger.info("✅ Respuesta guardada en 'respuesta_estructurada.txt'")
    
    return has_direct_answer and has_legal_basis and has_references

def run_all_tests():
    """Ejecuta todas las pruebas de optimización de prompt"""
    logger.info("🚀 Iniciando pruebas de optimización de prompt para GPT")
    logger.info("=" * 80)
    
    tests = [
        ("Comparación Original vs Optimizado", test_old_vs_new_prompt),
        ("Respuesta con Información Insuficiente", test_insufficient_info_response),
        ("Formato Estructurado de Respuestas", test_structured_formatting)
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