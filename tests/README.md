# Pruebas End-to-End (E2E) - LegalAssista

Este directorio contiene las pruebas end-to-end para verificar las funcionalidades completas del sistema LegalAssista, especialmente para el usuario con rol "abogado".

## 📋 Índice

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Ejecución de Pruebas](#ejecución-de-pruebas)
- [Estructura de Pruebas](#estructura-de-pruebas)
- [Casos de Prueba](#casos-de-prueba)
- [Reportes](#reportes)
- [Solución de Problemas](#solución-de-problemas)

## 🔧 Requisitos

- **Node.js**: Versión 16 o superior
- **npm**: Incluido con Node.js
- **Backend**: LegalAssista backend ejecutándose (por defecto en `http://localhost:8000`)
- **Frontend**: LegalAssista frontend ejecutándose (por defecto en `http://localhost:3000`)

## 📦 Instalación

1. **Navegar al directorio de pruebas:**
   ```bash
   cd tests
   ```

2. **Instalar dependencias:**
   ```bash
   npm install
   ```

3. **Hacer ejecutable el script de pruebas:**
   ```bash
   chmod +x run-tests.sh
   ```

## 🚀 Ejecución de Pruebas

### Opción 1: Script Automatizado (Recomendado)

```bash
# Ejecutar todas las pruebas
./run-tests.sh

# Ejecutar solo pruebas de abogado
./run-tests.sh abogado

# Ejecutar con cobertura
./run-tests.sh coverage

# Ejecutar en modo CI
./run-tests.sh ci
```

### Opción 2: Comandos npm directos

```bash
# Todas las pruebas
npm test

# Solo pruebas de abogado
npm run test:abogado

# Con cobertura
npm run test:coverage

# Modo watch (desarrollo)
npm run test:watch
```

### Opción 3: Variables de entorno personalizadas

```bash
# Configurar URLs personalizadas
export BACKEND_URL=https://legalassista.onrender.com
export FRONTEND_URL=https://legalassista-frontend.onrender.com
./run-tests.sh abogado
```

## 📁 Estructura de Pruebas

```
tests/
├── e2e/
│   ├── abogado.test.js          # Pruebas para usuario abogado
│   ├── admin.test.js            # (Futuro) Pruebas para admin
│   └── cliente.test.js          # (Futuro) Pruebas para cliente
├── reports/                     # Reportes generados
│   ├── index.html              # Reporte principal
│   └── *-results.json          # Resultados detallados
├── setup.js                    # Configuración inicial
├── package.json                # Dependencias y scripts
├── run-tests.sh               # Script principal de ejecución
└── README.md                  # Esta documentación
```

## 🧪 Casos de Prueba - Usuario Abogado

### 1. Login y Autenticación
- ✅ Login exitoso con credenciales válidas
- ✅ Verificación de almacenamiento en localStorage
- ✅ Redirección correcta al dashboard de abogado

### 2. Gestión de Casos
- ✅ Obtener lista de casos asignados
- ✅ Filtrar casos por estado (pendiente, en_proceso, resuelto)
- ✅ Filtrar casos por nivel de riesgo (bajo, medio, alto)
- ✅ Obtener detalle de caso específico
- ✅ Actualizar estado y comentarios de caso

### 3. Chat con Cliente
- ✅ Enviar mensaje en chat
- ✅ Obtener historial de conversación
- ✅ Verificar estructura de mensajes

### 4. Gestión de Documentos
- ✅ Subir documento al sistema
- ✅ Listar documentos asociados a un caso
- ✅ Descargar documento con headers correctos

### 5. Consultas Legales (IA)
- ✅ Realizar consulta a sistema de IA
- ✅ Verificar respuesta válida
- ✅ Obtener historial de consultas

### 6. Protección de Rutas
- ✅ Acceso denegado sin token de autenticación
- ✅ Acceso denegado a rutas de admin
- ✅ Verificación de roles y permisos

### 7. Logout
- ✅ Cerrar sesión correctamente
- ✅ Invalidación de token
- ✅ Limpieza de datos de sesión

## 📊 Reportes

Después de ejecutar las pruebas, se generan varios tipos de reportes:

### Reporte HTML
- **Ubicación**: `reports/index.html`
- **Contenido**: Resumen visual de resultados
- **Acceso**: Abrir en navegador web

### Reportes JSON
- **Ubicación**: `reports/*-results.json`
- **Contenido**: Resultados detallados por suite
- **Formato**: JSON estructurado para análisis programático

### Ejemplo de estructura de reporte:
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "total_tests": 20,
  "passed": 18,
  "failed": 2,
  "skipped": 0,
  "results": [...]
}
```

## 🔍 Endpoints Verificados

### Autenticación
- `POST /api/v1/auth/login` - Login de usuario
- `POST /api/v1/auth/register` - Registro de usuario

### Abogado
- `GET /api/v1/abogado/casos` - Lista de casos
- `GET /api/v1/abogado/casos/{id}` - Detalle de caso
- `POST /api/v1/abogado/actualizar` - Actualizar caso

### Chat
- `POST /api/v1/chat` - Enviar mensaje
- `GET /api/v1/chat?caseId={id}` - Historial de chat

### Documentos
- `POST /api/v1/docs/upload` - Subir documento
- `GET /api/v1/docs?caseId={id}` - Listar documentos
- `GET /api/v1/docs/download/{id}` - Descargar documento

### IA
- `POST /api/v1/ask` - Consulta a IA
- `GET /api/v1/ask/historial` - Historial de consultas

### Admin (Verificación de permisos)
- `GET /api/v1/admin/analytics` - Analytics (debe fallar para abogado)

## 🛠️ Solución de Problemas

### Error: "Backend no disponible"
```bash
# Verificar que el backend esté ejecutándose
curl http://localhost:8000/health

# Si usa URL diferente, configurar variable
export BACKEND_URL=https://tu-backend.com
```

### Error: "Usuario de prueba no existe"
```bash
# El script automáticamente crea el usuario, pero si falla:
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Abogado Test",
    "email": "abogado@legalassista.com", 
    "password": "Abogado123!",
    "rol": "abogado"
  }'
```

### Error: "Timeout en pruebas"
```bash
# Aumentar timeout en package.json
"jest": {
  "testTimeout": 60000
}
```

### Error: "Módulo no encontrado"
```bash
# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

### Depuración de pruebas específicas
```bash
# Ejecutar una prueba específica con logs detallados
npm test -- --testNamePattern="Login exitoso" --verbose
```

## 📝 Credenciales de Prueba

Las pruebas utilizan las siguientes credenciales por defecto:

```javascript
{
  email: 'abogado@legalassista.com',
  password: 'Abogado123!',
  rol: 'abogado'
}
```

## 🔄 Integración Continua

Para usar en CI/CD, ejecutar:

```bash
# Modo CI (sin watch, con coverage)
npm run test:ci

# O usando el script
./run-tests.sh ci
```

## 📈 Métricas de Éxito

- **Cobertura mínima**: 80%
- **Tiempo máximo por prueba**: 30 segundos
- **Tasa de éxito esperada**: 95%

## 🤝 Contribuir

Para agregar nuevas pruebas:

1. Crear archivo en `e2e/` siguiendo el patrón `{rol}.test.js`
2. Seguir la estructura de `abogado.test.js`
3. Agregar configuración en `run-tests.sh`
4. Actualizar esta documentación

## 📞 Soporte

Si encuentras problemas con las pruebas:

1. Revisar logs detallados en `reports/`
2. Verificar que backend y frontend estén ejecutándose
3. Comprobar credenciales y permisos
4. Consultar la sección de solución de problemas

---

**Última actualización**: Enero 2024  
**Versión**: 1.0.0 