"""
Script de prueba para el procesador de documentos
-------------------------------------------
Este script prueba la funcionalidad del procesador de documentos con textos de ejemplo.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Asegurarnos de que backend/ esté en sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar módulos
from utils.document_processor import DocumentProcessor

# Crear ejemplos de documentos legales en el directorio de prueba
SAMPLE_TEXTS = {
    "licencia_maternidad.txt": """
    CÓDIGO SUSTANTIVO DEL TRABAJO
    ARTÍCULO 236. LICENCIA EN LA ÉPOCA DEL PARTO E INCENTIVOS PARA LA ADECUADA ATENCIÓN Y CUIDADO DEL RECIÉN NACIDO.
    (Artículo modificado por el artículo 1 de la Ley 1822 de 2017)
    
    1. Toda trabajadora en estado de embarazo tiene derecho a una licencia de dieciocho (18) semanas en la época de parto, remunerada con el salario que devengue al momento de iniciar su licencia.
    
    2. Si se tratare de un salario que no sea fijo como en el caso del trabajo a destajo o por tarea, se tomará en cuenta el salario promedio devengado por la trabajadora en el último año de servicio, o en todo el tiempo si fuere menor.
    
    3. Para los efectos de la licencia de que trata este artículo, la trabajadora debe presentar al empleador un certificado médico, en el cual debe constar:
       a) El estado de embarazo de la trabajadora;
       b) La indicación del día probable del parto, y
       c) La indicación del día desde el cual debe empezar la licencia, teniendo en cuenta que, por lo menos, ha de iniciarse dos semanas antes del parto.
    
    4. Todas las provisiones y garantías establecidas en la presente ley para la madre biológica se hacen extensivas en los mismos términos y en cuanto fuere procedente a la madre adoptante, o al padre que quede a cargo del recién nacido sin apoyo de la madre, sea por enfermedad o muerte, asimilando la fecha del parto a la de la entrega oficial del menor que se ha adoptado, o del que adquiere custodia justo después del nacimiento.
    """,
    
    "salario_minimo.txt": """
    DECRETO NÚMERO 2613 DE 2022
    (Diciembre 15)
    
    Por el cual se fija el salario mínimo mensual legal
    
    EL PRESIDENTE DE LA REPÚBLICA DE COLOMBIA
    
    En ejercicio de sus atribuciones constitucionales y legales, en particular las conferidas en el numeral 11 del artículo 189 de la Constitución Política, en desarrollo de lo dispuesto en el artículo 8 de la Ley 278 de 1996,
    
    DECRETA:
    
    ARTÍCULO 1. Salario Mínimo Legal Mensual para el año 2023. Fijar a partir del primero (1°) de enero de 2023, como Salario Mínimo Legal Mensual para los trabajadores de los sectores urbano y rural, la suma de UN MILLÓN CIENTO SESENTA MIL PESOS ($1.160.000).
    
    ARTÍCULO 2. Vigencia. Este Decreto rige a partir del primero (1°) de enero de 2023 y deroga el Decreto 1724 de 2021.
    
    PUBLÍQUESE Y CÚMPLASE
    Dado en Bogotá, D.C., a los 15 días del mes de diciembre de 2022
    
    (Original firmado)
    GUSTAVO PETRO URREGO
    PRESIDENTE DE LA REPÚBLICA
    """,
    
    "estabilidad_reforzada.txt": """
    SENTENCIA C-005/17
    
    PROTECCION LABORAL REFORZADA A MUJERES EMBARAZADAS
    
    PROTECCION LABORAL REFORZADA DE MUJER EMBARAZADA-Fundamento constitucional
    
    PROTECCION LABORAL REFORZADA DE MUJER EMBARAZADA-Contenido y alcance
    
    La protección a la mujer durante el embarazo y la lactancia tiene múltiples fundamentos en nuestro ordenamiento constitucional. En primer lugar, el artículo 43 contiene un deber específico estatal en este sentido cuando señala que la mujer "durante el embarazo y después del parto gozará de especial asistencia y protección del Estado, y recibirá de éste subsidio alimentario si entonces estuviere desempleada o desamparada". Este enunciado constitucional implica a su vez dos obligaciones: la especial protección estatal de la mujer embarazada y lactante, sin distinción, y un deber prestacional también a cargo del Estado: otorgar un subsidio cuando esté desempleada o desamparada.
    
    En el ámbito del trabajo, la protección a la mujer embarazada y lactante se extiende a todas las modalidades de relación laboral incluyendo las que se dan en virtud de contratos de prestación de servicios. Por ello, el legislador prevé medidas legislativas que buscan asegurar la permanencia en el empleo de las mujeres que se encuentran en el periodo de embarazo o de lactancia, como desarrollo del principio de "estabilidad laboral reforzada". La jurisprudencia ha sistematizado los elementos que configuran tal protección laboral reforzada.
    """
}

def create_sample_files():
    """Crea archivos de ejemplo en el directorio de prueba"""
    # Crear directorio de prueba
    test_dir = os.path.join(backend_dir, "data", "docs", "txt")
    os.makedirs(test_dir, exist_ok=True)
    
    # Crear archivos de muestra
    for filename, content in SAMPLE_TEXTS.items():
        file_path = os.path.join(test_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Archivo creado: {file_path}")
    
    return test_dir

def test_document_processing():
    """Prueba el procesador de documentos con archivos de ejemplo"""
    # Crear archivos de muestra
    test_dir = create_sample_files()
    
    # Inicializar el procesador
    processor = DocumentProcessor()
    
    # Procesar los documentos
    print("\n=== Procesando documentos ===")
    documents = processor.process_directory(test_dir)
    
    if not documents:
        print("No se procesaron documentos")
        return
    
    # Mostrar resultados
    print(f"\n=== {len(documents)} documentos procesados ===")
    for i, doc in enumerate(documents, 1):
        print(f"\nDocumento {i}:")
        print(f"Título: {doc['title']}")
        print(f"Tipo: {doc['document_type']}")
        print(f"Referencia: {doc['reference_number']}")
        print(f"Fecha: {doc['issue_date']}")
        print(f"Fuente: {doc['source']}")
        print(f"Categoría: {doc['category']} / {doc['subcategory']}")
        print(f"Palabras clave: {doc['keywords']}")
        print(f"Contenido: {doc['content'][:100]}...")

def test_text_processing():
    """Prueba el procesamiento de texto directamente"""
    processor = DocumentProcessor()
    
    # Probar con un ejemplo específico
    print("\n=== Procesando texto de ejemplo ===")
    sample_text = SAMPLE_TEXTS["licencia_maternidad.txt"]
    
    # Preprocesar
    processed_text = processor.preprocess_text(sample_text)
    tokens = processor.tokenize_text(processed_text)
    
    # Mostrar resultados
    print(f"Tokens extraídos: {len(tokens)}")
    print(f"Primeros 20 tokens: {tokens[:20]}")
    
    # Extraer tipo y referencia
    doc_type = processor.detect_document_type(processed_text)
    reference = processor.extract_reference_number(processed_text, doc_type)
    
    print(f"Tipo detectado: {doc_type}")
    print(f"Referencia: {reference}")
    
    # Extraer categoría y keywords
    category, subcategory = processor.extract_categories(tokens)
    keywords = processor.extract_keywords(tokens)
    
    print(f"Categoría: {category} / {subcategory}")
    print(f"Palabras clave: {keywords}")

if __name__ == "__main__":
    print("=== Prueba del procesador de documentos ===")
    
    # Probar procesamiento de texto
    test_text_processing()
    
    # Probar procesamiento de documentos
    test_document_processing() 