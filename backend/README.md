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
   OPENAI_API_KEY=sk-tu-api-key-de-openai
   GPT_MODEL=gpt-4o
   SECRET_KEY=clave_secreta_para_jwt
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

## Configuración de OpenAI 🔑

El backend utiliza la API de OpenAI para generar respuestas fundamentadas en documentos legales. Para configurar correctamente OpenAI:

1. **Obtener una API Key**:
   - Crea una cuenta en [OpenAI](https://platform.openai.com/)
   - Genera una API key en la sección [API Keys](https://platform.openai.com/api-keys)

2. **Configurar la API Key**:
   - Agrega tu API key al archivo `.env`:
     ```
     OPENAI_API_KEY=sk-tu-api-key-de-openai
     GPT_MODEL=gpt-4o  # Puedes usar gpt-3.5-turbo para reducir costos
     ```

3. **Verificar la configuración**:
   - Ejecuta el script de prueba para verificar que todo funciona correctamente:
     ```bash
     python test_openai_config.py
     ```
   - Este script ejecutará pruebas de:
     - Validación de la configuración
     - Inicialización del servicio de IA
     - Validación de la API key con OpenAI
     - Una prueba simple de generación de texto

4. **Características del Servicio de IA**:
   - **Manejo de errores robusto**: Reintentos automáticos con backoff exponencial para errores temporales
   - **Validación de API Key**: Verificación de formato y validez de la API key
   - **Formateo de contexto BM25**: Estructuración de resultados de búsqueda para GPT
   - **Optimización de prompts**: Mejora la precisión de las respuestas con instrucciones específicas
   - **Control de costos**: Límites de tokens y manejo eficiente del contexto
   - **Evaluación de confianza**: Detección automática de casos que requieren revisión humana
   - **Formateo de referencias legales**: Extracción y estructuración de citas a documentos legales

El módulo `app/services/ai_service.py` contiene la implementación del servicio de IA, con métodos específicos para la integración BM25+GPT. Los principales métodos incluyen:

- `format_bm25_context()`: Formatea resultados BM25 para enviar a GPT
- `generate_gpt_response()`: Maneja la comunicación con OpenAI API
- `generate_response()`: Método principal para generar respuestas legales
- `format_response_with_sources()`: Asocia respuestas con fuentes legales

El archivo `config.py` contiene la configuración centralizada y validación de variables de entorno.

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

## Nuevo Endpoint: Consultas Legales Directas 🔍💬

Hemos implementado un nuevo endpoint `/api/ask/` que proporciona una forma rápida y directa para realizar consultas legales. Este endpoint:

1. **Recibe una consulta legal del usuario**
2. **Busca documentos relevantes utilizando BM25**
3. **Genera una respuesta fundamentada con GPT-4**
4. **Devuelve la respuesta con referencias a los documentos legales utilizados**

### Uso del Endpoint

```python
import requests

url = "http://127.0.0.1:12345/api/ask/"
payload = {"query": "¿Qué es la estabilidad laboral reforzada?"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

print(result["response"])  # Respuesta generada
print(result["references"])  # Referencias legales utilizadas
```

### Estructura de la Respuesta

```json
{
  "query": "¿Qué es la estabilidad laboral reforzada?",
  "response": "La estabilidad laboral reforzada es una protección especial...",
  "references": [
    {
      "id": 24,
      "title": "Sentencia T-320 de 2016",
      "reference": "SentT-320/2016",
      "relevance": 0.92
    }
  ],
  "confidence_score": 0.85,
  "needs_human_review": false,
  "review_reason": null,
  "processing_time_ms": 1250.45,
  "timestamp": "2023-01-01T12:00:05"
}
```

### Prueba del Endpoint

Para probar rápidamente el endpoint:

```bash
python test_ask_endpoint.py "¿Cuántos días de licencia de maternidad me corresponden?"
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

## Optimización del Prompt para GPT 🧠

Para mejorar la calidad de las respuestas legales, se han implementado las siguientes optimizaciones en el prompt para GPT:

### Mejoras implementadas

1. **Instrucciones más explícitas**: Se reformuló el prompt para asegurar que GPT solo utilice información de los documentos legales proporcionados, sin inventar o añadir conocimiento externo.

2. **Estructura mejorada**: Las respuestas ahora siguen un formato consistente:
   - **Respuesta Directa**: Respuesta concisa y clara a la consulta
   - **Fundamento Legal**: Explicación detallada con citas a documentos específicos
   - **Referencias Legales**: Lista completa de fuentes utilizadas

3. **Formato de documentos optimizado**: 
   - Priorización de contenido relevante en documentos extensos
   - Eliminación de redundancias entre documentos
   - Extracción inteligente de párrafos clave

4. **Control de confianza**: 
   - Sistema de evaluación de confianza (0-1) para cada respuesta
   - Advertencia automática para respuestas con baja confianza
   - Indicación clara cuando la información disponible es insuficiente

5. **Citación precisa**:
   - Referencias exactas a artículos y leyes
   - Citas explícitas a los documentos fuente
   - Formato destacado para facilitar la identificación

### Pruebas y validación

Se han desarrollado scripts de prueba para verificar la calidad de las respuestas:
- `test_optimized_gpt_prompt.py`: Prueba exhaustiva de todos los aspectos del prompt
- `test_simple_prompt.py`: Prueba rápida para verificar el funcionamiento básico

Para ejecutar las pruebas:
```bash
cd backend
python test_simple_prompt.py
```

> **Nota**: Es necesario configurar correctamente la API key de OpenAI en el archivo `.env` antes de ejecutar las pruebas.

## Documentación API

La documentación interactiva está disponible en:

- Swagger UI: [http://127.0.0.1:12345/docs](http://127.0.0.1:12345/docs)
- ReDoc: [http://127.0.0.1:12345/redoc](http://127.0.0.1:12345/redoc)

### Endpoints Principales

- `POST /api/ask/`: Consultas legales directas (BM25 + GPT) con respuesta inmediata
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
4. Ejecuta el script de diagnóstico: `python test_openai_config.py`

### Códigos de Error Comunes de OpenAI

- **401 (Unauthorized)**: API key inválida o expirada
- **429 (Too Many Requests)**: Límite de tasa excedido
- **500, 502, 503, 504**: Errores del servidor de OpenAI

## Ejecución de Tests

```bash
cd backend
pytest
```

## Inicialización de Usuarios

Para crear usuarios iniciales en la base de datos, se puede ejecutar el script `seed.py`:

```bash
cd backend
python scripts/seed.py
```

Este script creará los siguientes usuarios si no existen:
- **admin@legalassista.com** (password: admin123) - Rol: Administrador
- **abogado@legalassista.com** (password: abogado123) - Rol: Abogado

El script verifica primero si los usuarios ya existen para evitar duplicados. 