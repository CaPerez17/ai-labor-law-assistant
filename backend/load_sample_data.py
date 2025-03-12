"""
Script para cargar datos de ejemplo
--------------------------------
Este script carga datos de ejemplo en la base de datos para pruebas.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Asegurarnos de que estamos en el directorio correcto
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

# Asegurar que el directorio backend esté en sys.path
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# Importaciones de la aplicación
from app.db.database import SessionLocal, engine, Base
from app.models.legal_document import LegalDocument, DocumentType


# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

# Datos de ejemplo
sample_documents = [
    {
        "title": "Código Sustantivo del Trabajo, Artículo 236",
        "document_type": DocumentType.LEY,
        "reference_number": "CST-236",
        "issue_date": datetime(1950, 8, 5),
        "source": "Congreso de Colombia",
        "content": """
        ARTICULO 236. LICENCIA EN LA ÉPOCA DEL PARTO E INCENTIVOS PARA LA ADECUADA ATENCIÓN Y CUIDADO DEL RECIÉN NACIDO.

        1. Toda trabajadora en estado de embarazo tiene derecho a una licencia de dieciocho (18) semanas en la época de parto, remunerada con el salario que devengue al momento de iniciar su licencia.

        2. Si se tratare de un salario que no sea fijo como en el caso del trabajo a destajo o por tarea, se tomará en cuenta el salario promedio devengado por la trabajadora en el último año de servicio, o en todo el tiempo si fuere menor.

        3. Para los efectos de la licencia de que trata este artículo, la trabajadora debe presentar al empleador un certificado médico, en el cual debe constar:

           a) El estado de embarazo de la trabajadora;
           b) La indicación del día probable del parto, y
           c) La indicación del día desde el cual debe empezar la licencia, teniendo en cuenta que, por lo menos, ha de iniciarse dos semanas antes del parto.

        4. Todas las provisiones y garantías establecidas en la presente ley para la madre biológica se hacen extensivas en los mismos términos y en cuanto fuere procedente a la madre adoptante, o al padre que quede a cargo del recién nacido sin apoyo de la madre, sea por enfermedad o muerte, asimilando la fecha del parto a la de la entrega oficial del menor que se ha adoptado, o del que adquiere custodia justo después del nacimiento. En ese sentido, la licencia materna se extiende al padre en caso de fallecimiento o enfermedad de la madre, el empleador del padre del niño le concederá una licencia de duración equivalente al tiempo que falta para expirar el periodo de la licencia posterior al parto concedida a la madre.

        5. La licencia de maternidad para madres de niños prematuros, tendrá en cuenta la diferencia entre la fecha gestacional y el nacimiento a término, las cuales serán sumadas a las dieciocho (18) semanas que se establecen en la presente ley. Cuando se trate de madres con parto múltiple, la licencia se ampliará en dos (2) semanas más.

        6. La trabajadora que haga uso de la licencia en la época del parto tomará las dieciocho (18) semanas de licencia a las que tiene derecho, de la siguiente manera:

           a) Licencia preparto: La trabajadora podrá tomar una o dos semanas previas a la fecha probable del parto. Esta decisión deberá ser informada al empleador con anterioridad.
           b) Licencia posparto: La trabajadora tomará las semanas restantes inmediatamente después del parto.

        7. De las dieciocho (18) semanas de licencia remunerada, la semana anterior al probable parto será de obligatorio goce en caso de que el médico tratante prescriba algo diferente. La licencia remunerada de la que habla este artículo es incompatible con la licencia de calamidad doméstica y en caso de haberse solicitado esta última por el nacimiento de un hijo, estos días serán descontados de la misma.
        """,
        "keywords": "licencia de maternidad, embarazo, parto, remuneración, semanas, protección laboral",
        "category": "Licencias Laborales",
        "subcategory": "Maternidad"
    },
    {
        "title": "Ley 1822 de 2017",
        "document_type": DocumentType.LEY,
        "reference_number": "Ley 1822 de 2017",
        "issue_date": datetime(2017, 1, 4),
        "source": "Congreso de Colombia",
        "content": """
        LEY 1822 DE 2017
        (Enero 4)
        
        Por medio de la cual se incentiva la adecuada atención y cuidado de la primera infancia, se modifican los artículos 236 y 239 del Código Sustantivo del Trabajo y se dictan otras disposiciones.
        
        EL CONGRESO DE COLOMBIA
        
        DECRETA:
        
        ARTÍCULO 1o. El artículo 236 del Código Sustantivo del Trabajo quedará así:
        
        Artículo 236. Licencia en la época del parto e incentivos para la adecuada atención y cuidado del recién nacido.
        
        1. Toda trabajadora en estado de embarazo tiene derecho a una licencia de dieciocho (18) semanas en la época de parto, remunerada con el salario que devengue al momento de iniciar su licencia.
        
        2. Si se tratare de un salario que no sea fijo como en el caso del trabajo a destajo o por tarea, se tomará en cuenta el salario promedio devengado por la trabajadora en el último año de servicio, o en todo el tiempo si fuere menor.
        
        3. Para los efectos de la licencia de que trata este artículo, la trabajadora debe presentar al empleador un certificado médico, en el cual debe constar:
        
        a) El estado de embarazo de la trabajadora;
        
        b) La indicación del día probable del parto, y
        
        c) La indicación del día desde el cual debe empezar la licencia, teniendo en cuenta que, por lo menos, ha de iniciarse dos semanas antes del parto.
        
        Los beneficios incluidos en este artículo, y el artículo 239 de la presente ley, no excluyen a los trabajadores del sector público.
        
        4. Todas las provisiones y garantías establecidas en el presente capítulo para la madre biológica se hacen extensivas, en los mismos términos y en cuanto fuere procedente para la madre adoptante asimilando la fecha del parto a la de la entrega oficial del menor que se adopta. La licencia se extiende al padre adoptante sin cónyuge o compañera permanente.
        """,
        "keywords": "licencia de maternidad, embarazo, parto, ley, artículo 236, código sustantivo del trabajo",
        "category": "Licencias Laborales",
        "subcategory": "Maternidad"
    },
    {
        "title": "Salario Mínimo Colombia 2023",
        "document_type": DocumentType.DECRETO,
        "reference_number": "Decreto 2613 de 2022",
        "issue_date": datetime(2022, 12, 15),
        "source": "Ministerio del Trabajo",
        "content": """
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
        "keywords": "salario mínimo, 2023, decreto, Colombia, remuneración",
        "category": "Salarios y Prestaciones",
        "subcategory": "Salario Mínimo"
    },
    {
        "title": "Sentencia C-005 de 2017 sobre Estabilidad Laboral Reforzada",
        "document_type": DocumentType.SENTENCIA,
        "reference_number": "C-005/17",
        "issue_date": datetime(2017, 1, 18),
        "source": "Corte Constitucional de Colombia",
        "content": """
        SENTENCIA C-005/17
        
        PROTECCION LABORAL REFORZADA A MUJERES EMBARAZADAS
        
        PROTECCION LABORAL REFORZADA DE MUJER EMBARAZADA-Fundamento constitucional
        
        PROTECCION LABORAL REFORZADA DE MUJER EMBARAZADA-Contenido y alcance
        
        La protección a la mujer durante el embarazo y la lactancia tiene múltiples fundamentos en nuestro ordenamiento constitucional. En primer lugar, el artículo 43 contiene un deber específico estatal en este sentido cuando señala que la mujer "durante el embarazo y después del parto gozará de especial asistencia y protección del Estado, y recibirá de éste subsidio alimentario si entonces estuviere desempleada o desamparada". Este enunciado constitucional implica a su vez dos obligaciones: la especial protección estatal de la mujer embarazada y lactante, sin distinción, y un deber prestacional también a cargo del Estado: otorgar un subsidio cuando esté desempleada o desamparada.
        
        En el ámbito del trabajo, la protección a la mujer embarazada y lactante se extiende a todas las modalidades de relación laboral incluyendo las que se dan en virtud de contratos de prestación de servicios. Por ello, el legislador prevé medidas legislativas que buscan asegurar la permanencia en el empleo de las mujeres que se encuentran en el periodo de embarazo o de lactancia, como desarrollo del principio de "estabilidad laboral reforzada". La jurisprudencia ha sistematizado los elementos que configuran tal protección laboral reforzada.
        
        FUERO DE ESTABILIDAD LABORAL REFORZADA-El fuero de estabilidad laboral reforzada se aplica a todas las trabajadoras sin importar la modalidad de contratación
        
        El fuero de estabilidad laboral reforzada se aplica a todas las trabajadoras sin importar la modalidad de contratación. Sin embargo el alcance de la protección varía de acuerdo con la modalidad de vinculación. Para las trabajadoras en relación laboral por contrato de trabajo a término indefinido aplica el fuero de estabilidad reforzada hasta los seis meses posteriores al parto. Para las trabajadoras con contrato a término fijo, la Sala determinó que el fuero de estabilidad reforzada comprende el mantenimiento del contrato o su renovación cuando subsistan las causas que le dieron origen y la materia del trabajo hasta por lo menos el vencimiento de la licencia de maternidad, habida cuenta que, en estos casos, las protecciones establecidas en el artículo 239 del CST, se extienden durante el embarazo y la licencia de maternidad, es decir "los tres meses posteriores al parto".
        
        En el supuesto del contrato de prestación de servicios, la Corte consideró que el mecanismo de protección opera por el tiempo de gestación y los seis meses siguientes, e incluye el pago de las erogaciones dejadas de percibir en caso de desvinculación injustificada, mas no supone el reintegro al cargo, por la naturaleza del contrato y la autonomía del contratista.
        """,
        "keywords": "estabilidad laboral reforzada, embarazo, fuero, protección, sentencia, maternidad",
        "category": "Protección Laboral",
        "subcategory": "Estabilidad Laboral Reforzada"
    },
    {
        "title": "Indemnización por Despido Sin Justa Causa",
        "document_type": DocumentType.LEY,
        "reference_number": "CST-Art 64",
        "issue_date": datetime(1950, 8, 5),
        "source": "Código Sustantivo del Trabajo",
        "content": """
        ARTICULO 64. TERMINACION UNILATERAL DEL CONTRATO DE TRABAJO SIN JUSTA CAUSA. 
        
        En todo contrato de trabajo va envuelta la condición resolutoria por incumplimiento de lo pactado, con indemnización de perjuicios a cargo de la parte responsable. Esta indemnización comprende el lucro cesante y el daño emergente.
        
        En caso de terminación unilateral del contrato de trabajo sin justa causa comprobada, por parte del empleador o si éste da lugar a la terminación unilateral por parte del trabajador por alguna de las justas causas contempladas en la ley, el primero deberá al segundo una indemnización en los términos que a continuación se señalan:
        
        En los contratos a término fijo, el valor de los salarios correspondientes al tiempo que faltare para cumplir el plazo estipulado del contrato; o el del lapso determinado por la duración de la obra o la labor contratada, caso en el cual la indemnización no será inferior a quince (15) días.
        
        En los contratos a término indefinido la indemnización se pagará así:
        
        a) Para trabajadores que devenguen un salario inferior a diez (10) salarios mínimos mensuales legales:
        
        1. Treinta (30) días de salario cuando el trabajador tuviere un tiempo de servicio no mayor de un (1) año.
        
        2. Si el trabajador tuviere más de un (1) año de servicio continuo se le pagarán veinte (20) días adicionales de salario sobre los treinta (30) básicos del numeral 1, por cada uno de los años de servicio subsiguientes al primero y proporcionalmente por fracción;
        
        b) Para trabajadores que devenguen un salario igual o superior a diez (10), salarios mínimos legales mensuales.
        
        1. Veinte (20) días de salario cuando el trabajador tuviere un tiempo de servicio no mayor de un (1) año.
        
        2. Si el trabajador tuviere más de un (1) año de servicio continuo, se le pagarán quince (15) días adicionales de salario sobre los veinte (20) días básicos del numeral 1 anterior, por cada uno de los años de servicio subsiguientes al primero y proporcionalmente por fracción.
        
        PARÁGRAFO TRANSITORIO. Los trabajadores que al momento de entrar en vigencia la presente ley, tuvieren diez (10) o más años al servicio continuo del empleador, se les aplicará la tabla de indemnización establecida en los literales b), c) y d) del artículo 6o. de la Ley 50 de 1990, exceptuando el parágrafo transitorio, el cual se aplica únicamente para los trabajadores que tenían diez (10) o más años el primero de enero de 1991.
        """,
        "keywords": "despido sin justa causa, indemnización, terminación de contrato, código sustantivo del trabajo",
        "category": "Terminación Laboral",
        "subcategory": "Indemnizaciones"
    }
]

def load_sample_data():
    """Carga los datos de ejemplo en la base de datos"""
    try:
        # Crear una sesión
        db = SessionLocal()
        
        # Verificar si ya hay documentos
        existing_count = db.query(LegalDocument).count()
        if existing_count > 0:
            print(f"Ya existen {existing_count} documentos en la base de datos.")
            should_continue = input("¿Desea continuar y agregar más documentos? (s/n): ").lower()
            if should_continue != 's':
                print("Operación cancelada.")
                return
        
        # Insertar los documentos
        for doc_data in sample_documents:
            document = LegalDocument(**doc_data)
            db.add(document)
        
        # Guardar cambios
        db.commit()
        print(f"Se han agregado {len(sample_documents)} documentos de ejemplo a la base de datos.")
        
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    load_sample_data() 