#!/bin/bash

# Script para ejecutar pruebas E2E de LegalAssista
# ===============================================

set -e

echo "🚀 Iniciando pruebas E2E para LegalAssista"
echo "=========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar que Node.js esté instalado
if ! command -v node &> /dev/null; then
    error "Node.js no está instalado. Por favor instala Node.js 16 o superior."
    exit 1
fi

# Verificar versión de Node.js
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    error "Se requiere Node.js 16 o superior. Versión actual: $(node --version)"
    exit 1
fi

log "Node.js versión: $(node --version)"

# Configurar variables de entorno
export NODE_ENV=test
export BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
export FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}

log "Backend URL: $BACKEND_URL"
log "Frontend URL: $FRONTEND_URL"

# Cambiar al directorio de pruebas
cd "$(dirname "$0")"

# Instalar dependencias si no existen
if [ ! -d "node_modules" ]; then
    log "Instalando dependencias..."
    npm install
    success "Dependencias instaladas"
else
    log "Dependencias ya instaladas"
fi

# Verificar conectividad con el backend
log "Verificando conectividad con el backend..."
if curl -s --max-time 10 "$BACKEND_URL/health" > /dev/null 2>&1; then
    success "Backend disponible en $BACKEND_URL"
else
    warning "Backend no disponible en $BACKEND_URL"
    warning "Las pruebas continuarán pero pueden fallar"
fi

# Crear directorio de reportes si no existe
mkdir -p reports

# Función para ejecutar pruebas específicas
run_test_suite() {
    local test_name=$1
    local test_file=$2
    
    log "Ejecutando pruebas: $test_name"
    
    if npm run test -- "$test_file" --json --outputFile="reports/${test_name}-results.json"; then
        success "Pruebas $test_name completadas exitosamente"
        return 0
    else
        error "Pruebas $test_name fallaron"
        return 1
    fi
}

# Ejecutar pruebas según argumentos
case "${1:-all}" in
    "abogado")
        log "Ejecutando solo pruebas de abogado..."
        run_test_suite "abogado" "e2e/abogado.test.js"
        ;;
    "all")
        log "Ejecutando todas las pruebas E2E..."
        
        # Ejecutar pruebas de abogado
        run_test_suite "abogado" "e2e/abogado.test.js"
        
        # Aquí se pueden agregar más suites de pruebas
        # run_test_suite "admin" "e2e/admin.test.js"
        # run_test_suite "cliente" "e2e/cliente.test.js"
        ;;
    "coverage")
        log "Ejecutando pruebas con cobertura..."
        npm run test:coverage
        ;;
    "ci")
        log "Ejecutando pruebas en modo CI..."
        npm run test:ci
        ;;
    *)
        echo "Uso: $0 [abogado|all|coverage|ci]"
        echo ""
        echo "Opciones:"
        echo "  abogado   - Ejecutar solo pruebas de abogado"
        echo "  all       - Ejecutar todas las pruebas (por defecto)"
        echo "  coverage  - Ejecutar con reporte de cobertura"
        echo "  ci        - Ejecutar en modo CI"
        exit 1
        ;;
esac

# Generar reporte final
log "Generando reporte final..."

# Crear reporte HTML simple
cat > reports/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Reporte de Pruebas E2E - LegalAssista</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .success { color: green; }
        .error { color: red; }
        .warning { color: orange; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Reporte de Pruebas E2E - LegalAssista</h1>
        <p class="timestamp">Generado: $(date)</p>
        <p>Backend URL: $BACKEND_URL</p>
        <p>Frontend URL: $FRONTEND_URL</p>
    </div>
    
    <h2>Resultados de Pruebas</h2>
    <p>Los resultados detallados están disponibles en los archivos JSON de este directorio.</p>
    
    <h3>Archivos de Resultados:</h3>
    <ul>
EOF

# Listar archivos de resultados
for file in reports/*-results.json; do
    if [ -f "$file" ]; then
        echo "        <li><a href=\"$(basename "$file")\">$(basename "$file")</a></li>" >> reports/index.html
    fi
done

cat >> reports/index.html << EOF
    </ul>
    
    <h3>Instrucciones para Revisar Fallos</h3>
    <ol>
        <li>Revisa los archivos JSON para detalles específicos de cada prueba</li>
        <li>Verifica que el backend esté ejecutándose en $BACKEND_URL</li>
        <li>Asegúrate de que las credenciales de prueba sean correctas</li>
        <li>Revisa los logs de la aplicación para errores específicos</li>
    </ol>
</body>
</html>
EOF

success "Reporte generado en reports/index.html"

# Mostrar resumen
log "Resumen de ejecución:"
echo "- Reportes disponibles en: $(pwd)/reports/"
echo "- Para ver resultados detallados: open reports/index.html"

success "Pruebas E2E completadas" 