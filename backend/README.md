# Backend de AI Labor Law Assistant

Este directorio contiene el backend del asistente de derecho laboral colombiano basado en inteligencia artificial.

## Tecnologías utilizadas

- **FastAPI**: Framework moderno para APIs con Python
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
├── config.py        # Configuración centralizada
├── main.py          # Aplicación principal FastAPI
├── run.py           # Script para ejecutar el backend desde cualquier ubicación
├── test_server.py   # Servidor simple para pruebas
├── .env             # Variables de entorno (excluido de git)
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

3. Configura las variables de entorno:
   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales
   ```

## Ejecución

Para ejecutar el servidor, **asegúrate de estar en el directorio raíz del proyecto** y ejecuta:

```bash
python backend/run.py
```

O, alternativamente, puedes entrar al directorio `backend` y ejecutar:

```bash
cd backend
python run.py
```

Para probar que el servidor funciona correctamente, también puedes ejecutar:

```bash
cd backend
python test_server.py
```

El servidor estará disponible en la dirección y puerto configurados en `.env` (por defecto http://127.0.0.1:12345).

## API Docs

La documentación interactiva de la API estará disponible en:
- http://127.0.0.1:12345/docs (Swagger UI)
- http://127.0.0.1:12345/redoc (ReDoc)

## Solución de problemas

Si encuentras errores al iniciar el servidor:

1. **Problemas de puerto**: El puerto configurado puede estar en uso. Prueba cambiando el puerto en el archivo `.env` a otro número (como 12345, 54321, etc.)

2. **Problemas de base de datos**: Por defecto se usa SQLite para desarrollo. Si deseas usar PostgreSQL, descomenta la línea correspondiente en `.env`.

3. **Problemas de importación**: Asegúrate de estar ejecutando el servidor desde el directorio correcto. El script `run.py` está diseñado para manejar esto automáticamente.

4. **Problemas de dependencias**: Verifica que todas las dependencias estén instaladas correctamente con `pip list`.

## Pruebas

Para ejecutar las pruebas:

```bash
cd backend
pytest
```

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