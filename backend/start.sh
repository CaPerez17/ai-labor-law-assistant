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

echo "🚀 Iniciando LegalAssista Backend..."

# Ejecutar scripts de inicialización de base de datos en orden
echo "🗄️ Configurando base de datos..."

# 1. Crear tablas básicas (compatible SQLite/PostgreSQL)
echo "📋 Paso 1: Creando tablas básicas..."
if python scripts/create_db_tables.py; then
    echo "✅ Tablas básicas creadas exitosamente"
else
    echo "⚠️ Error creando tablas básicas"
    # Si falla, intentar corrección agresiva para PostgreSQL
    echo "🚨 Intentando corrección agresiva para PostgreSQL..."
    if python scripts/fix_production_db.py; then
        echo "✅ Corrección agresiva completada"
    else
        echo "❌ Error en corrección agresiva"
        # Continuar de todas formas
    fi
fi

# 2. Corregir cualquier problema avanzado de PostgreSQL (solo si es necesario)
echo "🔧 Paso 2: Verificando estructura avanzada..."
if python scripts/fix_production_db.py; then
    echo "✅ Estructura verificada/corregida"
else
    echo "⚠️ Error en verificación avanzada (continuando...)"
fi

# 3. Crear usuarios y datos iniciales
echo "👥 Paso 3: Creando usuarios iniciales..."
if python scripts/seed.py; then
    echo "✅ Usuarios iniciales creados"
else
    echo "⚠️ Error creando usuarios iniciales (continuando...)"
fi

echo "🎯 Iniciando servidor FastAPI..."

# Iniciar el servidor FastAPI
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 