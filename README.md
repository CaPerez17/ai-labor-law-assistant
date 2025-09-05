# 🏛️ LegalAssista - AI Legal Assistant

**LegalAssista** es un asistente legal inteligente especializado en derecho laboral colombiano que combina análisis automatizado con IA, gestión de casos CRM, y escalamiento a abogados humanos.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)
![React](https://img.shields.io/badge/React-18+-cyan.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## 🚀 Características Principales

### ⚖️ **Análisis Legal Automatizado**
- Consultas legales procesadas con GPT-3.5/GPT-4
- Sistema BM25 para búsqueda en documentos legales
- Evaluación de confianza automática
- Escalamiento inteligente a abogados

### 📋 **Herramientas Especializadas**
- **Contrato Realidad**: Evaluación de relaciones laborales
- **Cálculo de Indemnización**: Liquidaciones precisas por despido
- **Análisis de Contratos**: Revisión automatizada de documentos
- **Generación de Contratos**: Plantillas legales personalizadas

### 👥 **Gestión Integral**
- **CRM para Abogados**: Gestión completa de casos
- **Chat en Tiempo Real**: Comunicación abogado-cliente
- **Dashboard Administrativo**: Métricas y analytics
- **Sistema de Facturación**: Integración con MercadoPago

### 🔄 **Onboarding Inteligente**
- Clasificación automática de consultas
- Flujos guiados por tipo de caso
- Recomendaciones personalizadas

## 🏗️ Arquitectura Técnica

### **Stack Tecnológico**
```
Frontend:  React 18 + Vite + Tailwind CSS
Backend:   FastAPI + Python 3.10+ + SQLAlchemy
Database:  PostgreSQL + pgvector
Cache:     SQLite (BM25) + Redis (futuro)
AI:        OpenAI GPT-3.5/GPT-4
Payments:  MercadoPago API
Deploy:    Docker + Nginx + DigitalOcean
```

### **Patrón Arquitectónico**
- **Monolito Modular** con 29 endpoints especializados
- **15 Servicios de Negocio** independientes
- **Separación clara** de responsabilidades
- **Preparado para microservicios** sin refactoring mayor

## 📦 Instalación y Configuración

### **Prerrequisitos**
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Git

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/CaPerez17/ai-labor-law-assistant.git
cd ai-labor-law-assistant
```

### **2. Configurar Backend**
```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

### **3. Configurar Base de Datos**
```bash
# Crear base de datos PostgreSQL
createdb legalassista

# Ejecutar migraciones
alembic upgrade head

# Opcional: Cargar datos de prueba
python -m app.db.seed
```

### **4. Configurar Frontend**
```bash
cd ../frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con la URL del backend
```

### **5. Ejecutar en Desarrollo**
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Acceder a:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs

## 🔧 Variables de Entorno

### **Backend (.env)**
```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost/legalassista

# Autenticación
SECRET_KEY=tu_clave_secreta_jwt
ALGORITHM=HS256

# OpenAI
OPENAI_API_KEY=sk-...
GPT_MODEL=gpt-3.5-turbo

# Email (opcional)
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_app_password
MAIL_FROM=noreply@legalassista.com
MAIL_SERVER=smtp.gmail.com

# MercadoPago (opcional)
MERCADOPAGO_PUBLIC_KEY=TEST-...
MERCADOPAGO_ACCESS_TOKEN=TEST-...

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=false
FRONTEND_URL=http://localhost:5173
```

### **Frontend (.env.local)**
```env
VITE_BACKEND_URL=http://localhost:8000
VITE_WEBSOCKET_URL=ws://localhost:8000/ws
VITE_APP_VERSION=1.0.0
```

## 🐳 Despliegue con Docker

### **Desarrollo**
```bash
# Construir y ejecutar
docker-compose up --build

# Solo backend
docker-compose up backend

# Solo frontend
docker-compose up frontend
```

### **Producción**
```bash
# Configurar variables de entorno de producción
cp .env.example .env.production

# Desplegar
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 Estructura del Proyecto

```
ai-labor-law-assistant/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # 29 Endpoints especializados
│   │   ├── core/           # Configuración y seguridad
│   │   ├── db/             # Base de datos y modelos
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Validación Pydantic
│   │   ├── services/       # 15 Servicios de negocio
│   │   └── templates/      # Templates de email
│   ├── alembic/            # Migraciones de DB
│   ├── main.py             # Punto de entrada
│   └── requirements.txt    # Dependencias Python
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── api/           # Cliente HTTP
│   │   ├── components/    # Componentes React
│   │   ├── layouts/       # Layouts de página
│   │   └── pages/         # Páginas principales
│   ├── package.json       # Dependencias Node.js
│   └── vite.config.js     # Configuración Vite
├── docs/                  # Documentación
├── README.md              # Este archivo
└── render.yaml            # Configuración Render.com
```

## 🧪 Testing

### **Backend**
```bash
cd backend

# Ejecutar tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest app/tests/test_auth.py -v
```

### **Frontend**
```bash
cd frontend

# Tests unitarios
npm run test

# Tests E2E
npm run test:e2e

# Coverage
npm run test:coverage
```

## 📊 Funcionalidades por Módulo

| Módulo | Estado | Descripción |
|--------|--------|-------------|
| **Análisis Legal** | ✅ Completo | GPT + BM25 + Confidence scoring |
| **Contrato Realidad** | ✅ Completo | Evaluación multi-factor de relaciones laborales |
| **Indemnización** | ✅ Completo | Cálculos precisos por tipo de contrato |
| **Análisis Documentos** | ✅ Completo | PDF/DOCX + detección de riesgos |
| **CRM Abogados** | ✅ Completo | Gestión de casos + métricas |
| **Chat Tiempo Real** | ✅ Completo | WebSocket abogado-cliente |
| **Facturación** | ✅ Completo | MercadoPago + webhooks |
| **Notificaciones** | ✅ Completo | Email + in-app |
| **Admin Dashboard** | ✅ Completo | Analytics + gestión usuarios |
| **Escalamiento WhatsApp** | ⚠️ Preparado | Código listo, API no conectada |

## 🔒 Seguridad

- **Autenticación JWT** con refresh tokens
- **Hashing de contraseñas** con bcrypt
- **Validación de entrada** con Pydantic
- **Protección CORS** configurada
- **Rate limiting** (recomendado para producción)
- **HTTPS** en producción con Let's Encrypt

## 🚀 Roadmap

### **Próximas Funcionalidades**
- [ ] **Casos de Tránsito**: Fotomultas y comparendos
- [ ] **Reformulación de Preguntas**: IA para consultas ambiguas
- [ ] **Sistema Híbrido Real**: Conexión WhatsApp Business
- [ ] **ML Avanzado**: Clasificación inteligente de casos

### **Mejoras Técnicas**
- [ ] **Redis Cache**: Cache distribuido
- [ ] **Message Queues**: Procesamiento asíncrono
- [ ] **Observabilidad**: Prometheus + Grafana
- [ ] **Microservicios**: Extracción gradual de servicios

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Camilo Pérez**
- GitHub: [@CaPerez17](https://github.com/CaPerez17)
- Email: devcamper97@gmail.com

## 🙏 Agradecimientos

- OpenAI por la API GPT
- FastAPI por el excelente framework
- React team por la librería frontend
- Comunidad open source por las herramientas utilizadas

---

⭐ **¡Dale una estrella si este proyecto te ha sido útil!**


