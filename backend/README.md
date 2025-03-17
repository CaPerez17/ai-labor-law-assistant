# Backend AI Labor Law Assistant 🤖⚖️

Este es el backend para el proyecto "AI Labor Law Assistant", un asistente de IA especializado en derecho laboral colombiano.

## Tecnologías Utilizadas

- **FastAPI**: Framework para crear APIs con Python
- **SQLAlchemy**: ORM para manejo de base de datos
- **BM25**: Algoritmo de recuperación de información para búsqueda
- **GPT/OpenAI**: Procesamiento de lenguaje natural
- **SQLite**: Base de datos para desarrollo
- **PostgreSQL**: Base de datos para producción (opcional)
- **NLTK**: Procesamiento de lenguaje natural
- **PyMuPDF**: Procesamiento de documentos PDF

## Estructura del Proyecto

```
backend/
├── app/
│   ├── api/               # Definición de endpoints API
│   ├── core/              # Configuración central
│   ├── db/                # Configuración de base de datos
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/           # Esquemas Pydantic
│   ├── services/          # Servicios (búsqueda, autenticación, etc.)
│   └── utils/             # Utilidades generales
├── data/                  # Archivos de datos
│   └── docs/              # Documentos legales
│       ├── pdf/           # Documentos en formato PDF
│       └── txt/           # Documentos en formato texto
├── tests/                 # Tests unitarios e integración
│── utils/                 # Utilidades para procesamiento de documentos
│── alembic/               # Migraciones de base de datos
│── .env                   # Variables de entorno
└── requirements.txt       # Dependencias
```

## Configuración del Entorno

1. **Crear un entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**:
   - Crea un archivo `.env` en la carpeta `backend/` con las siguientes variables:
   ```
   DATABASE_URL=sqlite:///./test.db
   # O para PostgreSQL:
   # DATABASE_URL=postgresql://user:password@localhost/dbname
   OPENAI_API_KEY=tu_api_key
   SECRET_KEY=clave_secreta_para_jwt
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

## Ejecución

1. **Desde el directorio raíz del proyecto**:
   ```bash
   cd backend
   python run.py
   ```
   O directamente con uvicorn:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 12345
   ```

2. **Para cargar documentos en la base de datos**:
   ```bash
   python load_documents.py --create-tables
   ```

## Integración BM25 + GPT 🧠

Hemos implementado una integración completa de nuestro motor de búsqueda BM25 con GPT-4 para generar respuestas inteligentes a consultas legales.

### Características Principales

1. **Búsqueda de Documentos Legales Relevantes con BM25**
   - Recuperación de documentos por relevancia
   - Sistema de caché para consultas repetidas
   - Parámetros optimizados (k1=1.5, b=0.75) para documentos legales

2. **Formateo Estructurado para GPT**
   - Conversión de resultados BM25 a formato JSON optimizado
   - Extracción de metadatos clave (tipo, referencia, relevancia)
   - Límites de contexto configurables para optimizar tokens

3. **Prompt Avanzado para Respuestas Legales**
   - Instrucciones precisas para respuestas basadas en evidencia
   - Sistema de citas a documentos específicos [DocX]
   - Sección de "Referencias Legales" obligatoria

4. **Evaluación de Confianza**
   - Evaluación automática de calidad de respuesta (0-1)
   - Detección de casos que requieren revisión humana
   - Explicación de motivos de baja confianza

### Probando el Asistente Legal

Para probar el asistente legal:

```bash
# Consulta específica
python test_legal_assistant.py "¿Cuántos días de licencia de maternidad me corresponden?"

# Suite completa de pruebas
python test_legal_assistant.py
```

### Ejemplo de Respuesta Estructurada

Las respuestas generadas incluyen:
- Respuesta directa a la consulta
- Citas específicas a los documentos legales
- Lista de fuentes legales utilizadas
- Puntuación de confianza de la respuesta

## Optimización de Búsqueda BM25 🔍

Recientemente hemos optimizado el sistema de búsqueda para mejorar la precisión y eficiencia con las siguientes mejoras:

### 1. Parámetros Ajustados

- **k1 = 1.5** (antes 1.2): Controla la importancia de la frecuencia del término en un documento. Un valor más alto da más peso a la frecuencia.
- **b = 0.75**: Controla el impacto de la longitud del documento en la relevancia. 

Estas modificaciones mejoran la precisión para documentos legales en español, priorizando mejor la relevancia.

### 2. Sistema de Caché de Consultas

Hemos implementado un sistema de caché de consultas usando SQLite que:

- Almacena resultados de búsquedas previas 
- Reduce dramáticamente el tiempo de respuesta para consultas repetidas (mejoras de 17ms a 0.1ms)
- Gestiona automáticamente la expiración del caché (por defecto 24 horas)

### 3. Indexación Optimizada

- El índice BM25 se mantiene en memoria
- Se recalcula automáticamente solo cuando hay cambios en la base de datos
- Permite indexación específica para consultas filtradas
- Reduce el tiempo de procesamiento para búsquedas frecuentes

### Pruebas de Rendimiento

El script `test_search.py` permite evaluar el rendimiento con diferentes:
- Configuraciones de parámetros (k1, b)
- Consultas de prueba
- Medición de tiempos de respuesta con y sin caché

Para ejecutar las pruebas:
```bash
python test_search.py
```

## Documentación API

La documentación interactiva está disponible en:

- Swagger UI: [http://127.0.0.1:12345/docs](http://127.0.0.1:12345/docs)
- ReDoc: [http://127.0.0.1:12345/redoc](http://127.0.0.1:12345/redoc)

### Endpoints Principales

- `POST /api/queries/`: Crea una nueva consulta (procesamiento asíncrono)
- `POST /api/queries/sync`: Crea y procesa una consulta inmediatamente (síncrono)
- `GET /api/queries/{query_id}`: Obtiene el estado de una consulta
- `POST /api/search/`: Búsqueda directa con BM25 (sin procesamiento GPT)

## Solución de Problemas

### Conflictos de Puertos

Si el puerto 12345 está ocupado, puedes cambiarlo en `config.py` o especificarlo en el comando:
```bash
uvicorn app.main:app --port 10000
```

### Problemas de Base de Datos

Para reiniciar la base de datos:
```bash
rm backend/test.db
python -c "from app.db.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Errores de Importación

Si hay errores de importación, verifica:
1. Que estás ejecutando desde el directorio correcto (backend/)
2. Que las dependencias están instaladas
3. Que el archivo `__init__.py` existe en todos los paquetes

### Problemas con el Caché

Si encuentras problemas con las respuestas en caché:
```bash
rm -rf backend/cache
```

### Problemas con OpenAI API

Si encuentras errores relacionados con la API de OpenAI:
1. Verifica que tu API key sea válida y esté configurada en `.env`
2. Asegúrate de tener crédito disponible en tu cuenta
3. Verifica la disponibilidad del modelo configurado

## Ejecución de Tests

```bash
cd backend
pytest
``` 