# AI Labor Law Assistant

Este MVP está diseñado para ayudar a los usuarios a obtener respuestas rápidas, generadas por IA, a consultas sobre derecho laboral basadas en una base de datos controlada de casos anteriores y documentos legales. Integra NLP, búsqueda BM25, respuestas potenciadas por GPT y automatización a través de n8n para optimizar la toma de decisiones y agilizar la orientación legal.

## 🌟 Características

- 🏛 **Experiencia en Derecho Laboral**: Responde preguntas legales comunes sobre contratos, despidos, beneficios, seguridad social y más.
- 🔎 **Búsqueda basada en BM25**: Recupera precedentes legales relevantes de una base de datos seleccionada.
- 🤖 **Respuestas Impulsadas por IA**: Utiliza GPTs y automatización n8n para clasificar consultas y determinar si se requiere revisión profesional.
- 🔗 **Chatbot de WhatsApp y Web**: Los usuarios pueden acceder a asistencia legal a través de un chatbot de aplicación web o WhatsApp (integración Twilio).
- 📊 **Sistema Semiautomatizado**: Si no se encuentra una coincidencia exacta, se genera una respuesta básica y se guía a los usuarios hacia una consulta profesional si es necesario.

## 🛠 Stack Tecnológico

- **Backend**: FastAPI (Python)
- **Base de datos**: PostgreSQL (conjunto de datos controlado de casos legales)
- **Motor de búsqueda**: BM25 + Coincidencia Semántica GPT
- **Automatización**: n8n (orquestación de flujo de trabajo y toma de decisiones)
- **Frontend**: Next.js (Página de inicio + Chatbot)
- **Mensajería**: API de Twilio para integración de WhatsApp
- **Despliegue**: Vercel (Frontend), Render (Backend)

## 📋 Requisitos

- Python 3.9+
- Node.js 18+ (para el frontend y n8n)
- PostgreSQL o SQLite
- Cuenta de OpenAI con API key
- Cuenta de Twilio (opcional, para integración con WhatsApp)

## 🚀 Configuración y Ejecución

### Configuración de OpenAI

Para utilizar las funcionalidades de IA del asistente, necesitas configurar una API key de OpenAI:

