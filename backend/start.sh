#!/bin/bash
set -e

echo "Verificando variables de entorno..."

# Función para verificar y reportar variables de entorno
check_env_var() {
    if [ -z "${!1}" ]; then
        echo "⚠️  Variable $1 no está configurada"
        return 1
    else
        echo "✅ Variable $1 está configurada"
        return 0
    fi
}

# Verificar variables críticas
echo "🔍 Verificando configuración..."
check_env_var "DATABASE_URL" || echo "Base de datos no configurada"
check_env_var "SECRET_KEY" || echo "Clave secreta no configurada"

echo "🚀 Iniciando LegalAssista API en puerto ${PORT:-10000}"

# Paso 1: Crear tablas básicas
echo "🏗️ Creando tablas de base de datos..."
python scripts/create_db_tables.py || echo "⚠️ Error creando tablas básicas"

# Paso 2: Ejecutar corrección completa de base de datos
echo "🔧 Ejecutando corrección completa de base de datos..."
python scripts/fix_production_db.py || echo "⚠️ Error en corrección avanzada de DB"

# Ejecutar comando pasado como argumento (generalmente seed + uvicorn)
if [ $# -eq 0 ]; then
    # Si no se pasan argumentos, ejecutar configuración por defecto
    echo "📋 Inicializando datos de prueba..."
    python scripts/seed.py || echo "⚠️ Advertencia: Error en seed de datos"
    
    echo "🌐 Iniciando servidor web..."
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
else
    # Ejecutar los comandos pasados como argumentos
    exec "$@"
fi 