# Backend de AI Labor Law Assistant

Este directorio contiene el backend del asistente de derecho laboral colombiano basado en inteligencia artificial.

## Tecnologías utilizadas

- **FastAPI**: Framework moderno para APIs con Python
- **PostgreSQL**: Base de datos relacional para almacenar documentos legales
- **SQLAlchemy**: ORM para interactuar con la base de datos
- **BM25**: Algoritmo de recuperación de información
- **GPT**: Modelos de lenguaje para generación de respuestas
- **NLTK**: Procesamiento de lenguaje natural para preprocesamiento de texto

## Estructura del proyecto

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── documents.py
│   │   │   └── queries.py
│   │   └── __init__.py
│   ├── core/
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   └── legal_document.py
│   ├── schemas/
│   │   ├── legal_document.py
│   │   └── query.py
│   ├── services/
│   │   ├── ai_service.py
│   │   └── search_service.py
│   └── utils/
├── main.py
├── .env
└── README.md
```

## Configuración del entorno

1. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. Instala las dependencias:
   ```bash
   pip install -r ../requirements.txt
   ```

3. Configura la base de datos PostgreSQL:
   ```bash
   # Ejemplo en PostgreSQL
   createdb laborlaw
   ```

4. Copia el archivo `.env.example` a `.env` y configura las variables de entorno:
   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales
   ```

## Ejecución

Para ejecutar el servidor en modo desarrollo:

```bash
uvicorn main:app --reload
```

El servidor estará disponible en [http://localhost:8000](http://localhost:8000).

La documentación interactiva de la API estará disponible en:
- [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)

## Características principales

1. **Gestión de documentos legales**: CRUD para documentos legales en la base de datos
2. **Búsqueda mediante BM25**: Algoritmo de búsqueda para recuperar documentos relevantes
3. **Generación de respuestas con GPT**: Utiliza modelos de lenguaje para generar respuestas contextuales
4. **Evaluación de confianza**: Determina si una respuesta tiene suficiente calidad o necesita revisión humana
5. **Procesamiento asíncrono**: Las consultas se procesan en segundo plano para mejorar la experiencia del usuario

## Endpoints principales

- `POST /api/queries/`: Crea una nueva consulta legal
- `GET /api/queries/{query_id}`: Obtiene el estado y respuesta de una consulta
- `POST /api/documents/`: Crea un nuevo documento legal
- `GET /api/documents/`: Lista documentos legales con filtros opcionales
- `POST /api/documents/search`: Busca documentos legales por texto 