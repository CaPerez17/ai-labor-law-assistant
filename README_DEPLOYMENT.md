# Despliegue de LegalAssista en Render

Este documento detalla el proceso de despliegue de LegalAssista, una aplicación fullstack con FastAPI (backend), React/Vite (frontend) y WebSockets para comunicación en tiempo real.

## URLs de la aplicación

- **Frontend**: https://legalassista-frontend.onrender.com
- **Backend API**: https://legalassista.onrender.com
- **API Docs**: https://legalassista.onrender.com/docs
- **WebSocket**: wss://legalassista.onrender.com/ws

## Usuarios demo

Para probar la aplicación, puedes usar las siguientes credenciales:

- **Administrador**:
  - Email: admin@legalassista.com
  - Contraseña: admin123

- **Abogado**:
  - Email: abogado@legalassista.com
  - Contraseña: abogado123

- **Cliente**:
  - Email: cliente@legalassista.com
  - Contraseña: cliente123

## Configuración del despliegue en Render

El despliegue en Render se realiza automáticamente utilizando el archivo `render.yaml` en la raíz del proyecto.

### Servicios configurados

- **API Backend** (legalassista): Servicio web Python con FastAPI y WebSockets
- **Frontend** (legalassista-frontend): Servicio web estático con React/Vite
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
4. Configura como Python
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
4. Configura como Static Site
5. Configura las variables de entorno:
   - `VITE_BACKEND_URL`: URL del backend desplegado (https://legalassista.onrender.com)
   - `VITE_WEBSOCKET_URL`: URL del WebSocket (wss://legalassista.onrender.com/ws)

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

1. Accede al frontend en https://legalassista-frontend.onrender.com
2. Verifica que puedas iniciar sesión con los usuarios demo
3. Accede a la documentación API en https://legalassista.onrender.com/docs
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

### Problemas de login

Si experimentas problemas al iniciar sesión:

1. Asegúrate de que la URL del backend está correctamente configurada en el frontend:
   - Debe ser `https://legalassista.onrender.com` (¡no `legalassista-api.onrender.com`!)
   - Verifica la variable de entorno `VITE_BACKEND_URL` en el servicio frontend de Render

2. Revisa los logs del backend para ver si las solicitudes de login están llegando correctamente

3. Utiliza la herramienta de depuración en el formulario de login (haz clic en "Mostrar información técnica") 