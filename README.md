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


