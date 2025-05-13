#!/bin/bash

# Script para conectarse a PostgreSQL de Render (versión segura)
echo "Verificando instalación de psql..."
if ! command -v psql &> /dev/null; then
    echo "psql no está instalado. Instalalo con:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "  macOS: brew install postgresql"
    exit 1
fi

# Configuración de la base de datos
DB_HOST="dpg-d0alb1ruibrs73a9udv0-a.oregon-postgres.render.com"
DB_NAME="legalassista_db"
DB_USER="legalassista_db_user"

# Solicitar contraseña de forma segura
echo "Introduce la contraseña para la base de datos (no se mostrará en pantalla):"
read -s DB_PASSWORD
echo ""

if [ -z "$DB_PASSWORD" ]; then
    echo "La contraseña no puede estar vacía."
    exit 1
fi

echo "Conectando a la base de datos PostgreSQL en Render..."
echo "Usar los siguientes comandos una vez conectado:"
echo "  \\dt                       → listar tablas"
echo "  \\d <table_name>           → describir tabla"
echo "  SELECT * FROM usuarios LIMIT 10;  → ver primeros 10 usuarios"
echo "  \\q                        → salir"
echo ""

# Conectar a la base de datos sin mostrar la contraseña
export PGPASSWORD="$DB_PASSWORD"
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME"
unset PGPASSWORD  # Limpiar la variable por seguridad 