1. Regístrate en [OpenAI Platform](https://platform.openai.com) si aún no tienes una cuenta
2. Crea una nueva API key en [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
3. Copia la API key generada (comienza con `sk-`)
4. Pégala en el archivo `.env` del backend:
   ```
   OPENAI_API_KEY=sk-tu-api-key-aquí
   ```

Para verificar que OpenAI está configurado correctamente:
```bash
cd backend
python test_openai_config.py
```

### Backend

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/ai-labor-law-assistant.git
cd ai-labor-law-assistant

# Configurar el entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
cd backend
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Iniciar el servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 12345
```

### Frontend

```bash
# Desde la raíz del proyecto
cd frontend

# Instalar dependencias
npm install

# Iniciar el servidor de desarrollo
npm run dev
```

## 📚 Documentación

La documentación completa está disponible en:

- Backend API: http://localhost:12345/docs
- Guía de Usuario: [docs/user_guide.md](docs/user_guide.md)
- Guía de Desarrollo: [docs/developer_guide.md](docs/developer_guide.md)

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor, lee [CONTRIBUTING.md](CONTRIBUTING.md) para obtener detalles sobre nuestro código de conducta y el proceso para enviarnos pull requests.

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

# LegalAssista - Entorno de Prueba

Este documento describe cómo configurar y ejecutar el entorno de prueba de LegalAssista.

## Requisitos Previos

- Python 3.8+
- PostgreSQL
- Redis
- Node.js 14+
- npm o yarn

## Configuración del Backend

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd legalassista
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
cd backend/app
pip install -r requirements.txt
```

4. Configurar variables de entorno:
- Copiar el archivo `.env.example` a `.env`
- Completar las variables con tus credenciales

5. Ejecutar el servidor:
```bash
chmod +x scripts/run_dev.sh
./scripts/run_dev.sh
```

## Credenciales de Prueba

### Usuario Admin
- Email: admin@legalassista.com
- Contraseña: Admin123!

### Usuario Abogado
- Email: abogado@legalassista.com
- Contraseña: Abogado123!

### Usuario Cliente
- Email: cliente@legalassista.com
- Contraseña: Cliente123!

## Endpoints Principales

### Autenticación
- POST /api/v1/auth/register - Registro de usuario
- POST /api/v1/auth/login - Inicio de sesión
- POST /api/v1/auth/recover-password - Recuperación de contraseña

### Casos
- GET /api/v1/casos - Listar casos
- POST /api/v1/casos - Crear caso
- GET /api/v1/casos/{id} - Obtener caso
- PUT /api/v1/casos/{id} - Actualizar caso

### Chat
- GET /api/v1/chat/{caso_id} - Obtener mensajes
- POST /api/v1/chat/{caso_id} - Enviar mensaje
- WebSocket: ws://localhost:8000/ws/chat/{caso_id}

### Notificaciones
- GET /api/v1/notificaciones - Listar notificaciones
- POST /api/v1/notificaciones/{id}/leer - Marcar como leída

### Pagos
- POST /api/v1/pagos/crear-sesion - Crear sesión de pago
- POST /api/v1/pagos/webhook - Webhook de Stripe

## Flujos de Prueba

### Flujo de Cliente
1. Registro/Login como cliente
2. Onboarding conversacional
3. Crear caso
4. Subir documentos
5. Realizar pago
6. Chat con abogado
7. Recibir notificaciones

### Flujo de Abogado
1. Login como abogado
2. Ver casos asignados
3. Responder mensajes
4. Actualizar estado de casos
5. Generar facturas

### Flujo de Admin
1. Login como admin
2. Gestionar usuarios
3. Ver analytics
4. Configurar sistema

## Notas Importantes

- El entorno de prueba usa una base de datos PostgreSQL local
- Los pagos se procesan en modo sandbox de Stripe
- Las notificaciones por email se envían a una bandeja de prueba
- El chat en tiempo real requiere Redis
- Los webhooks de Stripe se pueden probar usando el CLI de Stripe

## Solución de Problemas

1. Si la base de datos no se inicializa:
```bash
alembic upgrade head
python scripts/init_test_data.py
```

2. Si los webhooks no funcionan:
```bash
stripe listen --forward-to localhost:8000/api/v1/pagos/webhook
```

3. Si el chat no funciona:
- Verificar que Redis esté corriendo
- Revisar la conexión WebSocket

## Contacto

Para soporte técnico o preguntas:
- Email: soporte@legalassista.com
- Slack: #soporte-legalassista

## Inicio Rápido

Para iniciar todo el entorno de prueba con un solo comando:

```bash
# Dar permisos de ejecución a los scripts
chmod +x scripts/start_all.sh
chmod +x backend/app/scripts/run_dev.sh
chmod +x backend/app/scripts/run_websocket.sh
chmod +x frontend/scripts/run_dev.sh

# Iniciar todos los servicios
./scripts/start_all.sh
```

### Verificación de Servicios

1. Backend API: http://localhost:8000/docs
2. Frontend: http://localhost:3000
3. WebSocket: ws://localhost:8000/ws
4. Stripe Webhook: Escuchando en localhost:8000/api/v1/pagos/webhook

### Prueba de Flujos

1. **Flujo de Cliente**:
   - Acceder a http://localhost:3000
   - Registrarse como cliente
   - Completar el onboarding
   - Crear un caso
   - Subir documentos
   - Realizar pago de prueba
   - Iniciar chat con abogado

2. **Flujo de Abogado**:
   - Acceder a http://localhost:3000
   - Iniciar sesión como abogado
   - Ver casos asignados
   - Responder mensajes
   - Actualizar estado de casos

3. **Flujo de Admin**:
   - Acceder a http://localhost:3000
   - Iniciar sesión como admin
   - Gestionar usuarios
   - Ver analytics
   - Configurar sistema


