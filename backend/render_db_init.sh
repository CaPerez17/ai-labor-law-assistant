#!/bin/bash

# Script para inicializar usuarios en la base de datos de Render.com
# Uso: ./render_db_init.sh [postgres_connection_string]

echo "=== Inicialización de Base de Datos en Render.com ==="
echo "Este script conectará a la base de datos en Render e inicializará usuarios."

# Si hay un parámetro, usarlo como cadena de conexión
if [ -n "$1" ]; then
    CONNECTION_STRING="$1"
    echo "Usando conexión PostgreSQL proporcionada como parámetro"
else
    # Si no hay parámetro, solicitar la cadena de conexión
    echo "Por favor, ingresa la cadena de conexión PostgreSQL de Render.com."
    echo "Ejemplo: postgresql://user:password@host:port/database"
    echo "(La contraseña no se mostrará)"
    echo -n "Conexión PostgreSQL: "
    read -s CONNECTION_STRING
    echo # Salto de línea después de input secreto
fi

# Verificar que la cadena de conexión no esté vacía
if [ -z "$CONNECTION_STRING" ]; then
    echo "❌ Error: Cadena de conexión vacía"
    exit 1
fi

# Verificar que la cadena de conexión comience con postgresql://
if [[ ! "$CONNECTION_STRING" == postgresql://* ]]; then
    echo "❌ Error: La cadena de conexión debe comenzar con postgresql://"
    exit 1
fi

echo "Ejecutando script de inicialización..."
python direct_seed.py --postgres "$CONNECTION_STRING"

# Verificar el resultado
if [ $? -ne 0 ]; then
    echo "❌ Falló la ejecución del script"
    exit 1
else
    echo "✅ Script ejecutado correctamente"
fi 