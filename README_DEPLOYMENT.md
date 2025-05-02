# Despliegue de LegalAssista en Render

Este documento detalla el proceso de despliegue de LegalAssista, una aplicación fullstack con FastAPI (backend), React/Vite (frontend) y WebSockets para comunicación en tiempo real.

## URLs de la aplicación

- **Frontend**: https://legalassista.onrender.com
- **Backend API**: https://legalassista-api.onrender.com
- **API Docs**: https://legalassista-api.onrender.com/docs
- **WebSocket**: wss://legalassista-api.onrender.com/ws

## Usuarios demo

Para probar la aplicación, puedes usar las siguientes credenciales:

- **Administrador**:
  - Email: admin@legalassista.com
  - Contraseña: Admin123!

- **Abogado**:
  - Email: abogado@legalassista.com
  - Contraseña: Abogado123!

- **Cliente**:
  - Email: cliente@legalassista.com
  - Contraseña: Cliente123!

## Configuración del despliegue en Render

El despliegue en Render se realiza automáticamente utilizando el archivo `render.yaml` en la raíz del proyecto.

### Servicios configurados

- **API Backend** (legalassista-api): Servicio web Docker con FastAPI y WebSockets
- **Frontend** (legalassista): Servicio web Docker con React/Vite
- **Base de datos** (legalassista-db): PostgreSQL gestionado
- **Redis** (legalassista-redis): Redis gestionado para WebSockets y caché

### Variables de entorno requeridas

El archivo `render.yaml` configura automáticamente la mayoría de las variables, pero deberás configurar manualmente las siguientes en el panel de Render:

- **OPENAI_API_KEY**: Tu clave de API de OpenAI
- **MERCADOPAGO_PUBLIC_KEY**: Clave pública de MercadoPago
- **MERCADOPAGO_ACCESS_TOKEN**: Token de acceso de MercadoPago

## Instrucciones para despliegue manual

Si necesitas desplegar manualmente (sin usar render.yaml), sigue estos pasos:

### 1. Despliegue del backend

1. Crea un nuevo servicio web en Render
2. Conecta con tu repositorio de GitHub
3. Selecciona la carpeta `/backend`
4. Configura como Docker
5. Configura las variables de entorno:
   - `DATABASE_URL`: URL de conexión a PostgreSQL
   - `REDIS_URL`: URL de conexión a Redis
   - `SECRET_KEY`: Clave secreta para JWT (generada automáticamente)
   - `OPENAI_API_KEY`: Tu clave de API de OpenAI
   - `MERCADOPAGO_PUBLIC_KEY`: Clave pública de MercadoPago
   - `MERCADOPAGO_ACCESS_TOKEN`: Token de acceso de MercadoPago
   - `FRONTEND_URL`: URL del frontend desplegado
   - `PORT`: 8000

### 2. Despliegue del frontend

1. Crea un nuevo servicio web en Render
2. Conecta con tu repositorio de GitHub
3. Selecciona la carpeta `/frontend`
4. Configura como Docker
5. Configura las variables de entorno:
   - `VITE_BACKEND_URL`: URL del backend desplegado
   - `VITE_WEBSOCKET_URL`: URL del WebSocket (ws:// o wss://)

### 3. Configuración de base de datos PostgreSQL

1. Crea un nuevo servicio de PostgreSQL en Render
2. Anota las credenciales de conexión
3. Configura la variable `DATABASE_URL` en el servicio backend

### 4. Configuración de Redis

1. Crea un nuevo servicio de Redis en Render
2. Anota la URL de conexión
3. Configura la variable `REDIS_URL` en el servicio backend

## Verificación post-despliegue

Una vez completado el despliegue, verifica:

1. Accede al frontend en https://legalassista.onrender.com
2. Verifica que puedas iniciar sesión con los usuarios demo
3. Accede a la documentación API en https://legalassista-api.onrender.com/docs
4. Asegúrate de que las notificaciones en tiempo real funcionan (usa el WebSocket)
5. Prueba un flujo de pago con MercadoPago (en modo sandbox)

## Ejecución local

Para ejecutar la aplicación localmente:

### Backend

```bash
cd backend
pip install -r requirements.txt
cd app
python -m uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Websocket (se ejecuta separado del backend)

```bash
cd backend/app
python -m scripts.run_websocket.py
```

## Solución de problemas comunes

### Problemas de conexión al WebSocket

Verifica que:
- El servicio Render para el backend tiene habilitado los WebSockets
- La URL del WebSocket usa `wss://` (WebSocket seguro)
- Las políticas CORS están correctamente configuradas en el backend

### Errores de base de datos

- Verifica que la migración se ejecutó correctamente
- Comprueba los logs del servicio backend en Render

### Problemas con MercadoPago

- Confirma que las credenciales de MercadoPago son correctas
- Verifica que estás usando las credenciales de sandbox para pruebas
- Asegúrate de que la URL del webhook está correctamente configurada en MercadoPago 